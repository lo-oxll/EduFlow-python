import os
import datetime
import time
import random
import string
import bcrypt
import sqlite3
from dotenv import load_dotenv

load_dotenv()

# Database configuration
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'school_db')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
SQLITE_PATH = os.getenv('SQLITE_PATH', os.path.join(os.path.dirname(__file__), 'school.db'))

_mysql_pool = None
_use_sqlite = False

# SQLite adapter class to mimic MySQL connection pool interface
class SQLiteConnectionWrapper:
    def __init__(self, path):
        self.path = path
        self._conn = None
    
    def get_connection(self):
        conn = sqlite3.connect(self.path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return SQLiteConnection(conn)

class SQLiteConnection:
    def __init__(self, conn):
        self._conn = conn
    
    def cursor(self, dictionary=False):
        return SQLiteCursor(self._conn.cursor(), dictionary)
    
    def commit(self):
        self._conn.commit()
    
    def close(self):
        self._conn.close()

class SQLiteCursor:
    def __init__(self, cursor, dictionary=False):
        self._cursor = cursor
        self._dictionary = dictionary
        self.lastrowid = None
        self.rowcount = 0
    
    def execute(self, query, params=None):
        # Convert MySQL placeholders %s to SQLite ?
        query = query.replace('%s', '?')
        # Handle JSON type for SQLite (store as TEXT)
        query = query.replace(' JSON', ' TEXT')
        # Handle MySQL-specific syntax
        query = query.replace('ENGINE=InnoDB DEFAULT CHARSET=utf8mb4', '')
        query = query.replace('ON UPDATE CURRENT_TIMESTAMP', '')
        # Convert MySQL auto-increment to SQLite
        query = query.replace('INT AUTO_INCREMENT PRIMARY KEY', 'INTEGER PRIMARY KEY AUTOINCREMENT')
        query = query.replace('INT AUTO_INCREMENT', 'INTEGER')
        query = query.replace('INT NOT NULL', 'INTEGER NOT NULL')
        
        if params:
            self._cursor.execute(query, params)
        else:
            self._cursor.execute(query)
        self.lastrowid = self._cursor.lastrowid
        self.rowcount = self._cursor.rowcount
    
    def fetchone(self):
        row = self._cursor.fetchone()
        if row is None:
            return None
        if self._dictionary:
            return dict(row)
        return tuple(row)
    
    def fetchall(self):
        rows = self._cursor.fetchall()
        if self._dictionary:
            return [dict(row) for row in rows]
        return [tuple(row) for row in rows]

def get_mysql_pool():
    global _mysql_pool, _use_sqlite
    
    # Return existing pool if available
    if _mysql_pool:
        return _mysql_pool
    
    # If already determined to use SQLite, return SQLite wrapper
    if _use_sqlite:
        return SQLiteConnectionWrapper(SQLITE_PATH)
    
    # Try MySQL first
    try:
        import mysql.connector
        from mysql.connector import pooling
        _mysql_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="school_pool",
            pool_size=10,
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
            port=MYSQL_PORT
        )
        print(f"[OK] Using MySQL database: {MYSQL_DATABASE} on {MYSQL_HOST}")
        return _mysql_pool
    except Exception as e:
        print(f"[WARN] MySQL connection failed: {e}")
        print(f"[OK] Falling back to SQLite: {SQLITE_PATH}")
        _use_sqlite = True
        return SQLiteConnectionWrapper(SQLITE_PATH)

def init_db():
    create_tables()

def create_tables():
    pool = get_mysql_pool()
    if not pool:
        return
    
    conn = pool.get_connection()
    try:
        cursor = conn.cursor()
        
        # Enable foreign keys for SQLite
        try:
            cursor.execute('PRAGMA foreign_keys = ON')
        except:
            pass  # MySQL doesn't support PRAGMA
        
        # Create users table
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
          id INT AUTO_INCREMENT PRIMARY KEY,
          username VARCHAR(255) UNIQUE NOT NULL,
          password_hash VARCHAR(255) NOT NULL,
          role VARCHAR(50) NOT NULL DEFAULT 'admin',
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')

        # Create schools table
        cursor.execute('''CREATE TABLE IF NOT EXISTS schools (
          id INT AUTO_INCREMENT PRIMARY KEY,
          name VARCHAR(255) NOT NULL,
          code VARCHAR(100) UNIQUE NOT NULL,
          study_type VARCHAR(100) NOT NULL,
          level VARCHAR(100) NOT NULL,
          gender_type VARCHAR(50) NOT NULL,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')

        # Create students table
        cursor.execute('''CREATE TABLE IF NOT EXISTS students (
          id INT AUTO_INCREMENT PRIMARY KEY,
          school_id INT NOT NULL,
          full_name VARCHAR(255) NOT NULL,
          student_code VARCHAR(100) UNIQUE NOT NULL,
          grade VARCHAR(50) NOT NULL,
          branch VARCHAR(100),
          room VARCHAR(100) NOT NULL,
          enrollment_date DATE,
          parent_contact VARCHAR(255),
          blood_type VARCHAR(10),
          chronic_disease TEXT,
          detailed_scores JSON,
          daily_attendance JSON,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(school_id) REFERENCES schools(id) ON DELETE CASCADE,
          UNIQUE KEY unique_student_school_grade_room (school_id, full_name, grade, room)
        )''')
        
        # Add new columns to existing students table if they don't exist (for migration)
        try:
            cursor.execute("ALTER TABLE students ADD COLUMN parent_contact VARCHAR(255)")
        except:
            pass  # Column already exists
        try:
            cursor.execute("ALTER TABLE students ADD COLUMN blood_type VARCHAR(10)")
        except:
            pass  # Column already exists
        try:
            cursor.execute("ALTER TABLE students ADD COLUMN chronic_disease TEXT")
        except:
            pass  # Column already exists
        try:
            cursor.execute("ALTER TABLE teachers ADD COLUMN free_text_subjects TEXT")
        except:
            pass  # Column already exists
        
        # Add unique constraint to prevent duplicate students (same name, grade, room, school)
        # This ensures database-level protection against duplicates
        try:
            cursor.execute("ALTER TABLE students ADD CONSTRAINT unique_student_school_grade_room UNIQUE (school_id, full_name, grade, room)")
        except:
            pass  # Constraint already exists or incompatible with existing data
        
        # Migration: Ensure grade_level column allows NULL values
        # This fixes databases created with NOT NULL constraint
        try:
            if _use_sqlite:
                # SQLite doesn't support ALTER COLUMN, need to recreate table
                cursor.execute("PRAGMA foreign_keys = OFF")
                cursor.execute('''CREATE TABLE IF NOT EXISTS teachers_new (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  school_id INTEGER NOT NULL,
                  full_name VARCHAR(255) NOT NULL,
                  teacher_code VARCHAR(50) UNIQUE NOT NULL,
                  phone VARCHAR(50),
                  email VARCHAR(255),
                  password_hash VARCHAR(255),
                  grade_level VARCHAR(100),
                  specialization VARCHAR(255),
                  free_text_subjects TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY(school_id) REFERENCES schools(id) ON DELETE CASCADE
                )''')
                cursor.execute('''INSERT OR IGNORE INTO teachers_new 
                    SELECT id, school_id, full_name, teacher_code, phone, email, password_hash, 
                           grade_level, specialization, free_text_subjects, created_at, updated_at 
                    FROM teachers''')
                cursor.execute("DROP TABLE IF EXISTS teachers")
                cursor.execute("ALTER TABLE teachers_new RENAME TO teachers")
                cursor.execute("PRAGMA foreign_keys = ON")
            else:
                # MySQL - modify column to allow NULL
                cursor.execute("ALTER TABLE teachers MODIFY COLUMN grade_level VARCHAR(100) NULL")
        except Exception as e:
            print(f"[INFO] Grade level column migration skipped: {e}")
            pass  # Column already has correct definition or other issue

        # Create subjects table
        cursor.execute('''CREATE TABLE IF NOT EXISTS subjects (
          id INT AUTO_INCREMENT PRIMARY KEY,
          school_id INT NOT NULL,
          name VARCHAR(255) NOT NULL,
          grade_level VARCHAR(50),
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(school_id) REFERENCES schools(id) ON DELETE CASCADE
        )''')

        # Create grade_levels table for custom grade levels per school
        cursor.execute('''CREATE TABLE IF NOT EXISTS grade_levels (
          id INT AUTO_INCREMENT PRIMARY KEY,
          school_id INT NOT NULL,
          name VARCHAR(255) NOT NULL,
          display_order INT DEFAULT 0,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(school_id) REFERENCES schools(id) ON DELETE CASCADE
        )''')

        # Create class_sections table to normalize class/room per grade and school
        cursor.execute('''CREATE TABLE IF NOT EXISTS class_sections (
          id INT AUTO_INCREMENT PRIMARY KEY,
          school_id INT NOT NULL,
          grade_level_id INT,
          name VARCHAR(100) NOT NULL,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(school_id) REFERENCES schools(id) ON DELETE CASCADE,
          FOREIGN KEY(grade_level_id) REFERENCES grade_levels(id) ON DELETE SET NULL,
          UNIQUE KEY unique_section_per_grade (school_id, grade_level_id, name)
        )''')

        # Create teachers table for managing teachers and their subjects
        cursor.execute('''CREATE TABLE IF NOT EXISTS teachers (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          school_id INTEGER NOT NULL,
          full_name VARCHAR(255) NOT NULL,
          teacher_code VARCHAR(50) UNIQUE NOT NULL,
          phone VARCHAR(50),
          email VARCHAR(255),
          password_hash VARCHAR(255),
          grade_level VARCHAR(100),
          specialization VARCHAR(255),
          free_text_subjects TEXT,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(school_id) REFERENCES schools(id) ON DELETE CASCADE
        )''')

        # Create teacher_subjects table for many-to-many relationship
        cursor.execute('''CREATE TABLE IF NOT EXISTS teacher_subjects (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          teacher_id INTEGER NOT NULL,
          subject_id INTEGER NOT NULL,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
          FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
          UNIQUE(teacher_id, subject_id)
        )''')

        # Create teacher_class_assignments table for tracking which teachers teach which classes
        cursor.execute('''CREATE TABLE IF NOT EXISTS teacher_class_assignments (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          teacher_id INTEGER NOT NULL,
          class_name VARCHAR(255) NOT NULL,
          subject_id INTEGER NOT NULL,
          academic_year_id INTEGER,
          assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
          FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
          FOREIGN KEY(academic_year_id) REFERENCES system_academic_years(id) ON DELETE SET NULL,
          UNIQUE(teacher_id, class_name, subject_id, academic_year_id)
        )''')

        # Create system_academic_years table for centralized academic year management
        # This table is managed by the system administrator and applies to ALL schools
        cursor.execute('''CREATE TABLE IF NOT EXISTS system_academic_years (
          id INT AUTO_INCREMENT PRIMARY KEY,
          name VARCHAR(50) NOT NULL UNIQUE,
          start_year INT NOT NULL,
          end_year INT NOT NULL,
          start_date DATE,
          end_date DATE,
          is_current INT DEFAULT 0,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Legacy: Keep academic_years table for backward compatibility during migration
        # New implementations should use system_academic_years
        cursor.execute('''CREATE TABLE IF NOT EXISTS academic_years (
          id INT AUTO_INCREMENT PRIMARY KEY,
          school_id INT NOT NULL,
          name VARCHAR(50) NOT NULL,
          start_year INT NOT NULL,
          end_year INT NOT NULL,
          start_date DATE,
          end_date DATE,
          is_current INT DEFAULT 0,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(school_id) REFERENCES schools(id) ON DELETE CASCADE
        )''')
        
        # Create student_grades table for storing grades per academic year (uses system_academic_years)
        cursor.execute('''CREATE TABLE IF NOT EXISTS student_grades (
          id INT AUTO_INCREMENT PRIMARY KEY,
          student_id INT NOT NULL,
          academic_year_id INT NOT NULL,
          subject_name VARCHAR(255) NOT NULL,
          month1 INT DEFAULT 0,
          month2 INT DEFAULT 0,
          midterm INT DEFAULT 0,
          month3 INT DEFAULT 0,
          month4 INT DEFAULT 0,
          final INT DEFAULT 0,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
          FOREIGN KEY(academic_year_id) REFERENCES system_academic_years(id) ON DELETE CASCADE
        )''')
        
        # Create student_attendance table for storing attendance per academic year (uses system_academic_years)
        cursor.execute('''CREATE TABLE IF NOT EXISTS student_attendance (
          id INT AUTO_INCREMENT PRIMARY KEY,
          student_id INT NOT NULL,
          academic_year_id INT NOT NULL,
          attendance_date DATE NOT NULL,
          status VARCHAR(20) NOT NULL DEFAULT "present",
          notes TEXT,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
          FOREIGN KEY(academic_year_id) REFERENCES system_academic_years(id) ON DELETE CASCADE
        )''')

        # Ensure a unique attendance record per student/date/year for ON DUPLICATE KEY logic
        try:
            cursor.execute(
                "ALTER TABLE student_attendance "
                "ADD CONSTRAINT unique_student_attendance_per_day "
                "(student_id, academic_year_id, attendance_date)"
            )
        except Exception:
            # Constraint already exists or incompatible with existing data
            pass

        # Create default admin
        cursor.execute('SELECT * FROM users WHERE username = %s', ('alikoko',))
        if not cursor.fetchone():
            pwd_hash = bcrypt.hashpw('alikoko0000'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute('INSERT INTO users(username, password_hash, role) VALUES(%s, %s, %s)',
                           ('alikoko', pwd_hash, 'admin'))
            print('[OK] Default admin created (alikoko / alikoko0000)')
        else:
            # Check if role is admin, update if needed
            cursor.execute('UPDATE users SET role = %s WHERE username = %s', ('admin', 'alikoko'))
            
        conn.commit()
        print('[OK] Database tables created successfully')
    except Exception as e:
        print(f"[ERROR] Error creating tables: {e}")
    finally:
        conn.close()

def generate_school_code():
    import time
    import random
    import string
    timestamp = str(int(time.time() * 1000))[-6:]
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
    return f"SCH-{timestamp}-{random_str}"

def get_unique_school_code():
    code = generate_school_code()
    pool = get_mysql_pool()
    if not pool:
        return code
        
    conn = pool.get_connection()
    try:
        cursor = conn.cursor()
        while True:
            cursor.execute('SELECT code FROM schools WHERE code = %s', (code,))
            if not cursor.fetchone():
                break
            code = generate_school_code()
    finally:
        conn.close()
    
    return code

def generate_teacher_code():
    """Generate a unique teacher code in format TCHR-XXXXX-XXXX with enhanced uniqueness"""
    import time
    import random
    import string
    import hashlib
    
    # Use multiple entropy sources for maximum uniqueness
    timestamp_ns = str(int(time.time() * 1000000000))[-5:]  # Nanosecond timestamp
    timestamp_ms = str(int(time.time() * 1000))[-3:]       # Millisecond timestamp
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    
    # Add process-specific entropy
    process_entropy = str(hash(str(time.process_time())))[-2:]
    
    # Combine all sources
    combined = f"{timestamp_ns}{timestamp_ms}{random_part}{process_entropy}"
    
    # Hash to ensure consistent length and distribution
    hash_obj = hashlib.md5(combined.encode())
    hash_hex = hash_obj.hexdigest()[:4].upper()
    
    return f"TCHR-{timestamp_ns}-{hash_hex}"

def get_unique_teacher_code(school_id):
    """Generate a unique teacher code for a specific school with improved uniqueness"""
    import time
    import random
    import string
    
    max_attempts = 5000  # Increase attempts limit significantly
    attempts = 0
    
    pool = get_mysql_pool()
    if not pool:
        # Fallback to generated code if database unavailable
        return generate_teacher_code()
        
    conn = pool.get_connection()
    try:
        cursor = conn.cursor()
        
        # First, get all existing codes for this school to avoid them
        cursor.execute('SELECT teacher_code FROM teachers WHERE school_id = %s', (school_id,))
        existing_codes = {row[0] for row in cursor.fetchall()}
        
        while attempts < max_attempts:
            code = generate_teacher_code()
            
            # Check against existing codes in memory first (faster)
            if code not in existing_codes:
                # Double-check with database query
                cursor.execute('SELECT teacher_code FROM teachers WHERE teacher_code = %s AND school_id = %s', (code, school_id))
                if not cursor.fetchone():
                    # Verify the code format is correct
                    if code.startswith('TCHR-') and len(code) == 14:  # TCHR-XXXXX-XXXX
                        return code
            
            attempts += 1
            
            # Add more entropy after failed attempts
            if attempts > 100:
                # Add more randomness to increase uniqueness
                extra_random = ''.join(random.choices(string.ascii_uppercase + string.digits, k=2))
                timestamp = str(int(time.time() * 1000000000))[-5:]
                # Generate new random string instead of using undefined variable
                additional_random = ''.join(random.choices(string.ascii_uppercase + string.digits, k=2))
                code = f"TCHR-{timestamp}-{extra_random}{additional_random}"
            
            # Add progressive delays to prevent rapid generation
            if attempts % 100 == 0:
                time.sleep(0.05)  # Increase delay
            elif attempts % 50 == 0:
                time.sleep(0.02)
                
    finally:
        conn.close()
    
    # If we can't generate a unique code after max_attempts, try a different approach
    print(f"Warning: Could not generate unique code after {max_attempts} attempts for school {school_id}")
    
    # Fallback: Generate code with UUID component for guaranteed uniqueness
    import uuid
    unique_suffix = str(uuid.uuid4())[:4].upper()
    timestamp = str(int(time.time() * 1000000000))[-5:]
    fallback_code = f"TCHR-{timestamp}-{unique_suffix}"
    
    # Verify fallback code doesn't exist
    conn = pool.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT teacher_code FROM teachers WHERE teacher_code = %s AND school_id = %s', (fallback_code, school_id))
        if not cursor.fetchone():
            return fallback_code
    finally:
        conn.close()
    
    # Last resort: raise error with more helpful message
    raise Exception(f"Unable to generate unique teacher code for school {school_id} after {max_attempts} attempts. Database may be full or corrupted.")

def get_teacher_subjects(teacher_id):
    """Get all subjects assigned to a teacher (both predefined and free-text)"""
    pool = get_mysql_pool()
    if not pool:
        return []
        
    conn = pool.get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        
        # First get predefined subjects
        predefined_query = '''
            SELECT s.id, s.name, s.grade_level
            FROM teacher_subjects ts
            JOIN subjects s ON ts.subject_id = s.id
            WHERE ts.teacher_id = %s
            ORDER BY s.name
        '''
        cursor.execute(predefined_query, (teacher_id,))
        predefined_subjects = cursor.fetchall()
        
        # Then get free-text subjects
        free_text_query = '''
            SELECT free_text_subjects
            FROM teachers
            WHERE id = %s
        '''
        cursor.execute(free_text_query, (teacher_id,))
        result = cursor.fetchone()
        
        free_text_subjects = []
        if result and result['free_text_subjects']:
            # Split free-text subjects by comma and create subject objects
            subjects_list = [s.strip() for s in result['free_text_subjects'].split(',') if s.strip()]
            free_text_subjects = [{'id': None, 'name': subject, 'grade_level': 'free_text'} for subject in subjects_list]
        
        # Combine both lists
        all_subjects = predefined_subjects + free_text_subjects
        return all_subjects
    finally:
        conn.close()

def get_teacher_students(teacher_id, academic_year_id=None):
    """Get all students taught by a teacher based on their subjects"""
    pool = get_mysql_pool()
    if not pool:
        return []
        
    conn = pool.get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        # Get teacher's school_id first
        cursor.execute('SELECT school_id FROM teachers WHERE id = %s', (teacher_id,))
        teacher_school = cursor.fetchone()
        
        if not teacher_school:
            return []
        
        school_id = teacher_school['school_id']
        
        # Get teacher's subjects first
        subject_query = '''
            SELECT s.id, s.name, s.grade_level
            FROM teacher_subjects ts
            JOIN subjects s ON ts.subject_id = s.id
            WHERE ts.teacher_id = %s
        '''
        cursor.execute(subject_query, (teacher_id,))
        teacher_subjects = cursor.fetchall()
        
        if not teacher_subjects:
            return []
            
        # Get students in those grade levels AND same school
        # Note: Student grade format is "ابتدائي - الأول الابتدائي" 
        # while subject grade_level format is "الأول الابتدائي"
        # We need to match using LIKE pattern
        # Use set to deduplicate grade levels (teacher may teach multiple subjects in same grade)
        grade_levels = list(set([subject['grade_level'] for subject in teacher_subjects]))
        
        # Build a query that matches grades ending with the grade level
        # e.g., grade "ابتدائي - الأول الابتدائي" should match grade_level "الأول الابتدائي"
        conditions = []
        params = [school_id]  # Add school_id as first parameter
        for grade in grade_levels:
            conditions.append("s.grade LIKE %s")
            params.append(f"% - {grade}")
        
        # Also check for exact match in case formats are normalized in the future
        for grade in grade_levels:
            conditions.append("s.grade = %s")
            params.append(grade)
        
        student_query = f'''
            SELECT DISTINCT s.id, s.full_name, s.student_code, s.grade, s.room,
                   s.detailed_scores, s.daily_attendance
            FROM students s
            WHERE s.school_id = %s  -- Only get students from teacher's school
              AND ({' OR '.join(conditions)})
        '''
        
        if academic_year_id:
            student_query += ' AND s.academic_year_id = %s'
            params.append(academic_year_id)
            
        cursor.execute(student_query, params)
        students = cursor.fetchall()
        
        # Parse JSON fields
        for student in students:
            if student.get('detailed_scores'):
                try:
                    import json
                    if isinstance(student['detailed_scores'], str):
                        student['detailed_scores'] = json.loads(student['detailed_scores'])
                except:
                    student['detailed_scores'] = {}
            else:
                student['detailed_scores'] = {}
                
            if student.get('daily_attendance'):
                try:
                    import json
                    if isinstance(student['daily_attendance'], str):
                        student['daily_attendance'] = json.loads(student['daily_attendance'])
                except:
                    student['daily_attendance'] = {}
            else:
                student['daily_attendance'] = {}
        
        return students
    finally:
        conn.close()

def assign_teacher_to_class(teacher_id, class_name, subject_id, academic_year_id=None):
    """Assign a teacher to teach a specific subject in a class"""
    pool = get_mysql_pool()
    if not pool:
        return False
        
    conn = pool.get_connection()
    try:
        cursor = conn.cursor()
        query = '''INSERT INTO teacher_class_assignments 
                   (teacher_id, class_name, subject_id, academic_year_id) 
                   VALUES (%s, %s, %s, %s)'''
        cursor.execute(query, (teacher_id, class_name, subject_id, academic_year_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error assigning teacher to class: {e}")
        return False
    finally:
        conn.close()

def remove_teacher_from_class(assignment_id):
    """Remove a teacher's class assignment"""
    pool = get_mysql_pool()
    if not pool:
        return False
        
    conn = pool.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM teacher_class_assignments WHERE id = %s', (assignment_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error removing teacher from class: {e}")
        return False
    finally:
        conn.close()

def get_teacher_class_assignments(teacher_id, academic_year_id=None):
    """Get all class assignments for a teacher"""
    pool = get_mysql_pool()
    if not pool:
        return []
        
    conn = pool.get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        if academic_year_id:
            query = '''
                SELECT tca.*, s.name as subject_name, t.full_name as teacher_name
                FROM teacher_class_assignments tca
                JOIN subjects s ON tca.subject_id = s.id
                JOIN teachers t ON tca.teacher_id = t.id
                WHERE tca.teacher_id = %s AND tca.academic_year_id = %s
                ORDER BY tca.class_name, s.name
            '''
            cursor.execute(query, (teacher_id, academic_year_id))
        else:
            query = '''
                SELECT tca.*, s.name as subject_name, t.full_name as teacher_name
                FROM teacher_class_assignments tca
                JOIN subjects s ON tca.subject_id = s.id
                JOIN teachers t ON tca.teacher_id = t.id
                WHERE tca.teacher_id = %s
                ORDER BY tca.class_name, s.name
            '''
            cursor.execute(query, (teacher_id,))
        return cursor.fetchall()
    finally:
        conn.close()

def get_class_teachers(class_name, academic_year_id=None):
    """Get all teachers assigned to a specific class"""
    pool = get_mysql_pool()
    if not pool:
        return []
        
    conn = pool.get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        if academic_year_id:
            query = '''
                SELECT tca.*, t.full_name, t.teacher_code, s.name as subject_name
                FROM teacher_class_assignments tca
                JOIN teachers t ON tca.teacher_id = t.id
                JOIN subjects s ON tca.subject_id = s.id
                WHERE tca.class_name = %s AND tca.academic_year_id = %s
                ORDER BY s.name
            '''
            cursor.execute(query, (class_name, academic_year_id))
        else:
            query = '''
                SELECT tca.*, t.full_name, t.teacher_code, s.name as subject_name
                FROM teacher_class_assignments tca
                JOIN teachers t ON tca.teacher_id = t.id
                JOIN subjects s ON tca.subject_id = s.id
                WHERE tca.class_name = %s
                ORDER BY s.name
            '''
            cursor.execute(query, (class_name,))
        return cursor.fetchall()
    finally:
        conn.close()

def get_school_teachers_with_assignments(school_id, academic_year_id=None):
    """Get all teachers in a school with their class assignments"""
    pool = get_mysql_pool()
    if not pool:
        return []
        
    conn = pool.get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        if academic_year_id:
            query = '''
                SELECT t.*, 
                       COALESCE(GROUP_CONCAT(DISTINCT s.name), '') as subject_names,
                       COALESCE(GROUP_CONCAT(DISTINCT tca.class_name), '') as assigned_classes,
                       COUNT(DISTINCT tca.id) as assignment_count
                FROM teachers t
                LEFT JOIN teacher_subjects ts ON t.id = ts.teacher_id
                LEFT JOIN subjects s ON ts.subject_id = s.id
                LEFT JOIN teacher_class_assignments tca ON t.id = tca.teacher_id AND tca.academic_year_id = %s
                WHERE t.school_id = %s
                GROUP BY t.id
                ORDER BY t.full_name
            '''
            cursor.execute(query, (academic_year_id, school_id))
        else:
            query = '''
                SELECT t.*, 
                       COALESCE(GROUP_CONCAT(DISTINCT s.name), '') as subject_names,
                       COALESCE(GROUP_CONCAT(DISTINCT tca.class_name), '') as assigned_classes,
                       COUNT(DISTINCT tca.id) as assignment_count
                FROM teachers t
                LEFT JOIN teacher_subjects ts ON t.id = ts.teacher_id
                LEFT JOIN subjects s ON ts.subject_id = s.id
                LEFT JOIN teacher_class_assignments tca ON t.id = tca.teacher_id
                WHERE t.school_id = %s
                GROUP BY t.id
                ORDER BY t.full_name
            '''
            cursor.execute(query, (school_id,))
        return cursor.fetchall()
    finally:
        conn.close()

def get_school_teacher_class_assignments(school_id, academic_year_id=None):
    """Get all teacher-class assignments for a school"""
    pool = get_mysql_pool()
    if not pool:
        return []
        
    conn = pool.get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        query = '''
            SELECT tca.*, s.name as subject_name, t.full_name as teacher_name, t.teacher_code
            FROM teacher_class_assignments tca
            JOIN subjects s ON tca.subject_id = s.id
            JOIN teachers t ON tca.teacher_id = t.id
            WHERE t.school_id = %s
        '''
        params = [school_id]
        if academic_year_id:
            query += ' AND tca.academic_year_id = %s'
            params.append(academic_year_id)
        
        query += ' ORDER BY tca.class_name, s.name'
        cursor.execute(query, tuple(params))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error getting school teacher class assignments: {e}")
        return []
    finally:
        conn.close()
