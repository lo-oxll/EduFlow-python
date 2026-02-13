# Assessment Reporting System

<cite>
**Referenced Files in This Document**
- [README.md](file://README.md)
- [server.py](file://server.py)
- [database.py](file://database.py)
- [services.py](file://services.py)
- [performance.py](file://performance.py)
- [security.py](file://security.py)
- [cache.py](file://cache.py)
- [validation.py](file://validation.py)
- [requirements.txt](file://requirements.txt)
- [public/admin-dashboard.html](file://public/admin-dashboard.html)
- [public/teacher-portal.html](file://public/teacher-portal.html)
- [public/student-portal.html](file://public/student-portal.html)
- [public/school-dashboard.html](file://public/school-dashboard.html)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Architecture Overview](#architecture-overview)
5. [Detailed Component Analysis](#detailed-component-analysis)
6. [Dependency Analysis](#dependency-analysis)
7. [Performance Considerations](#performance-considerations)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Conclusion](#conclusion)

## Introduction
This document describes the Assessment Reporting System built with Python and Flask. It focuses on report generation mechanisms, progress tracking displays, and academic performance dashboards. The system integrates student profiles, teacher dashboards, and administrative reporting requirements, and provides real-time analytics and multi-format export capabilities.

## Project Structure
The system follows a layered architecture:
- Frontend: HTML/CSS/JavaScript dashboards for admin, school, teacher, and student portals
- Backend: Flask server exposing REST endpoints for authentication, data management, and analytics
- Services: Business logic layer for recommendations and performance analytics
- Persistence: MySQL/SQLite via a unified connection abstraction
- Infrastructure: Security middleware, caching, performance monitoring, and validation

```mermaid
graph TB
subgraph "Frontend Portals"
Admin["Admin Dashboard<br/>admin-dashboard.html"]
School["School Dashboard<br/>school-dashboard.html"]
Teacher["Teacher Portal<br/>teacher-portal.html"]
Student["Student Portal<br/>student-portal.html"]
end
subgraph "Backend API"
Server["Flask Server<br/>server.py"]
Services["Services Layer<br/>services.py"]
Security["Security & Validation<br/>security.py, validation.py"]
Cache["Caching Layer<br/>cache.py"]
Perf["Performance Monitoring<br/>performance.py"]
end
subgraph "Persistence"
DB["Database Abstraction<br/>database.py"]
MySQL["MySQL/SQLite"]
end
Admin --> Server
School --> Server
Teacher --> Server
Student --> Server
Server --> Services
Server --> Security
Server --> Cache
Server --> Perf
Services --> DB
DB --> MySQL
```

**Diagram sources**
- [server.py](file://server.py#L1-L200)
- [services.py](file://services.py#L1-L120)
- [database.py](file://database.py#L1-L120)
- [security.py](file://security.py#L1-L120)
- [cache.py](file://cache.py#L1-L120)
- [performance.py](file://performance.py#L1-L120)
- [public/admin-dashboard.html](file://public/admin-dashboard.html#L1-L174)
- [public/school-dashboard.html](file://public/school-dashboard.html#L1-L200)
- [public/teacher-portal.html](file://public/teacher-portal.html#L1-L120)
- [public/student-portal.html](file://public/student-portal.html#L1-L120)

**Section sources**
- [README.md](file://README.md#L1-L23)
- [requirements.txt](file://requirements.txt#L1-L14)

## Core Components
- Authentication and Authorization: JWT-based login for admin, school, and student; teacher login via code; role-based access control disabled for development
- Data Management: CRUD endpoints for schools, students, subjects, and teacher assignments
- Academic Data: Student grades and attendance stored as JSON fields with validation and scale-aware scoring
- Recommendations Engine: AI-powered academic insights for teachers and personalized guidance for students
- Performance Analytics: Dashboards with charts and AI predictions for performance trends
- Export Capabilities: Excel export for teacher and student lists from school dashboard

**Section sources**
- [server.py](file://server.py#L140-L304)
- [database.py](file://database.py#L138-L320)
- [services.py](file://services.py#L367-L765)
- [public/school-dashboard.html](file://public/school-dashboard.html#L270-L285)

## Architecture Overview
The backend exposes REST endpoints that integrate with a service layer for business logic, secured by middleware, cached for performance, and monitored for system metrics. The frontend portals consume these APIs to present dashboards and interactive reports.

```mermaid
sequenceDiagram
participant Client as "Portal Browser"
participant Server as "Flask Server<br/>server.py"
participant Sec as "Security<br/>security.py"
participant Cache as "Cache<br/>cache.py"
participant Svc as "Services<br/>services.py"
participant DB as "Database<br/>database.py"
Client->>Server : "POST /api/student/login"
Server->>Sec : "Authenticate JWT"
Server->>DB : "Query student by code"
DB-->>Server : "Student record"
Server-->>Client : "JWT token + student data"
Client->>Server : "GET /api/school/<id>/student"
Server->>Cache : "Check cache"
alt Cache miss
Server->>Svc : "Fetch student data"
Svc->>DB : "Query students"
DB-->>Svc : "Results"
Svc-->>Server : "Processed data"
Server->>Cache : "Store in cache"
else Cache hit
Cache-->>Server : "Cached data"
end
Server-->>Client : "Student list"
```

**Diagram sources**
- [server.py](file://server.py#L258-L304)
- [security.py](file://security.py#L476-L578)
- [cache.py](file://cache.py#L14-L120)
- [services.py](file://services.py#L232-L282)
- [database.py](file://database.py#L120-L177)

## Detailed Component Analysis

### Report Generation Mechanisms
- Student Comprehensive Reports: The student portal generates a comprehensive academic report by analyzing detailed scores and attendance, computing averages, identifying trends, and providing personalized recommendations.
- Teacher Grade Recommendations: The teacher portal surfaces recommendations derived from subject performance analysis, class insights, and at-risk student identification.
- Administrative Yearly Reports: The admin dashboard supports academic year management and enables exporting school lists; the school dashboard provides export buttons for teachers and students.

```mermaid
flowchart TD
Start(["Load Student Data"]) --> Parse["Parse detailed_scores JSON"]
Parse --> Scale["Detect grade scale (10 vs 100)"]
Scale --> Compute["Compute averages per period and subject"]
Compute --> Trends["Analyze grade trends and consistency"]
Trends --> Risk["Identify at-risk subjects and students"]
Risk --> Recommend["Generate personalized recommendations"]
Recommend --> Render["Render comprehensive report UI"]
Render --> End(["Report Ready"])
```

**Diagram sources**
- [public/student-portal.html](file://public/student-portal.html#L556-L713)
- [public/student-portal.html](file://public/student-portal.html#L277-L549)

**Section sources**
- [public/student-portal.html](file://public/student-portal.html#L113-L125)
- [public/teacher-portal.html](file://public/teacher-portal.html#L522-L533)
- [public/admin-dashboard.html](file://public/admin-dashboard.html#L80-L97)

### Progress Tracking Displays
- Student Tabs: Detailed scores, daily attendance, and comprehensive report tabs with trend analysis and at-risk indicators.
- Teacher Dashboard: Overview cards for subjects, student counts, attendance rates, and grade averages; modal for managing grades and attendance.
- School Dashboard: Performance analytics with indicators (average grade, pass rate, attendance, excellence rate), charts, and AI predictions.

```mermaid
graph LR
StudentPortal["Student Portal<br/>Tabs: Scores | Attendance | Report"]
TeacherPortal["Teacher Portal<br/>Dashboard + Modals"]
SchoolPortal["School Dashboard<br/>Analytics + Charts"]
StudentPortal --> |"Detailed Scores"| StudentPortal
StudentPortal --> |"Daily Attendance"| StudentPortal
StudentPortal --> |"Comprehensive Report"| StudentPortal
TeacherPortal --> |"Grades Modal"| TeacherPortal
TeacherPortal --> |"Attendance Modal"| TeacherPortal
SchoolPortal --> |"Indicators"| SchoolPortal
SchoolPortal --> |"Charts"| SchoolPortal
SchoolPortal --> |"AI Predictions"| SchoolPortal
```

**Diagram sources**
- [public/student-portal.html](file://public/student-portal.html#L67-L125)
- [public/teacher-portal.html](file://public/teacher-portal.html#L477-L558)
- [public/school-dashboard.html](file://public/school-dashboard.html#L311-L377)

**Section sources**
- [public/student-portal.html](file://public/student-portal.html#L67-L125)
- [public/teacher-portal.html](file://public/teacher-portal.html#L477-L558)
- [public/school-dashboard.html](file://public/school-dashboard.html#L311-L377)

### Academic Performance Dashboards
- Real-time Metrics: PerformanceMonitor tracks request times, endpoint statistics, and system metrics for observability.
- AI Predictions: The PerformanceModel computes predicted performance levels, risk categories, and subject trends for proactive interventions.
- Visualizations: Chart.js renders grade and attendance distributions in the school dashboard.

```mermaid
classDiagram
class PerformanceMonitor {
+request_times
+endpoint_stats
+record_db_query()
+get_performance_stats()
+get_endpoint_details()
+get_system_metrics()
}
class PerformanceModel {
+predictPerformance(student)
+getMaxGradeForStudent(grade)
+getThresholds(maxGrade)
}
PerformanceMonitor <.. Server : "registered endpoints"
PerformanceModel <.. SchoolPortal : "predictions"
```

**Diagram sources**
- [performance.py](file://performance.py#L15-L145)
- [public/school-dashboard.html](file://public/school-dashboard.html#L359-L377)

**Section sources**
- [performance.py](file://performance.py#L214-L241)
- [public/school-dashboard.html](file://public/school-dashboard.html#L359-L377)

### Report Templates and Data Formatting Standards
- Data Storage: Student detailed_scores and daily_attendance are stored as JSON fields in the students table, enabling flexible multi-period grade storage.
- Scale Awareness: The system detects elementary (1-4) versus higher grades to enforce appropriate score ranges (0-10 vs 0-100).
- Export Formats: The school dashboard provides Excel export buttons for teachers and students.

```mermaid
erDiagram
STUDENTS {
int id PK
int school_id FK
string full_name
string student_code
string grade
string room
date enrollment_date
text parent_contact
string blood_type
text chronic_disease
json detailed_scores
json daily_attendance
}
SUBJECTS {
int id PK
int school_id FK
string name
string grade_level
}
TEACHERS {
int id PK
int school_id FK
string full_name
string teacher_code
string phone
string email
text password_hash
string grade_level
string specialization
text free_text_subjects
}
STUDENTS ||--o{ SUBJECTS : "enrolled in"
SUBJECTS ||--o{ TEACHERS : "taught by"
```

**Diagram sources**
- [database.py](file://database.py#L159-L177)
- [database.py](file://database.py#L197-L206)
- [database.py](file://database.py#L220-L234)

**Section sources**
- [server.py](file://server.py#L564-L767)
- [database.py](file://database.py#L159-L177)
- [public/school-dashboard.html](file://public/school-dashboard.html#L273-L280)

### Multi-format Export Capabilities
- Excel Export: Buttons on the school dashboard trigger Excel exports for teachers and students using SheetJS integration in the admin dashboard HTML.
- Future Enhancements: PDF and CSV exports can be integrated by adding server endpoints and client-side handlers similar to the existing Excel export pattern.

**Section sources**
- [public/admin-dashboard.html](file://public/admin-dashboard.html#L100-L104)
- [public/school-dashboard.html](file://public/school-dashboard.html#L273-L280)

### Real-time Reporting Features
- Live Dashboards: Teacher and school dashboards update in real-time as grades and attendance are saved.
- Performance Monitoring: X-Response-Time and X-Request-ID headers provide latency insights; endpoint statistics help identify slow routes.
- Caching: Redis or in-memory cache accelerates repeated reads of school, student, and teacher data.

**Section sources**
- [performance.py](file://performance.py#L49-L77)
- [cache.py](file://cache.py#L14-L120)

### Automated Report Scheduling
- Current State: No explicit scheduler is implemented in the codebase.
- Recommended Implementation: Integrate a job scheduler (e.g., APScheduler) to periodically generate and distribute reports, with configurable intervals and recipient lists.

[No sources needed since this section provides general guidance]

### Stakeholder Access Controls
- Authentication: JWT-based login for admin, school, and student; teacher login via code.
- Authorization: Role-based decorator currently allows all access (disabled for development).
- Security Enhancements: Input sanitization, rate limiting, audit logging, and 2FA support are available for production hardening.

**Section sources**
- [server.py](file://server.py#L91-L108)
- [security.py](file://security.py#L476-L578)

### Practical Examples

#### Report Creation Workflow (Student)
1. Student logs in via student portal
2. Detailed scores and attendance are fetched
3. Performance model computes averages, trends, and risk levels
4. Personalized recommendations are generated and displayed

```mermaid
sequenceDiagram
participant Student as "Student Portal"
participant API as "Flask API"
participant Model as "PerformanceModel"
participant UI as "Report UI"
Student->>API : "GET /api/school/<id>/student"
API-->>Student : "Student data with detailed_scores"
Student->>Model : "predictPerformance(student)"
Model-->>Student : "Performance prediction + recommendations"
Student->>UI : "Render comprehensive report"
```

**Diagram sources**
- [public/student-portal.html](file://public/student-portal.html#L717-L739)
- [public/student-portal.html](file://public/student-portal.html#L556-L713)

#### Custom Report Configuration (Teacher)
1. Teacher selects subject and class
2. System aggregates grades and attendance
3. Recommendations engine identifies weak areas and suggests actions
4. Teacher saves grades and views updated analytics

**Section sources**
- [public/teacher-portal.html](file://public/teacher-portal.html#L522-L533)
- [services.py](file://services.py#L367-L474)

#### Report Distribution Mechanism (School)
1. Admin selects academic year and filters
2. System generates analytics and predictions
3. Export buttons produce Excel files for stakeholders

**Section sources**
- [public/admin-dashboard.html](file://public/admin-dashboard.html#L80-L97)
- [public/school-dashboard.html](file://public/school-dashboard.html#L273-L280)

## Dependency Analysis
The system relies on Flask and supporting libraries for web, security, caching, and performance monitoring. Database connectivity is abstracted to support both MySQL and SQLite.

```mermaid
graph TB
Flask["Flask"]
FlaskCors["Flask-CORS"]
PyJWT["PyJWT"]
bcrypt["bcrypt"]
pythonDotEnv["python-dotenv"]
mysqlConnector["mysql-connector-python"]
bleach["bleach"]
MarkupSafe["MarkupSafe"]
psutil["psutil"]
qrcode["qrcode"]
pyotp["pyotp"]
redis["redis"]
Flask --> FlaskCors
Flask --> PyJWT
Flask --> bcrypt
Flask --> pythonDotEnv
Flask --> mysqlConnector
Flask --> bleach
Flask --> MarkupSafe
Flask --> psutil
Flask --> qrcode
Flask --> pyotp
Flask --> redis
```

**Diagram sources**
- [requirements.txt](file://requirements.txt#L1-L14)

**Section sources**
- [requirements.txt](file://requirements.txt#L1-L14)

## Performance Considerations
- Caching: Use RedisCache or in-memory fallback to reduce database load for frequently accessed data.
- Query Optimization: Leverage database indexes on foreign keys and frequently filtered columns.
- Monitoring: Track slow endpoints and system metrics to identify bottlenecks.
- Scalability: Consider horizontal scaling and connection pooling for MySQL.

[No sources needed since this section provides general guidance]

## Troubleshooting Guide
- Authentication Issues: Verify JWT secret and environment configuration; ensure login endpoints receive sanitized inputs.
- Database Connectivity: Confirm MySQL host, user, password, and database settings; fallback to SQLite when MySQL is unavailable.
- Performance Problems: Review performance endpoints for slow routes and adjust caching strategies.
- Export Failures: Ensure SheetJS is loaded and Excel export buttons are bound to working handlers.

**Section sources**
- [server.py](file://server.py#L110-L139)
- [database.py](file://database.py#L88-L118)
- [performance.py](file://performance.py#L214-L241)
- [public/admin-dashboard.html](file://public/admin-dashboard.html#L16-L16)

## Conclusion
The Assessment Reporting System provides a robust foundation for academic reporting, progress tracking, and performance analytics. Its modular architecture supports real-time dashboards, AI-driven insights, and multi-format exports. With proper security hardening, caching, and scheduling enhancements, it can serve as a scalable solution for comprehensive school assessment reporting.