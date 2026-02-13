# Student Progress Monitoring Workflows

<cite>
**Referenced Files in This Document**
- [README.md](file://README.md)
- [server.py](file://server.py)
- [database.py](file://database.py)
- [services.py](file://services.py)
- [utils.py](file://utils.py)
- [validation.py](file://validation.py)
- [auth.py](file://auth.py)
- [public/teacher-portal.html](file://public/teacher-portal.html)
- [public/school-dashboard.html](file://public/school-dashboard.html)
- [public/student-portal.html](file://public/student-portal.html)
- [public/admin-dashboard.html](file://public/admin-dashboard.html)
- [requirements.txt](file://requirements.txt)
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
This document describes the student progress monitoring workflows implemented in the EduFlow Python school management system. It covers attendance tracking, behavioral monitoring, academic performance evaluation, teacher-student supervision responsibilities, class management integration, progress reporting mechanisms, automated alerts, and real-time updates. The system integrates grading systems, attendance tracking, and provides performance analytics dashboards for administrators, schools, teachers, and students.

## Project Structure
The project follows a layered architecture:
- Backend API built with Flask
- Database abstraction supporting both MySQL and SQLite
- Service layer encapsulating business logic
- Frontend dashboards for admin, school, teacher, and student portals
- Utility and validation modules for data integrity and security

```mermaid
graph TB
subgraph "Frontend Portals"
Admin["Admin Dashboard<br/>admin-dashboard.html"]
School["School Dashboard<br/>school-dashboard.html"]
Teacher["Teacher Portal<br/>teacher-portal.html"]
Student["Student Portal<br/>student-portal.html"]
end
subgraph "Backend Services"
FlaskApp["Flask Server<br/>server.py"]
Services["Services Layer<br/>services.py"]
Utils["Utilities & Validation<br/>utils.py, validation.py"]
Auth["Authentication<br/>auth.py"]
end
subgraph "Data Layer"
DB["Database Abstraction<br/>database.py"]
MySQL["MySQL Connector"]
SQLite["SQLite Adapter"]
end
Admin --> FlaskApp
School --> FlaskApp
Teacher --> FlaskApp
Student --> FlaskApp
FlaskApp --> Services
Services --> DB
DB --> MySQL
DB --> SQLite
FlaskApp --> Auth
FlaskApp --> Utils
```

**Diagram sources**
- [server.py](file://server.py#L1-L120)
- [database.py](file://database.py#L88-L120)
- [services.py](file://services.py#L1-L40)
- [utils.py](file://utils.py#L1-L40)
- [validation.py](file://validation.py#L1-L40)
- [auth.py](file://auth.py#L1-L40)
- [public/admin-dashboard.html](file://public/admin-dashboard.html#L1-L40)
- [public/school-dashboard.html](file://public/school-dashboard.html#L1-L40)
- [public/teacher-portal.html](file://public/teacher-portal.html#L1-L40)
- [public/student-portal.html](file://public/student-portal.html#L1-L40)

**Section sources**
- [README.md](file://README.md#L1-L23)
- [requirements.txt](file://requirements.txt#L1-L14)

## Core Components
- Flask server with CORS and JWT-based authentication
- Database abstraction with MySQL connector and SQLite fallback
- Service layer for business logic (recommendations, student/teacher operations)
- Utilities for validation, sanitization, and response formatting
- Validation framework for robust input checks
- Authentication middleware with token management
- Frontend dashboards for admin, school, teacher, and student with integrated analytics

Key capabilities:
- Student profile management with detailed scores and daily attendance JSON fields
- Academic year management and centralized academic year table
- Teacher subject and class assignment tracking
- Performance analytics and recommendations engine
- Real-time progress reporting and trend analysis

**Section sources**
- [server.py](file://server.py#L1-L120)
- [database.py](file://database.py#L120-L338)
- [services.py](file://services.py#L367-L474)
- [utils.py](file://utils.py#L27-L120)
- [validation.py](file://validation.py#L203-L262)
- [auth.py](file://auth.py#L14-L68)

## Architecture Overview
The system separates concerns across layers:
- Presentation: HTML/CSS/JS dashboards
- API: Flask routes handling CRUD operations and analytics
- Business Logic: Services encapsulate recommendation and aggregation logic
- Data Access: Database abstraction with connection pooling/fallback
- Security: JWT tokens, rate limiting, input sanitization

```mermaid
sequenceDiagram
participant Browser as "Browser"
participant API as "Flask API<br/>server.py"
participant Services as "Services<br/>services.py"
participant DB as "Database<br/>database.py"
participant Auth as "Auth<br/>auth.py"
Browser->>API : Login Request
API->>Auth : Verify Credentials
Auth-->>API : JWT Token
API-->>Browser : Token Response
Browser->>API : Progress Request (with token)
API->>Services : Aggregate Scores/Attendance
Services->>DB : Query student data
DB-->>Services : Results
Services-->>API : Aggregated Data
API-->>Browser : Progress Report
```

**Diagram sources**
- [server.py](file://server.py#L142-L200)
- [auth.py](file://auth.py#L36-L128)
- [services.py](file://services.py#L367-L474)
- [database.py](file://database.py#L120-L177)

## Detailed Component Analysis

### Database Schema and Data Models
The system maintains normalized tables with JSON fields for flexible data storage:
- Students: detailed_scores JSON, daily_attendance JSON
- Academic years: centralized system_academic_years
- Teacher assignments: teacher_subjects and teacher_class_assignments
- Subjects and grade levels for school-specific organization

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
string parent_contact
string blood_type
text chronic_disease
json detailed_scores
json daily_attendance
timestamp created_at
timestamp updated_at
}
SYSTEM_ACADEMIC_YEARS {
int id PK
string name
int start_year
int end_year
date start_date
date end_date
int is_current
timestamp created_at
timestamp updated_at
}
STUDENT_GRADES {
int id PK
int student_id FK
int academic_year_id FK
string subject_name
int month1
int month2
int midterm
int month3
int month4
int final
timestamp created_at
timestamp updated_at
}
STUDENT_ATTENDANCE {
int id PK
int student_id FK
int academic_year_id FK
date attendance_date
string status
text notes
timestamp created_at
}
TEACHERS {
int id PK
int school_id FK
string full_name
string teacher_code
string phone
string email
string password_hash
string grade_level
string specialization
text free_text_subjects
timestamp created_at
timestamp updated_at
}
SUBJECTS {
int id PK
int school_id FK
string name
string grade_level
timestamp created_at
timestamp updated_at
}
TEACHER_SUBJECTS {
int id PK
int teacher_id FK
int subject_id FK
timestamp created_at
}
TEACHER_CLASS_ASSIGNMENTS {
int id PK
int teacher_id FK
string class_name
int subject_id FK
int academic_year_id FK
timestamp assigned_at
}
STUDENTS ||--o{ STUDENT_GRADES : "has"
STUDENTS ||--o{ STUDENT_ATTENDANCE : "has"
SYSTEM_ACADEMIC_YEARS ||--o{ STUDENT_GRADES : "contains"
SYSTEM_ACADEMIC_YEARS ||--o{ STUDENT_ATTENDANCE : "contains"
TEACHERS ||--o{ TEACHER_SUBJECTS : "has"
SUBJECTS ||--o{ TEACHER_SUBJECTS : "assigned"
TEACHERS ||--o{ TEACHER_CLASS_ASSIGNMENTS : "teaches"
SUBJECTS ||--o{ TEACHER_CLASS_ASSIGNMENTS : "taught_in"
```

**Diagram sources**
- [database.py](file://database.py#L159-L320)

**Section sources**
- [database.py](file://database.py#L159-L320)

### Student Progress Data Aggregation
The system aggregates progress data from multiple sources:
- Academic grades across periods (monthly, midterm, final)
- Daily attendance records
- Behavioral indicators via attendance statuses and notes
- Performance trends and recommendations

```mermaid
flowchart TD
Start(["Load Student Data"]) --> FetchGrades["Fetch Academic Grades<br/>student_grades"]
FetchGrades --> FetchAttendance["Fetch Daily Attendance<br/>student_attendance"]
FetchAttendance --> ComputeAvg["Compute Averages<br/>by subject and overall"]
ComputeAvg --> AnalyzeTrends["Analyze Trends<br/>improving/declining/inconsistent"]
AnalyzeTrends --> GenerateRec["Generate Recommendations<br/>strengths, risks, study plan"]
GenerateRec --> Output["Return Progress Report"]
```

**Diagram sources**
- [services.py](file://services.py#L476-L546)
- [services.py](file://services.py#L701-L765)
- [public/student-portal.html](file://public/student-portal.html#L280-L550)

**Section sources**
- [services.py](file://services.py#L476-L546)
- [services.py](file://services.py#L701-L765)
- [public/student-portal.html](file://public/student-portal.html#L280-L550)

### Teacher-Student Supervision and Class Management
Teachers supervise students within their assigned subjects and classes:
- Subject assignment via teacher_subjects
- Class assignment via teacher_class_assignments
- Access to student profiles, grades, and attendance
- Recommendations for at-risk students

```mermaid
sequenceDiagram
participant Teacher as "Teacher"
participant API as "Flask API"
participant DB as "Database"
participant Rec as "Recommendation Engine"
Teacher->>API : Get Assigned Students
API->>DB : Query teacher_class_assignments
DB-->>API : Students in assigned classes
API->>Rec : Analyze student performance
Rec-->>API : Recommendations
API-->>Teacher : Student list + insights
```

**Diagram sources**
- [database.py](file://database.py#L509-L550)
- [services.py](file://services.py#L367-L430)

**Section sources**
- [database.py](file://database.py#L509-L550)
- [services.py](file://services.py#L367-L430)

### Progress Reporting Mechanisms
Progress reports aggregate grade data, attendance records, and behavioral indicators:
- Subject-wise averages and pass rates
- Overall class performance metrics
- Individual student performance insights
- Automated recommendations for improvement

```mermaid
classDiagram
class RecommendationService {
+get_teacher_recommendations(teacher_id) Dict
+get_student_recommendations(student_id) Dict
-_analyze_subject_performance(subject, students) Dict
-_generate_class_insights(subjects, students, analysis) Dict
-_generate_educational_strategies(analysis) Dict[]
-_identify_at_risk_students(students) Dict[]
-_analyze_student_performance(student_id, detailed_scores) Dict
-_generate_student_message(analysis) Dict
-_generate_study_suggestions(analysis, grade_level) str[]
}
class StudentAcademicAdvisor {
+analyzePerformance() Dict
+getPerformanceLevel() Dict
+generatePersonalSummary() str[]
+generateStrengthsSection() str[]
+generateImprovementAreas() str[]
+generateStudyPlan() str[]
+generateMotivationalMessage() str[]
+generateFullAdvice() str[]
}
RecommendationService --> StudentAcademicAdvisor : "uses"
```

**Diagram sources**
- [services.py](file://services.py#L367-L858)
- [public/student-portal.html](file://public/student-portal.html#L280-L550)

**Section sources**
- [services.py](file://services.py#L367-L858)
- [public/student-portal.html](file://public/student-portal.html#L280-L550)

### Automated Alerts and Notifications
The system provides mechanisms for automated progress alerts:
- Threshold-based warnings for at-risk students
- Trend-based alerts for declining performance
- Recommendations for intervention strategies
- Export capabilities for administrative oversight

```mermaid
flowchart TD
LoadData["Load Student Data"] --> CheckThresholds["Check Performance Thresholds"]
CheckThresholds --> IsAtRisk{"At-Risk?"}
IsAtRisk --> |Yes| TriggerAlert["Trigger Alert<br/>Notify Teacher/Admin"]
IsAtRisk --> |No| MonitorTrends["Monitor Trends"]
MonitorTrends --> DeclineDetected{"Decline Detected?"}
DeclineDetected --> |Yes| TriggerAlert
DeclineDetected --> |No| ContinueMonitoring["Continue Monitoring"]
```

**Diagram sources**
- [services.py](file://services.py#L657-L699)
- [public/student-portal.html](file://public/student-portal.html#L556-L713)

**Section sources**
- [services.py](file://services.py#L657-L699)
- [public/student-portal.html](file://public/student-portal.html#L556-L713)

### Typical Monitoring Scenarios
Common workflows:
- Daily attendance entry and automatic aggregation
- Periodic grade updates with trend analysis
- Behavioral monitoring via attendance statuses
- Teacher recommendations for at-risk students
- School-level analytics dashboards
- Student self-monitoring and personalized recommendations

**Section sources**
- [server.py](file://server.py#L683-L766)
- [public/teacher-portal.html](file://public/teacher-portal.html#L520-L533)
- [public/school-dashboard.html](file://public/school-dashboard.html#L310-L377)
- [public/student-portal.html](file://public/student-portal.html#L48-L125)

## Dependency Analysis
External dependencies include Flask, MySQL connector, bcrypt, PyJWT, and Chart.js for frontend analytics.

```mermaid
graph TB
Flask["Flask"]
FlaskCors["Flask-Cors"]
JWT["PyJWT"]
Bcrypt["bcrypt"]
MySQL["mysql-connector-python"]
Werkzeug["Werkzeug"]
Bleach["bleach"]
MarkupSafe["MarkupSafe"]
Psutil["psutil"]
QRCode["qrcode"]
PyOTP["pyotp"]
Redis["redis"]
Server["server.py"] --> Flask
Server --> FlaskCors
Server --> JWT
Server --> Bcrypt
Server --> MySQL
Server --> Werkzeug
Utils["utils.py"] --> Bleach
Utils --> MarkupSafe
Utils --> Psutil
Auth["auth.py"] --> JWT
Auth --> Bcrypt
Validation["validation.py"] --> Bleach
SchoolPortal["school-dashboard.html"] --> ChartJS["Chart.js"]
```

**Diagram sources**
- [requirements.txt](file://requirements.txt#L1-L14)

**Section sources**
- [requirements.txt](file://requirements.txt#L1-L14)

## Performance Considerations
- Database connection pooling for MySQL with SQLite fallback
- JSON field handling for flexible student data storage
- Caching layer integration points
- Efficient aggregation queries for performance analytics
- Frontend chart rendering with Chart.js for real-time dashboards

## Troubleshooting Guide
Common issues and resolutions:
- Database connectivity: Verify MySQL host/port/user/password environment variables
- Authentication failures: Check JWT secret and token validity
- Input validation errors: Review validation rules and error messages
- Performance bottlenecks: Monitor query execution and consider indexing strategies

**Section sources**
- [server.py](file://server.py#L110-L139)
- [utils.py](file://utils.py#L19-L78)
- [validation.py](file://validation.py#L174-L202)

## Conclusion
EduFlow provides a comprehensive student progress monitoring solution with integrated attendance tracking, behavioral monitoring, and academic performance evaluation. The system supports teacher-student supervision, class management, real-time progress reporting, automated alerts, and performance analytics dashboards. Its modular architecture enables scalability and maintainability while ensuring data integrity and security.