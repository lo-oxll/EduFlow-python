# Project Overview

<cite>
**Referenced Files in This Document**
- [README.md](file://README.md)
- [requirements.txt](file://requirements.txt)
- [server.py](file://server.py)
- [auth.py](file://auth.py)
- [database.py](file://database.py)
- [public/index.html](file://public/index.html)
- [public/admin-dashboard.html](file://public/admin-dashboard.html)
- [public/school-dashboard.html](file://public/school-dashboard.html)
- [public/teacher-portal.html](file://public/teacher-portal.html)
- [public/student-portal.html](file://public/student-portal.html)
- [public/assets/js/main.js](file://public/assets/js/main.js)
- [public/assets/js/school.js](file://public/assets/js/school.js)
- [public/assets/js/teacher.js](file://public/assets/js/teacher.js)
- [public/assets/js/student.js](file://public/assets/js/student.js)
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
EduFlow is a comprehensive Arabic-language school management system built with Python and Flask. It serves Arabic-speaking educational institutions by providing integrated solutions for student administration, grade tracking, academic year management, and multi-role dashboards. The platform supports four primary user roles—school admin, school portal, teacher portal, and student portal—each with dedicated workflows optimized for Arabic education systems.

The system emphasizes multi-school support, centralized academic year management, and an Arabic RTL (right-to-left) interface designed for native Arabic users. It leverages modern web technologies to deliver responsive, accessible, and secure educational workflows across administrative, teaching, and learning contexts.

## Project Structure
The project follows a clear separation of concerns with a backend API server, a frontend with role-specific portals, and shared utilities for authentication, database abstraction, and performance monitoring.

```mermaid
graph TB
subgraph "Frontend"
UI_Index["public/index.html<br/>Role Selection"]
UI_Admin["public/admin-dashboard.html<br/>Admin Dashboard"]
UI_School["public/school-dashboard.html<br/>School Dashboard"]
UI_Teacher["public/teacher-portal.html<br/>Teacher Portal"]
UI_Student["public/student-portal.html<br/>Student Portal"]
JS_Main["public/assets/js/main.js<br/>Shared Utilities"]
JS_School["public/assets/js/school.js<br/>School Logic"]
JS_Teacher["public/assets/js/teacher.js<br/>Teacher Logic"]
JS_Student["public/assets/js/student.js<br/>Student Logic"]
end
subgraph "Backend"
Server["server.py<br/>API Server"]
Auth["auth.py<br/>JWT & Auth Middleware"]
DB["database.py<br/>Database Abstraction"]
Requirements["requirements.txt<br/>Dependencies"]
end
UI_Index --> Server
UI_Admin --> Server
UI_School --> Server
UI_Teacher --> Server
UI_Student --> Server
JS_Main --> Server
JS_School --> Server
JS_Teacher --> Server
JS_Student --> Server
Server --> Auth
Server --> DB
Server --> Requirements
```

**Diagram sources**
- [server.py](file://server.py#L1-L800)
- [auth.py](file://auth.py#L1-L376)
- [database.py](file://database.py#L1-L726)
- [requirements.txt](file://requirements.txt#L1-L14)
- [public/index.html](file://public/index.html#L1-L345)
- [public/admin-dashboard.html](file://public/admin-dashboard.html#L1-L174)
- [public/school-dashboard.html](file://public/school-dashboard.html#L1-L800)
- [public/teacher-portal.html](file://public/teacher-portal.html#L1-L631)
- [public/student-portal.html](file://public/student-portal.html#L1-L800)
- [public/assets/js/main.js](file://public/assets/js/main.js#L1-L153)
- [public/assets/js/school.js](file://public/assets/js/school.js#L1-L800)
- [public/assets/js/teacher.js](file://public/assets/js/teacher.js#L1-L784)
- [public/assets/js/student.js](file://public/assets/js/student.js#L1-L800)

**Section sources**
- [README.md](file://README.md#L1-L23)
- [requirements.txt](file://requirements.txt#L1-L14)
- [server.py](file://server.py#L1-L800)

## Core Components
- **Multi-School Architecture**: Centralized academic year management with school-scoped entities (students, subjects, teachers) enabling independent operations across multiple institutions.
- **Arabic RTL Interface**: Fully localized Arabic UI with right-to-left layout, Arabic labels, and culturally appropriate educational workflows.
- **Multi-Role Dashboards**: Dedicated interfaces for administrators, school managers, teachers, and students with role-based access controls.
- **Grade Management**: Support for both 10-point scale (elementary grades 1-4) and 100-point scale (middle, secondary, preparatory), with intelligent threshold detection.
- **Academic Year Management**: Centralized academic year tracking with current year designation and historical data management.
- **Teacher Assignment System**: Subject-based teacher assignments with grade-level filtering and class management.
- **Student Records**: Comprehensive student profiles with detailed scores, daily attendance, and medical information.

**Section sources**
- [server.py](file://server.py#L52-L89)
- [database.py](file://database.py#L261-L320)
- [public/index.html](file://public/index.html#L2-L345)
- [public/admin-dashboard.html](file://public/admin-dashboard.html#L1-L174)
- [public/school-dashboard.html](file://public/school-dashboard.html#L1-L800)
- [public/teacher-portal.html](file://public/teacher-portal.html#L1-L631)
- [public/student-portal.html](file://public/student-portal.html#L1-L800)

## Architecture Overview
EduFlow employs a client-server architecture with a Flask-based API serving role-specific single-page applications. The system integrates JWT-based authentication, database abstraction supporting both MySQL and SQLite, and responsive frontend components optimized for Arabic education workflows.

```mermaid
sequenceDiagram
participant Client as "Client Browser"
participant Server as "Flask Server"
participant Auth as "Auth Middleware"
participant DB as "Database Layer"
Client->>Server : GET /api/admin/login
Server->>Auth : authenticate_token()
Auth-->>Server : Bypassed (no auth)
Server->>DB : Query users table
DB-->>Server : User record
Server-->>Client : JWT token + user data
Client->>Server : GET /api/schools
Server->>Auth : roles_required('admin')
Auth-->>Server : Allow all roles
Server->>DB : Query schools table
DB-->>Server : Schools list
Server-->>Client : JSON response
```

**Diagram sources**
- [server.py](file://server.py#L142-L200)
- [auth.py](file://auth.py#L91-L108)
- [database.py](file://database.py#L138-L157)

**Section sources**
- [server.py](file://server.py#L1-L800)
- [auth.py](file://auth.py#L1-L376)
- [database.py](file://database.py#L1-L726)

## Detailed Component Analysis

### Multi-School Support Architecture
EduFlow implements a hierarchical database schema supporting multiple schools with independent academic calendars and administrative boundaries.

```mermaid
erDiagram
USERS {
int id PK
string username UK
string password_hash
string role
timestamp created_at
}
SCHOOLS {
int id PK
string name
string code UK
string study_type
string level
string gender_type
timestamp created_at
timestamp updated_at
}
STUDENTS {
int id PK
int school_id FK
string full_name
string student_code UK
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
SUBJECTS {
int id PK
int school_id FK
string name
string grade_level
timestamp created_at
timestamp updated_at
}
TEACHERS {
int id PK
int school_id FK
string full_name
string teacher_code UK
string phone
string email
string password_hash
string grade_level
string specialization
text free_text_subjects
timestamp created_at
timestamp updated_at
}
SYSTEM_ACADEMIC_YEARS {
int id PK
string name UK
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
USERS ||--o{ SCHOOLS : "manages"
SCHOOLS ||--o{ STUDENTS : "enrolls"
SCHOOLS ||--o{ SUBJECTS : "offers"
SCHOOLS ||--o{ TEACHERS : "employs"
SCHOOLS ||--o{ STUDENT_GRADES : "assesses"
SCHOOLS ||--o{ STUDENT_ATTENDANCE : "monitors"
SYSTEM_ACADEMIC_YEARS ||--o{ STUDENT_GRADES : "tracks"
SYSTEM_ACADEMIC_YEARS ||--o{ STUDENT_ATTENDANCE : "records"
```

**Diagram sources**
- [database.py](file://database.py#L138-L320)

**Section sources**
- [database.py](file://database.py#L120-L320)
- [server.py](file://server.py#L306-L374)

### Arabic RTL Interface Implementation
The frontend implements a comprehensive Arabic localization with right-to-left layout, Arabic typography, and culturally appropriate educational workflows.

```mermaid
flowchart TD
Start(["Page Load"]) --> DetectLang["Detect Arabic Locale"]
DetectLang --> SetRTL["Set dir='rtl' on html"]
SetRTL --> LoadFonts["Load Cairo Font"]
LoadFonts --> ApplyStyles["Apply Arabic Stylesheets"]
ApplyStyles --> RenderUI["Render Role Cards"]
RenderUI --> HandleAuth["Handle Login/Logout"]
HandleAuth --> PersistState["Persist User State"]
PersistState --> End(["Ready"])
```

**Diagram sources**
- [public/index.html](file://public/index.html#L2-L345)
- [public/assets/js/main.js](file://public/assets/js/main.js#L1-L153)

**Section sources**
- [public/index.html](file://public/index.html#L1-L345)
- [public/assets/js/main.js](file://public/assets/js/main.js#L1-L153)

### Multi-Role Dashboard System
EduFlow provides distinct dashboards optimized for each stakeholder role within Arabic educational institutions.

```mermaid
classDiagram
class AdminDashboard {
+manageSchools()
+createAcademicYears()
+exportReports()
+viewAnalytics()
}
class SchoolDashboard {
+manageStudents()
+trackGrades()
+monitorAttendance()
+assignTeachers()
+generateReports()
}
class TeacherPortal {
+viewAssignedSubjects()
+manageStudentGrades()
+recordAttendance()
+viewRecommendations()
+generateReports()
}
class StudentPortal {
+viewPersonalGrades()
+checkAttendance()
+getRecommendations()
+viewAcademicReport()
}
AdminDashboard --> SchoolDashboard : "manages"
SchoolDashboard --> TeacherPortal : "assigns"
TeacherPortal --> StudentPortal : "teaches"
```

**Diagram sources**
- [public/admin-dashboard.html](file://public/admin-dashboard.html#L1-L174)
- [public/school-dashboard.html](file://public/school-dashboard.html#L1-L800)
- [public/teacher-portal.html](file://public/teacher-portal.html#L1-L631)
- [public/student-portal.html](file://public/student-portal.html#L1-L800)

**Section sources**
- [public/admin-dashboard.html](file://public/admin-dashboard.html#L1-L174)
- [public/school-dashboard.html](file://public/school-dashboard.html#L1-L800)
- [public/teacher-portal.html](file://public/teacher-portal.html#L1-L631)
- [public/student-portal.html](file://public/student-portal.html#L1-L800)

## Dependency Analysis
EduFlow leverages a modern Python stack with Flask as the web framework, supporting both MySQL and SQLite databases with automatic fallback capabilities.

```mermaid
graph LR
Flask["Flask 3.0.0"] --> Server["server.py"]
Flask_CORS["Flask-CORS 4.0.0"] --> Server
PyJWT["PyJWT 2.8.0"] --> Auth["auth.py"]
bcrypt["bcrypt 4.0.1"] --> Auth
python_dotenv["python-dotenv 1.0.0"] --> Server
mysql_connector["mysql-connector-python 8.0.33"] --> DB["database.py"]
werkzeug["werkzeug 3.0.1"] --> Server
bleach["bleach 6.1.0"] --> Server
MarkupSafe["MarkupSafe 2.1.3"] --> Server
psutil["psutil 5.9.6"] --> Server
qrcode["qrcode 7.4.2"] --> Server
pyotp["pyotp 2.9.0"] --> Server
redis["redis 5.0.1"] --> Server
```

**Diagram sources**
- [requirements.txt](file://requirements.txt#L1-L14)

**Section sources**
- [requirements.txt](file://requirements.txt#L1-L14)
- [server.py](file://server.py#L1-L800)
- [auth.py](file://auth.py#L1-L376)
- [database.py](file://database.py#L1-L726)

## Performance Considerations
- **Database Abstraction**: Automatic MySQL/SQLite fallback with connection pooling for optimal performance
- **Caching Layer**: Redis integration planned for session management and frequently accessed data
- **API Optimization**: Field selection and pagination support for large datasets
- **Static Asset Management**: CDN-ready CSS/JS assets with RTL optimization
- **Responsive Design**: Mobile-first approach ensuring performance across devices

## Troubleshooting Guide
Common issues and resolutions for EduFlow deployment and operation:

### Authentication Issues
- **Problem**: JWT token validation failures
- **Solution**: Verify JWT_SECRET environment variable and token expiration settings
- **Debug**: Check `/api/admin/login` endpoint response and token structure

### Database Connection Problems
- **Problem**: MySQL connection failures
- **Solution**: Automatic fallback to SQLite with school.db creation
- **Debug**: Monitor database initialization logs and connection pool status

### Academic Year Management
- **Problem**: Incorrect grade scale application
- **Solution**: Verify grade string format follows "Educational Level - Grade Level" pattern
- **Debug**: Use `is_elementary_grades_1_to_4()` helper function for validation

### Multi-School Operations
- **Problem**: Cross-school data leakage
- **Solution**: Ensure proper school_id scoping in all queries
- **Debug**: Validate role-based access controls and school boundary enforcement

**Section sources**
- [server.py](file://server.py#L110-L139)
- [database.py](file://database.py#L120-L127)
- [auth.py](file://auth.py#L339-L376)

## Conclusion
EduFlow represents a comprehensive solution for Arabic-speaking educational institutions, combining robust backend architecture with intuitive Arabic RTL interfaces. The system's multi-school support, centralized academic year management, and role-specific dashboards address the complex needs of modern educational administration while maintaining cultural and linguistic appropriateness.

Key strengths include:
- Seamless multi-school operations with independent academic calendars
- Intelligent grade scale detection supporting both 10-point and 100-point systems
- Comprehensive Arabic localization with RTL interface design
- Scalable architecture supporting both MySQL and SQLite deployments
- Professional-grade academic analytics and recommendation systems

The platform provides a solid foundation for educational institutions seeking digital transformation while preserving cultural and linguistic identity essential to effective Arabic education systems.