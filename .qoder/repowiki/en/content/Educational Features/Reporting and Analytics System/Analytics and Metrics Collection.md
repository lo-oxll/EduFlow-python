# Analytics and Metrics Collection

<cite>
**Referenced Files in This Document**
- [README.md](file://README.md)
- [performance.py](file://performance.py)
- [services.py](file://services.py)
- [database.py](file://database.py)
- [cache.py](file://cache.py)
- [server.py](file://server.py)
- [edufloiw_logging.py](file://edufloiw_logging.py)
- [public/admin-dashboard.html](file://public/admin-dashboard.html)
- [public/assets/js/admin.js](file://public/assets/js/admin.js)
- [public/assets/js/main.js](file://public/assets/js/main.js)
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
10. [Appendices](#appendices)

## Introduction
This document describes the analytics and metrics collection system for the EduFlow school management platform. It explains how educational metrics are tracked (student performance indicators, class effectiveness, and program outcomes), how real-time monitoring captures system performance and user activity, and how data aggregation and statistical analysis are implemented. Administrative analytics features for decision support, resource allocation insights, and benchmarking are documented alongside practical examples of metric calculation workflows, data export capabilities, and guidance for extending analytics with custom integrations and privacy safeguards.

## Project Structure
The analytics system spans backend services, performance monitoring, caching, and frontend dashboards:
- Backend services encapsulate business logic and analytics computations
- Performance monitoring tracks request latency, endpoint statistics, and system resources
- Caching accelerates repeated analytics queries
- Logging centralizes error and performance telemetry
- Frontend dashboards present aggregated metrics and enable exports

```mermaid
graph TB
subgraph "Frontend"
AdminUI["Admin Dashboard<br/>admin-dashboard.html"]
AdminJS["Admin JS<br/>assets/js/admin.js"]
MainJS["Main Utilities<br/>assets/js/main.js"]
end
subgraph "Backend"
Server["Flask Server<br/>server.py"]
Services["Services Layer<br/>services.py"]
PerfMon["Performance Monitor<br/>performance.py"]
Cache["Cache Manager<br/>cache.py"]
DB["Database Abstraction<br/>database.py"]
Logger["Error Logger<br/>edufloiw_logging.py"]
end
AdminUI --> AdminJS
AdminJS --> Server
MainJS --> AdminUI
Server --> Services
Server --> PerfMon
Server --> Cache
Server --> DB
Services --> DB
Services --> Cache
PerfMon --> Server
Logger --> Server
```

**Diagram sources**
- [server.py](file://server.py#L1-L120)
- [performance.py](file://performance.py#L15-L108)
- [services.py](file://services.py#L1-L43)
- [cache.py](file://cache.py#L14-L50)
- [database.py](file://database.py#L88-L118)
- [edufloiw_logging.py](file://edufloiw_logging.py#L21-L80)
- [public/admin-dashboard.html](file://public/admin-dashboard.html#L1-L174)
- [public/assets/js/admin.js](file://public/assets/js/admin.js#L1-L120)
- [public/assets/js/main.js](file://public/assets/js/main.js#L1-L153)

**Section sources**
- [README.md](file://README.md#L1-L23)
- [server.py](file://server.py#L1-L120)

## Core Components
- PerformanceMonitor: Tracks request durations, endpoint statistics, slow endpoints, and system metrics; exposes REST endpoints for performance insights
- RecommendationService: Computes educational metrics including subject/class performance, pass rates, at-risk students, and personalized recommendations
- CacheManager: Provides Redis-backed caching with in-memory fallback and cache invalidation patterns
- Database abstraction: Manages MySQL/SQLite connections and creates normalized tables for students, teachers, subjects, academic years, and analytics data
- ErrorLogger: Centralized logging with categories, performance thresholds, and structured entries
- Frontend dashboards: Admin dashboard with export capabilities and interactive analytics displays

**Section sources**
- [performance.py](file://performance.py#L15-L144)
- [services.py](file://services.py#L367-L858)
- [cache.py](file://cache.py#L234-L275)
- [database.py](file://database.py#L120-L338)
- [edufloiw_logging.py](file://edufloiw_logging.py#L21-L143)
- [public/admin-dashboard.html](file://public/admin-dashboard.html#L100-L174)

## Architecture Overview
The system integrates analytics across three layers:
- Data ingestion and storage: Students’ detailed scores and attendance stored as JSON fields; normalized relational tables for subjects, teachers, and academic years
- Analytics computation: Services layer performs aggregations and statistical analysis
- Observability and presentation: PerformanceMonitor and ErrorLogger feed real-time dashboards and exportable reports

```mermaid
sequenceDiagram
participant Browser as "Browser"
participant AdminJS as "Admin JS<br/>admin.js"
participant Server as "Server<br/>server.py"
participant Services as "Services<br/>services.py"
participant Cache as "Cache<br/>cache.py"
participant DB as "Database<br/>database.py"
Browser->>AdminJS : User opens Admin Dashboard
AdminJS->>Server : GET /api/schools
Server->>Services : Retrieve schools
Services->>Cache : Check cache
alt Cache hit
Cache-->>Services : Cached data
else Cache miss
Services->>DB : Execute query
DB-->>Services : Rows
Services->>Cache : Store result
end
Services-->>Server : Schools list
Server-->>AdminJS : JSON response
AdminJS-->>Browser : Render dashboard
```

**Diagram sources**
- [public/admin-dashboard.html](file://public/admin-dashboard.html#L1-L174)
- [public/assets/js/admin.js](file://public/assets/js/admin.js#L64-L102)
- [server.py](file://server.py#L306-L321)
- [services.py](file://services.py#L44-L55)
- [cache.py](file://cache.py#L102-L128)
- [database.py](file://database.py#L128-L137)

## Detailed Component Analysis

### Performance Monitoring System
The PerformanceMonitor captures request timing, endpoint performance, and system resource usage. It maintains:
- Request time history with endpoint, method, status code, and timestamps
- Endpoint statistics (count, total time, average, min, max)
- Slow endpoint detection (>1s average)
- System metrics (CPU, memory, active requests, thread count)
- Performance endpoints for external monitoring

```mermaid
classDiagram
class PerformanceMonitor {
+init_app(app)
+before_request()
+after_request(response)
+teardown_request(exception)
+record_db_query(query_time, query)
+get_system_metrics() Dict
+get_performance_stats() Dict
+get_endpoint_details(endpoint) Dict
}
class DatabasePerformanceTracker {
+__enter__()
+__exit__(exc_type, exc_val, exc_tb)
+set_query(query)
}
PerformanceMonitor --> DatabasePerformanceTracker : "records"
```

**Diagram sources**
- [performance.py](file://performance.py#L15-L183)

**Section sources**
- [performance.py](file://performance.py#L15-L144)
- [performance.py](file://performance.py#L215-L234)

### Educational Metrics and Recommendations
The RecommendationService computes:
- Subject-level performance: counts, averages, pass rates, excellent/good/needs-support distributions
- Class-level insights: overall averages, pass rates, subjects needing focus, at-risk students
- Personalized student analysis: overall averages, strong/weak subjects, performance level, messaging
- Strategies and suggestions: targeted actions based on performance gaps

```mermaid
flowchart TD
Start(["Start Analysis"]) --> LoadScores["Load detailed_scores JSON"]
LoadScores --> ComputeAvg["Compute subject averages"]
ComputeAvg --> ClassInsights["Aggregate class-level metrics"]
ClassInsights --> IdentifyWeak["Identify weak subjects and at-risk students"]
IdentifyWeak --> GenerateStrategies["Generate actionable strategies"]
GenerateStrategies --> Output["Return analysis report"]
```

**Diagram sources**
- [services.py](file://services.py#L476-L765)

**Section sources**
- [services.py](file://services.py#L367-L858)

### Data Aggregation Pipelines
Aggregation relies on:
- Relational normalization: students, teachers, subjects, academic years, and many-to-many relationships
- JSON fields for flexible scoring and attendance storage
- Caching for repeated analytics queries
- Batch operations for bulk grade level creation

```mermaid
erDiagram
STUDENTS {
int id PK
int school_id FK
varchar full_name
varchar student_code UK
varchar grade
varchar room
text detailed_scores
text daily_attendance
}
SUBJECTS {
int id PK
int school_id FK
varchar name
varchar grade_level
}
TEACHERS {
int id PK
int school_id FK
varchar full_name
varchar teacher_code UK
varchar phone
varchar email
text free_text_subjects
}
TEACHER_SUBJECTS {
int id PK
int teacher_id FK
int subject_id FK
}
STUDENT_GRADES {
int id PK
int student_id FK
int academic_year_id FK
varchar subject_name
int month1
int month2
int midterm
int month3
int month4
int final
}
STUDENT_ATTENDANCE {
int id PK
int student_id FK
int academic_year_id FK
date attendance_date
varchar status
text notes
}
STUDENTS ||--o{ STUDENT_GRADES : "has"
STUDENTS ||--o{ STUDENT_ATTENDANCE : "has"
SUBJECTS ||--o{ TEACHER_SUBJECTS : "assigned_to"
TEACHERS ||--o{ TEACHER_SUBJECTS : "assigns"
```

**Diagram sources**
- [database.py](file://database.py#L159-L320)

**Section sources**
- [database.py](file://database.py#L120-L338)
- [server.py](file://server.py#L469-L559)

### Real-Time Monitoring and User Activity Tracking
Real-time monitoring includes:
- Request tracing with request IDs and response times
- Endpoint performance dashboards
- System resource usage (CPU/memory/threads)
- Slow endpoint identification
- Audit logging for administrative actions

```mermaid
sequenceDiagram
participant Client as "Client"
participant Server as "Server"
participant Perf as "PerformanceMonitor"
participant DB as "Database"
Client->>Server : HTTP Request
Server->>Perf : before_request()
Server->>DB : Execute query
DB-->>Server : Result
Server->>Perf : after_request(response)
Perf-->>Server : Stats & headers
Server-->>Client : Response with X-Response-Time/X-Request-ID
```

**Diagram sources**
- [performance.py](file://performance.py#L41-L77)
- [server.py](file://server.py#L1-L42)

**Section sources**
- [performance.py](file://performance.py#L15-L144)
- [edufloiw_logging.py](file://edufloiw_logging.py#L213-L242)

### Administrative Analytics and Decision Support
Administrative features include:
- Centralized academic year management applied across all schools
- Export of school lists to Excel via SheetJS
- Interactive dashboards for performance summaries and year management
- Bulk grade level creation templates

```mermaid
sequenceDiagram
participant Admin as "Admin"
participant UI as "Admin Dashboard"
participant JS as "admin.js"
participant API as "server.py"
participant DB as "database.py"
Admin->>UI : Click "Export Schools"
UI->>JS : exportSchoolsToExcel()
JS->>API : GET /api/schools
API->>DB : SELECT schools
DB-->>API : Rows
API-->>JS : JSON
JS-->>UI : Generate Excel and download
```

**Diagram sources**
- [public/admin-dashboard.html](file://public/admin-dashboard.html#L100-L174)
- [public/assets/js/admin.js](file://public/assets/js/admin.js#L318-L349)
- [server.py](file://server.py#L306-L321)

**Section sources**
- [public/admin-dashboard.html](file://public/admin-dashboard.html#L1-L174)
- [public/assets/js/admin.js](file://public/assets/js/admin.js#L318-L349)
- [server.py](file://server.py#L306-L321)

### Data Export Capabilities
- Excel export of school lists using SheetJS
- Structured column mapping and workbook creation
- Notification feedback for export operations

**Section sources**
- [public/assets/js/admin.js](file://public/assets/js/admin.js#L318-L349)
- [public/admin-dashboard.html](file://public/admin-dashboard.html#L100-L104)

### Custom Analytics Development
Guidance for extending analytics:
- Use RecommendationService patterns for new metrics
- Apply CacheManager decorators for performance-sensitive queries
- Integrate DatabasePerformanceTracker for query-level timing
- Leverage ErrorLogger for structured telemetry and performance thresholds
- Add new endpoints in server.py following existing patterns

**Section sources**
- [services.py](file://services.py#L12-L43)
- [cache.py](file://cache.py#L170-L211)
- [performance.py](file://performance.py#L167-L183)
- [edufloiw_logging.py](file://edufloiw_logging.py#L300-L352)
- [server.py](file://server.py#L141-L200)

## Dependency Analysis
The analytics system exhibits low coupling and high cohesion:
- Services depend on database abstractions and cache manager
- PerformanceMonitor is integrated into Flask lifecycle hooks
- Frontend communicates with backend via REST endpoints
- Logging and caching are cross-cutting concerns

```mermaid
graph LR
AdminUI["admin-dashboard.html"] --> AdminJS["admin.js"]
AdminJS --> Server["server.py"]
Server --> Services["services.py"]
Server --> Perf["performance.py"]
Server --> Cache["cache.py"]
Server --> DB["database.py"]
Services --> DB
Services --> Cache
Perf --> Server
Logger["edufloiw_logging.py"] --> Server
```

**Diagram sources**
- [server.py](file://server.py#L1-L42)
- [services.py](file://services.py#L1-L43)
- [performance.py](file://performance.py#L15-L35)
- [cache.py](file://cache.py#L234-L275)
- [database.py](file://database.py#L88-L118)
- [edufloiw_logging.py](file://edufloiw_logging.py#L268-L298)
- [public/admin-dashboard.html](file://public/admin-dashboard.html#L1-L174)
- [public/assets/js/admin.js](file://public/assets/js/admin.js#L1-L120)

**Section sources**
- [server.py](file://server.py#L1-L42)
- [services.py](file://services.py#L1-L43)
- [performance.py](file://performance.py#L15-L35)
- [cache.py](file://cache.py#L234-L275)
- [database.py](file://database.py#L88-L118)
- [edufloiw_logging.py](file://edufloiw_logging.py#L268-L298)

## Performance Considerations
- Use CacheManager decorators to cache expensive analytics queries
- Prefer batch operations for bulk updates (e.g., bulk grade levels)
- Monitor slow endpoints and optimize hotspots using PerformanceMonitor
- Apply DatabasePerformanceTracker around long-running queries
- Ensure JSON fields are indexed appropriately for filtering and sorting

[No sources needed since this section provides general guidance]

## Troubleshooting Guide
Common issues and resolutions:
- Performance degradation: Review slow endpoints and system metrics; adjust caching TTLs; profile queries
- Missing or malformed analytics data: Validate JSON fields (detailed_scores, daily_attendance) and normalize where needed
- Cache connectivity failures: Confirm Redis availability; fallback to in-memory cache is automatic
- Logging and monitoring: Use ErrorLogger categories and performance thresholds to pinpoint issues

**Section sources**
- [performance.py](file://performance.py#L110-L144)
- [edufloiw_logging.py](file://edufloiw_logging.py#L213-L242)
- [cache.py](file://cache.py#L29-L48)

## Conclusion
The EduFlow analytics and metrics system combines robust performance monitoring, relational modeling with flexible JSON fields, and a caching layer to deliver real-time insights for educational and administrative decision-making. The RecommendationService provides actionable analytics for educators, while the admin dashboard enables efficient data export and centralized academic year management. With structured logging and performance telemetry, the platform supports continuous optimization and reliable operations.

[No sources needed since this section summarizes without analyzing specific files]

## Appendices

### Example Metric Calculation Workflows
- Subject performance: Aggregate monthly and midterm scores per subject; compute averages and pass rates
- Class effectiveness: Combine subject metrics to derive class averages and identify focus areas
- Individual student insights: Compare subject averages, detect trends, and generate personalized messages
- Export pipeline: Fetch data via REST, transform to spreadsheet-ready arrays, and write Excel files

**Section sources**
- [services.py](file://services.py#L476-L765)
- [public/assets/js/admin.js](file://public/assets/js/admin.js#L318-L349)

### Integration with External Platforms
- Use performance endpoints for external monitoring dashboards
- Export analytics data for third-party BI tools
- Respect data privacy by avoiding PII in logs and ensuring secure transport

**Section sources**
- [performance.py](file://performance.py#L215-L234)
- [edufloiw_logging.py](file://edufloiw_logging.py#L268-L298)

### Data Privacy Considerations
- Avoid logging sensitive personal data; sanitize inputs and apply rate limiting
- Use HTTPS and secure tokens for authentication
- Apply least-privilege access controls and audit administrative actions

**Section sources**
- [server.py](file://server.py#L91-L108)
- [edufloiw_logging.py](file://edufloiw_logging.py#L186-L211)