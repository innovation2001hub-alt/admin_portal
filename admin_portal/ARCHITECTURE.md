# Admin Portal - Architecture & Design Documentation

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend Application                    │
│                (React, Vue, Angular, etc.)                  │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP/REST
┌───────────────────────────▼─────────────────────────────────┐
│                   Django REST API                           │
│  (DRF ViewSets + Token Authentication)                      │
├───────────────────────────────────────────────────────────┬─┤
│ URLs Layer                                                │ │
│ ├── /api/auth/          (Authentication)                 │ │
│ ├── /api/units/         (Hierarchy Management)           │ │
│ ├── /api/users/         (User Management)                │ │
│ └── /api/approvals/     (Approval Workflow)              │ │
├───────────────────────────────────────────────────────────┤ │
│ Views Layer (ViewSets)                                     │ │
│ ├── auth_views.py       (Login, Logout, Password)        │ │
│ ├── unit_views.py       (CRUD + Hierarchy queries)       │ │
│ ├── user_views.py       (CRUD + Role assignment)         │ │
│ └── approval_views.py   (CRUD + Approve/Reject)          │ │
├───────────────────────────────────────────────────────────┤ │
│ Serializers Layer (Validation & Transformation)            │ │
│ ├── user_serializer.py                                   │ │
│ ├── role_serializer.py                                   │ │
│ ├── unit_serializer.py                                   │ │
│ └── approval_serializer.py                               │ │
├───────────────────────────────────────────────────────────┤ │
│ Services Layer (Business Logic)                            │ │
│ ├── auth_service.py     (Authentication logic)           │ │
│ ├── hierarchy_service.py(Hierarchy operations)           │ │
│ └── approval_service.py (Workflow logic)                 │ │
├───────────────────────────────────────────────────────────┤ │
│ Models Layer (Data Models)                                │ │
│ ├── User (AbstractUser)                                  │ │
│ ├── Unit (Hierarchy)                                     │ │
│ ├── Role (RBAC)                                          │ │
│ ├── ApprovalRequest (Workflow)                           │ │
│ └── AuditLog (Audit Trail)                               │ │
├───────────────────────────────────────────────────────────┤ │
│ Database Layer                                             │ │
│ └── SQLite (Development) / PostgreSQL (Production)        │ │
└───────────────────────────────────────────────────────────┴─┘
```

## Data Model Relationships

```
                              ┌─────────────┐
                              │   Unit      │
                              ├─────────────┤
                              │ id          │
                              │ name        │
                              │ code        │
                              │ unit_type   │
                              │ parent_id   │◄────┐
                              └──────┬──────┘     │
                                     │ (self-ref)│
                                     │           │
                    ┌────────────────┴───────────┘
                    │
        ┌───────────▼──────────┐
        │      User            │
        ├──────────────────────┤
        │ id                   │
        │ username             │
        │ employee_id          │
        │ designation          │
        │ unit_id (FK)────────►Unit
        │ roles (M2M)────────┐ │
        └──────────────────────┘ │
                                  │
                    ┌─────────────▼──────────┐
                    │      Role              │
                    ├────────────────────────┤
                    │ id                     │
                    │ name                   │
                    │ description            │
                    └────────────────────────┘

        ┌──────────────────────────────────┐
        │    ApprovalRequest               │
        ├──────────────────────────────────┤
        │ id                               │
        │ action_type                      │
        │ payload (JSON)                   │
        │ maker_id (FK)────────► User      │
        │ checker_id (FK)──────► User      │
        │ status                           │
        │ comments                         │
        └──────────────────────────────────┘

        ┌──────────────────────────────────┐
        │    AuditLog                      │
        ├──────────────────────────────────┤
        │ id                               │
        │ user_id (FK)──────────► User     │
        │ action                           │
        │ action_type                      │
        │ metadata (JSON)                  │
        │ ip_address                       │
        │ created_at                       │
        └──────────────────────────────────┘
```

## Request Flow Diagram

### Authentication Flow
```
┌──────────────┐
│  User Login  │
│  Request     │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│   LoginView          │
│   (ViewSet)          │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│   AuthService        │
│ - authenticate_user()│
│ - generate_token()   │
│ - audit log          │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│   User Model         │
│   (check password)   │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│   Token Created      │
│   Response           │
└──────────────────────┘
```

### Create User Flow
```
┌──────────────────┐
│  CreateUser API  │
│  Request         │
└────────┬─────────┘
         │ (Token auth)
         ▼
┌──────────────────────┐
│   UserViewSet        │
│   (validate perms)   │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│   UserSerializer     │
│   (validate data)    │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│   User Model         │
│   (create instance)  │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│   AuditLog           │
│   (log creation)     │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│   Success Response   │
└──────────────────────┘
```

### Approval Workflow Flow
```
┌─────────────────┐
│  Create Approval│
│  Request        │
└────────┬────────┘
         │
         ▼
┌──────────────────────────┐
│   ApprovalViewSet        │
│   perform_create()       │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│   ApprovalService        │
│   route_approval()       │
│ - Determine checker      │
│ - Route based on:        │
│   * Action type          │
│   * Hierarchy level      │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│   HierarchyService       │
│   - Get superior unit    │
│   - Find checker         │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│   ApprovalRequest        │
│   (assigned to checker)  │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│   AuditLog               │
│   (log approval created) │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│   Approval Assigned to   │
│   Checker for Review     │
└──────────────────────────┘
```

## Key Design Decisions

### 1. Service Layer Pattern
**Decision**: Implement business logic in services, not views
**Reason**: 
- Reusability across different endpoints
- Easier testing
- Clear separation of concerns
- RBAC and hierarchy checks in one place

**Example**: `HierarchyService.can_manage_unit()` used by multiple views

### 2. Hierarchy-based Permissions
**Decision**: All access control based on organizational hierarchy
**Reason**:
- Scalable to any organization size
- Natural fit for hierarchical structures
- Users can only manage their own unit + subordinates
- Approval routing automatic based on hierarchy

**Example**: Manager can only create users in their unit and child units

### 3. Maker-Checker Workflow
**Decision**: Separate `maker` and `checker` roles
**Reason**:
- Implements segregation of duties (SoD)
- Audit trail for all changes
- Configurable approval routing
- Handles complex approval chains

**Example**: New user creation routed to immediate superior for approval

### 4. Audit Logging
**Decision**: Log all actions at service layer
**Reason**:
- Captures complete audit trail
- Includes metadata (IPs, request data)
- Facilitates compliance reporting
- Enables actionable analytics

**Example**: Every create/update/delete/approve logged with user and timestamp

### 5. Token Authentication
**Decision**: Use DRF Token auth, not JWT
**Reason**:
- Simpler to implement and maintain
- Built-in token management
- Database-backed (not stateless)
- Easier to revoke tokens

**Example**: POST /auth/login/ returns token used for all requests

### 6. Soft Deletes for Users
**Decision**: Deactivate users instead of hard delete
**Reason**:
- Preserves audit trail integrity
- Allows user reactivation
- Maintains data consistency
- Follows best practices

**Example**: DELETE /users/{id}/ sets is_active=False

## Authentication & Authorization Flow

```
┌─────────────────────────────────────────────────────────┐
│                   API Request                            │
└────────────────────┬────────────────────────────────────┘
                     │ Token in header
                     ▼
        ┌────────────────────────────┐
        │  Token Authentication      │
        │  (DRF TokenAuthentication) │
        │  - Get user from token     │
        │  - Validate token exists   │
        └────────┬───────────────────┘
                 │
        ┌────────▼────────────────────┐
        │  IsAuthenticated Check      │
        │  (Default permission class) │
        └────────┬───────────────────┘
                 │
        ┌────────▼────────────────────┐
        │  Business Logic             │
        │  (in service/view)          │
        │  - Can manage unit?         │
        │  - Can access resource?     │
        │  - Has correct role?        │
        └────────┬───────────────────┘
                 │
        ┌────────▼────────────────────┐
        │  Audit Log Entry            │
        │  - User info                │
        │  - Action performed         │
        │  - Timestamp & IP           │
        └────────┬───────────────────┘
                 │
                 ▼
        ┌────────────────────────────┐
        │  Response (Success/Error)  │
        └────────────────────────────┘
```

## Error Handling Strategy

```
API Request
    │
    ├─► Serialization Error (400)
    │   └─ Validation failed
    │
    ├─► Authentication Error (401)
    │   └─ Missing/invalid token
    │
    ├─► Permission Error (403)
    │   └─ User not authorized
    │
    ├─► Not Found Error (404)
    │   └─ Resource doesn't exist
    │
    ├─► Business Logic Error (400)
    │   └─ Cannot approve (not pending)
    │   └─ Cannot set descendant as parent
    │   └─ Employee ID already exists
    │
    └─► Server Error (500)
        └─ Unexpected exception
```

## Performance Considerations

### Query Optimization
```python
# Use select_related for ForeignKeys
users = User.objects.select_related('unit').prefetch_related('roles')

# Use prefetch_related for reverse relations
units = Unit.objects.prefetch_related('users', 'children')

# Use only/defer for large tables
users = User.objects.only('id', 'username', 'email')
```

### Caching Strategy (Future Enhancement)
```python
# Cache user's unit hierarchy
cache.set(f'user_hierarchy_{user.id}', unit_chain, timeout=3600)

# Cache role permissions
cache.set(f'user_roles_{user.id}', roles, timeout=3600)

# Cache approval statistics
cache.set(f'approval_stats_{user.id}', stats, timeout=300)
```

### Pagination
- Default page size: 20 items
- Configurable via settings
- Implemented for all list endpoints

### Filtering & Search
- Uses django-filter package
- Field-based filtering (unit, is_active, etc.)
- Full-text search on multiple fields
- Configurable per ViewSet

## Security Implementation

### Authentication
- Token-based (not session-based for API)
- Tokens created on login, deleted on logout
- 40-character random token
- Can have expiry (future enhancement)

### Authorization
- User model checks (is_active, not deleted)
- Hierarchy-based RBAC
- Subordinate-only access
- Role-based features (future enhancement)

### Data Protection
- Password hashing (PBKDF2)
- SQL injection prevention (ORM)
- CSRF protection disabled for API (token-based)
- CORS properly configured
- No sensitive data in logs

### Audit Trail
- All actions logged
- User and IP captured
- Request metadata stored
- Immutable logs (no edit/delete)
- Time-series capable

## Deployment Architecture

### Development
```
Django Development Server
    └─ SQLite Database
    └─ Local File Storage
    └─ Console Logging
```

### Production
```
Reverse Proxy (Nginx)
    │
    ▼
WSGI Application Server (Gunicorn)
    │
    ├─ Django Application
    │
    ├─ PostgreSQL/Oracle Database
    │
    └─ Elasticsearch (optional, for audit search)

External Services:
    ├─ Email (SMTP)
    ├─ Monitoring (Sentry)
    ├─ Logging (ELK Stack)
    └─ Storage (S3)
```

## Scalability Considerations

### Horizontal Scaling
- Stateless API (tokens in DB, not memory)
- Database as single source of truth
- Load balancer friendly
- No session affinity required

### Vertical Scaling
- Database query optimization
- Caching layer (Redis)
- Async tasks (Celery for approvals)
- Background jobs for reports

### Database Optimization
- Indexing on frequently queried fields
- Partitioning by date for audit logs
- Archiving old approval records
- Query analysis and tuning

## Future Enhancements

1. **JWT Authentication**: Replace Token with JWT for stateless auth
2. **API Versioning**: v1/, v2/ for backward compatibility
3. **Async Tasks**: Celery for email notifications
4. **WebSocket Support**: Real-time notifications
5. **API Rate Limiting**: Prevent abuse
6. **Advanced Reporting**: Audit analytics dashboard
7. **Two-Factor Authentication**: Enhanced security
8. **API Documentation**: OpenAPI/Swagger spec
9. **Caching Layer**: Redis for performance
10. **Microservices**: Separate services per domain

---

Last Updated: 2025-01-08
