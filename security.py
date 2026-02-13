"""
Enhanced Security Module for EduFlow
Provides rate limiting, input sanitization, audit logging, and security middleware
"""
import hashlib
import time
import json
from functools import wraps
from typing import Dict, Optional, Any, List
from flask import request, jsonify, g
from collections import defaultdict, deque
import bleach
from markupsafe import escape
import datetime
import pyotp
import qrcode
from io import BytesIO
import base64

class RateLimiter:
    """Rate limiting implementation for API endpoints"""
    
    def __init__(self):
        self.requests = defaultdict(deque)  # Store request timestamps
        self.limits = {
            'auth': {'limit': 5, 'window': 300},  # 5 requests per 5 minutes
            'api': {'limit': 100, 'window': 60},  # 100 requests per minute
            'default': {'limit': 200, 'window': 300}  # 200 requests per 5 minutes
        }
    
    def is_allowed(self, key: str, limit_type: str = 'default') -> bool:
        """
        Check if request is allowed based on rate limits
        
        Args:
            key: Unique identifier for rate limiting (IP + endpoint)
            limit_type: Type of limit to apply (auth, api, default)
            
        Returns:
            True if request is allowed, False if rate limited
        """
        limit_config = self.limits.get(limit_type, self.limits['default'])
        limit = limit_config['limit']
        window = limit_config['window']
        
        now = time.time()
        # Clean old requests outside the time window
        while self.requests[key] and self.requests[key][0] < now - window:
            self.requests[key].popleft()
        
        # Check if we're under the limit
        if len(self.requests[key]) < limit:
            self.requests[key].append(now)
            return True
        return False
    
    def get_limits_for_client(self, key: str) -> Dict:
        """Get current limit status for a client"""
        now = time.time()
        
        rate_limits = {}
        for limit_type, config in self.limits.items():
            window = config['window']
            limit = config['limit']
            
            # Count requests in current window
            recent_requests = [t for t in self.requests.get(key, []) if t > now - window]
            remaining = max(0, limit - len(recent_requests))
            
            rate_limits[limit_type] = {
                'limit': limit,
                'remaining': remaining,
                'reset_time': now + (window - (now % window)) if recent_requests else now
            }
        
        return rate_limits

class InputSanitizer:
    """Input sanitization and validation utilities"""
    
    # Allowed HTML tags for rich text content
    ALLOWED_TAGS = [
        'p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li', 
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6'
    ]
    
    ALLOWED_ATTRIBUTES = {
        'a': ['href', 'title'],
        'img': ['src', 'alt', 'title']
    }
    
    @staticmethod
    def sanitize_string(value: str, allow_html: bool = False) -> str:
        """
        Sanitize string input
        
        Args:
            value: String to sanitize
            allow_html: Whether to allow limited HTML tags
            
        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            return str(value) if value is not None else ""
        
        # Remove null bytes and control characters
        value = ''.join(char for char in value if ord(char) >= 32 or char in '\n\r\t')
        
        if allow_html:
            # Allow limited HTML for rich text
            return bleach.clean(
                value, 
                tags=InputSanitizer.ALLOWED_TAGS,
                attributes=InputSanitizer.ALLOWED_ATTRIBUTES,
                strip=True
            )
        else:
            # Strip all HTML
            clean_value = bleach.clean(value, tags=[], attributes={}, strip=True)
            return escape(clean_value)
    
    @staticmethod
    def sanitize_dict(data: Dict, allow_html_fields: List[str] = None) -> Dict:
        """
        Recursively sanitize dictionary values
        
        Args:
            data: Dictionary to sanitize
            allow_html_fields: List of field names that can contain HTML
            
        Returns:
            Sanitized dictionary
        """
        if not isinstance(data, dict):
            return data
            
        allow_html_fields = allow_html_fields or []
        sanitized = {}
        
        for key, value in data.items():
            allow_html = key in allow_html_fields
            
            if isinstance(value, str):
                sanitized[key] = InputSanitizer.sanitize_string(value, allow_html)
            elif isinstance(value, dict):
                sanitized[key] = InputSanitizer.sanitize_dict(value, allow_html_fields)
            elif isinstance(value, list):
                sanitized[key] = [
                    InputSanitizer.sanitize_string(item, allow_html) if isinstance(item, str)
                    else InputSanitizer.sanitize_dict(item, allow_html_fields) if isinstance(item, dict)
                    else item
                    for item in value
                ]
            else:
                sanitized[key] = value
                
        return sanitized
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Basic email validation"""
        if not isinstance(email, str) or not email:
            return False
        return '@' in email and '.' in email.split('@')[-1]
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Basic phone number validation"""
        if not isinstance(phone, str):
            return False
        # Remove common formatting characters
        clean_phone = ''.join(c for c in phone if c.isdigit() or c == '+')
        # Basic validation: 10-15 digits, optionally starting with +
        return 10 <= len(clean_phone) <= 15 and (clean_phone[0] == '+' or clean_phone[0].isdigit())

class AuditLogger:
    """Comprehensive audit logging system with database persistence"""
    
    def __init__(self, db_pool=None):
        self.db_pool = db_pool
        self.log_buffer = []
        self.batch_size = 100  # Batch size for database writes
    
    def log_action(self, user_id: int, action: str, resource_type: str, 
                   resource_id: Optional[int] = None, details: Optional[Dict] = None,
                   severity: str = 'INFO'):
        """
        Log user action for audit trail
        
        Args:
            user_id: ID of user performing action
            action: Action performed (CREATE, UPDATE, DELETE, LOGIN, etc.)
            resource_type: Type of resource (student, teacher, class, etc.)
            resource_id: ID of specific resource
            details: Additional details about the action
            severity: Log severity (INFO, WARNING, ERROR, CRITICAL)
        """
        audit_entry = {
            'timestamp': datetime.datetime.utcnow().isoformat(),
            'user_id': user_id,
            'action': action.upper(),
            'resource_type': resource_type.lower(),
            'resource_id': resource_id,
            'details': json.dumps(details or {}, default=str),
            'ip_address': request.remote_addr if request else 'unknown',
            'user_agent': request.user_agent.string[:255] if request else 'unknown',
            'endpoint': request.endpoint if request else 'unknown',
            'method': request.method if request else 'unknown',
            'severity': severity.upper()
        }
        
        self.log_buffer.append(audit_entry)
        
        # Write to database if available and buffer is full
        if self.db_pool and len(self.log_buffer) >= self.batch_size:
            self.flush_logs()
        
        # Also log to console for immediate visibility
        print(f"AUDIT [{severity}]: {json.dumps(audit_entry, default=str)}")
    
    def log_security_event(self, event_type: str, user_id: Optional[int] = None, 
                          details: Optional[Dict] = None, severity: str = 'WARNING'):
        """Log security-related events"""
        self.log_action(
            user_id=user_id or 0,
            action=f'SECURITY_{event_type.upper()}',
            resource_type='security',
            details=details,
            severity=severity
        )
    
    def log_login_attempt(self, user_id: Optional[int], username: str, 
                         success: bool, ip_address: str = None):
        """Log login attempt"""
        self.log_security_event(
            event_type='login_attempt',
            user_id=user_id,
            details={
                'username': username,
                'success': success,
                'ip_address': ip_address or (request.remote_addr if request else 'unknown')
            },
            severity='INFO' if success else 'WARNING'
        )
    
    def log_unauthorized_access(self, user_id: Optional[int], attempted_resource: str,
                               required_role: str = None):
        """Log unauthorized access attempts"""
        self.log_security_event(
            event_type='unauthorized_access',
            user_id=user_id,
            details={
                'attempted_resource': attempted_resource,
                'required_role': required_role
            },
            severity='ERROR'
        )
    
    def log_data_modification(self, user_id: int, action: str, resource_type: str,
                            resource_id: int, old_values: Dict = None, 
                            new_values: Dict = None):
        """Log data modification events"""
        self.log_action(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details={
                'old_values': old_values,
                'new_values': new_values,
                'modification_type': 'data_change'
            },
            severity='INFO'
        )
    
    def flush_logs(self):
        """Flush buffered logs to database"""
        if not self.log_buffer or not self.db_pool:
            return
            
        try:
            conn = self.db_pool.get_connection()
            try:
                cur = conn.cursor()
                
                # Create audit_logs table if it doesn't exist
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS audit_logs (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        user_id INT,
                        action VARCHAR(50),
                        resource_type VARCHAR(50),
                        resource_id INT,
                        details JSON,
                        ip_address VARCHAR(45),
                        user_agent TEXT,
                        endpoint VARCHAR(100),
                        method VARCHAR(10),
                        severity ENUM('INFO', 'WARNING', 'ERROR', 'CRITICAL') DEFAULT 'INFO',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Insert batch of logs
                insert_query = """
                    INSERT INTO audit_logs 
                    (timestamp, user_id, action, resource_type, resource_id, 
                     details, ip_address, user_agent, endpoint, method, severity)
                    VALUES (%(timestamp)s, %(user_id)s, %(action)s, %(resource_type)s, 
                            %(resource_id)s, %(details)s, %(ip_address)s, %(user_agent)s, 
                            %(endpoint)s, %(method)s, %(severity)s)
                """
                
                # Convert timestamp string back to datetime for MySQL
                for entry in self.log_buffer:
                    if isinstance(entry['timestamp'], str):
                        entry['timestamp'] = datetime.datetime.fromisoformat(
                            entry['timestamp'].replace('Z', '+00:00')
                        )
                
                cur.executemany(insert_query, self.log_buffer)
                conn.commit()
                
                print(f"✅ Flushed {len(self.log_buffer)} audit log entries to database")
                self.log_buffer.clear()
                
            except Exception as e:
                print(f"⚠️ Database flush error: {e}")
                # Keep logs in buffer for retry
                conn.rollback()
            finally:
                conn.close()
                
        except Exception as e:
            print(f"⚠️ Connection error: {e}")
    
    def get_audit_trail(self, user_id: int = None, resource_type: str = None, 
                       action: str = None, days: int = 30, limit: int = 1000) -> List[Dict]:
        """
        Retrieve audit trail with optional filters
        
        Args:
            user_id: Filter by user ID
            resource_type: Filter by resource type
            action: Filter by action
            days: Number of days to look back
            limit: Maximum number of records to return
            
        Returns:
            List of audit log entries
        """
        if not self.db_pool:
            return []
        
        try:
            conn = self.db_pool.get_connection()
            try:
                cur = conn.cursor(dictionary=True)
                
                # Build query with filters
                query = "SELECT * FROM audit_logs WHERE timestamp >= DATE_SUB(NOW(), INTERVAL %s DAY)"
                params = [days]
                
                if user_id:
                    query += " AND user_id = %s"
                    params.append(user_id)
                
                if resource_type:
                    query += " AND resource_type = %s"
                    params.append(resource_type)
                
                if action:
                    query += " AND action = %s"
                    params.append(action)
                
                query += " ORDER BY timestamp DESC LIMIT %s"
                params.append(limit)
                
                cur.execute(query, params)
                results = cur.fetchall()
                
                return results
            finally:
                conn.close()
        except Exception as e:
            print(f"Audit trail retrieval error: {e}")
            return []
    
    def get_security_events(self, days: int = 7, severity: str = None, limit: int = 100) -> List[Dict]:
        """Get security-related events"""
        filters = {
            'action': 'SECURITY_%',
            'days': days,
            'limit': limit
        }
        if severity:
            filters['severity'] = severity
            
        return self.get_audit_trail(**filters)
    
    def cleanup_old_logs(self, days_to_keep: int = 180):
        """Clean up old audit logs"""
        if not self.db_pool:
            return
            
        try:
            conn = self.db_pool.get_connection()
            try:
                cur = conn.cursor()
                cur.execute(
                    "DELETE FROM audit_logs WHERE timestamp < DATE_SUB(NOW(), INTERVAL %s DAY)",
                    (days_to_keep,)
                )
                deleted_count = cur.rowcount
                conn.commit()
                print(f"✅ Cleaned up {deleted_count} old audit log entries")
            finally:
                conn.close()
        except Exception as e:
            print(f"Audit log cleanup error: {e}")

class TwoFactorAuth:
    """Two-factor authentication implementation"""
    
    @staticmethod
    def generate_secret() -> str:
        """Generate a new TOTP secret"""
        return pyotp.random_base32()
    
    @staticmethod
    def generate_qr_code(secret: str, username: str, issuer: str = "EduFlow") -> str:
        """
        Generate QR code for 2FA setup
        
        Args:
            secret: TOTP secret
            username: User's username
            issuer: Application name for authenticator app
            
        Returns:
            Base64 encoded QR code image
        """
        totp = pyotp.totp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(username, issuer=issuer)
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return img_str
    
    @staticmethod
    def verify_token(secret: str, token: str) -> bool:
        """
        Verify 2FA token
        
        Args:
            secret: User's TOTP secret
            token: Token from authenticator app
            
        Returns:
            True if token is valid
        """
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)  # 1 window tolerance

class SecurityMiddleware:
    """Main security middleware class"""
    
    def __init__(self, app=None, db_pool=None):
        self.rate_limiter = RateLimiter()
        self.input_sanitizer = InputSanitizer()
        self.audit_logger = AuditLogger(db_pool)
        self.two_factor_auth = TwoFactorAuth()
        self.db_pool = db_pool
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app"""
        app.before_request(self.security_middleware)
        app.after_request(self.after_request)
        app.teardown_appcontext(self.teardown_app)
    
    def security_middleware(self):
        """Main security middleware function"""
        # Generate client key for rate limiting
        client_key = f"{request.remote_addr}:{request.endpoint or 'unknown'}"
        
        # Determine limit type based on endpoint
        endpoint = request.endpoint or ''
        if 'login' in endpoint.lower() or 'auth' in endpoint.lower():
            limit_type = 'auth'
        elif endpoint.startswith('api'):
            limit_type = 'api'
        else:
            limit_type = 'default'
        
        # Check rate limits
        if not self.rate_limiter.is_allowed(client_key, limit_type):
            limits = self.rate_limiter.get_limits_for_client(client_key)
            return jsonify({
                'success': False,
                'error': 'Rate limit exceeded',
                'error_ar': 'تم تجاوز حد الطلبات',
                'rate_limit': limits.get(limit_type)
            }), 429
        
        # Sanitize input data for POST/PUT requests
        if request.method in ['POST', 'PUT', 'PATCH']:
            if request.is_json:
                try:
                    raw_data = request.get_json()
                    if isinstance(raw_data, dict):
                        # Sanitize but preserve specific fields that need HTML
                        allow_html_fields = ['description', 'notes', 'bio']
                        sanitized_data = self.input_sanitizer.sanitize_dict(
                            raw_data, allow_html_fields
                        )
                        # Replace request data (this is a simplified approach)
                        request._cached_json = (sanitized_data, sanitized_data)
                except Exception as e:
                    # Log sanitization error but don't fail the request
                    print(f"Input sanitization error: {e}")
    
    def after_request(self, response):
        """After request processing"""
        # Flush audit logs
        self.audit_logger.flush_logs()
        return response
    
    def teardown_app(self, exception):
        """Teardown application context"""
        # Final flush of audit logs
        self.audit_logger.flush_logs()
    
    def rate_limit_exempt(self, f):
        """Decorator to exempt route from rate limiting"""
        f.rate_limit_exempt = True
        return f
    
    def get_rate_limit_headers(self, client_key: str) -> Dict[str, str]:
        """Get rate limit headers for response"""
        limits = self.rate_limiter.get_limits_for_client(client_key)
        
        headers = {}
        for limit_type, info in limits.items():
            headers[f'X-RateLimit-{limit_type.capitalize()}-Limit'] = str(info['limit'])
            headers[f'X-RateLimit-{limit_type.capitalize()}-Remaining'] = str(info['remaining'])
            headers[f'X-RateLimit-{limit_type.capitalize()}-Reset'] = str(int(info['reset_time']))
        
        return headers

# Global security instance
_security_middleware = None

def get_security_middleware() -> SecurityMiddleware:
    """Get global security middleware instance"""
    global _security_middleware
    if _security_middleware is None:
        _security_middleware = SecurityMiddleware()
    return _security_middleware

def setup_security(app, db_pool=None) -> SecurityMiddleware:
    """Setup security middleware for Flask app"""
    global _security_middleware
    _security_middleware = SecurityMiddleware(app, db_pool)
    return _security_middleware

# Convenience decorators
def rate_limit_exempt(f):
    """Decorator to exempt route from rate limiting"""
    return get_security_middleware().rate_limit_exempt(f)

def sanitize_input(allow_html_fields: List[str] = None):
    """
    Decorator to automatically sanitize input for route
    
    Args:
        allow_html_fields: List of field names that can contain HTML
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Sanitize request data
            if request.is_json:
                try:
                    raw_data = request.get_json()
                    if isinstance(raw_data, dict):
                        sanitized_data = InputSanitizer.sanitize_dict(
                            raw_data, allow_html_fields or []
                        )
                        # Store sanitized data for route to use
                        g.sanitized_data = sanitized_data
                except Exception as e:
                    print(f"Input sanitization error in decorator: {e}")
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Export main classes and functions
__all__ = [
    'RateLimiter', 'InputSanitizer', 'AuditLogger', 'TwoFactorAuth', 
    'SecurityMiddleware', 'get_security_middleware', 'setup_security',
    'rate_limit_exempt', 'sanitize_input'
]