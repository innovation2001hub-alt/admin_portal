# Admin Portal Backend

A comprehensive Django REST Framework-based Admin Portal backend implementing organizational hierarchy management, role-based access control (RBAC), and a Maker-Checker approval workflow.

## Features

- **Custom User Model**: Extends Django's AbstractUser with employee information, unit assignment, and role management
- **Organizational Hierarchy**: Self-referencing Unit model supporting unlimited hierarchy levels (HO, CIRCLE, NETWORK, AO, RBO, BRANCH)
- **Role-Based Access Control (RBAC)**: Flexible role system with user-role assignments
- **Maker-Checker Workflow**: Implements approval routing based on organizational hierarchy
- **Audit Logging**: Comprehensive audit trail for all user actions
- **REST API**: Full-featured REST API with DRF ViewSets and serializers
- **Authentication**: Token-based authentication with Django REST Framework
- **Filtering & Search**: Advanced filtering, searching, and ordering capabilities

## Project Structure

```
admin_portal/
├── admin_core/                 # Main application
│   ├── models/                 # Data models
│   │   ├── user.py            # Custom User model
│   │   ├── role.py            # Role model
│   │   ├── hierarchy.py        # Unit/Hierarchy model
│   │   ├── workflow.py         # ApprovalRequest model
│   │   ├── audit.py            # AuditLog model
│   │   └── __init__.py         # Model imports
│   ├── serializers/            # DRF Serializers
│   │   ├── user_serializer.py
│   │   ├── role_serializer.py
│   │   ├── unit_serializer.py
│   │   ├── approval_serializer.py
│   │   └── __init__.py
│   ├── services/               # Business logic services
│   │   ├── auth_service.py     # Authentication logic
│   │   ├── hierarchy_service.py # Hierarchy operations
│   │   ├── approval_service.py  # Approval workflow logic
│   ├── views/                  # API ViewSets
│   │   ├── auth_views.py       # Authentication endpoints
│   │   ├── unit_views.py       # Unit management endpoints
│   │   ├── user_views.py       # User management endpoints
│   │   ├── approval_views.py   # Approval workflow endpoints
│   ├── management/             # Django management commands
│   │   └── commands/
│   │       └── seed_data.py    # Initial data seeding
│   ├── admin.py                # Django admin configuration
│   ├── urls.py                 # App URL configuration
│   ├── apps.py
│   ├── tests.py
│   └── migrations/
├── admin_portal/               # Project settings
│   ├── settings.py             # Django settings
│   ├── urls.py                 # Main URL configuration
│   ├── asgi.py
│   ├── wsgi.py
├── manage.py
├── requirements.txt
├── README.md
└── db.sqlite3
```

## Installation & Setup

### Prerequisites

- Python 3.8+
- pip

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Run Migrations

```bash
python manage.py migrate
```

### Step 3: Create Superuser

```bash
python manage.py createsuperuser
```

### Step 4: Seed Initial Data (Optional)

```bash
python manage.py seed_data
```

This creates:
- 5 default roles (ADMIN, MANAGER, MAKER, CHECKER, VIEWER)
- Sample organizational hierarchy
- Sample users with different roles

### Step 5: Run Development Server

```bash
python manage.py runserver
```

Server will be available at `http://localhost:8000`

## API Documentation

### Authentication

#### Login
```
POST /api/auth/login/
Content-Type: application/json

{
    "username": "admin",
    "password": "AdminPortal@123"
}

Response:
{
    "token": "abc123...",
    "user": {...},
    "message": "Login successful."
}
```

#### Logout
```
POST /api/auth/logout/
Authorization: Token abc123...

Response:
{
    "message": "Logout successful."
}
```

#### Change Password
```
POST /api/auth/change-password/
Authorization: Token abc123...
Content-Type: application/json

{
    "old_password": "old_pass",
    "new_password": "new_pass",
    "new_password_confirm": "new_pass"
}
```

#### Get Current User
```
GET /api/auth/current-user/
Authorization: Token abc123...
```

### Unit Management

#### List Units
```
GET /api/units/
Authorization: Token abc123...

Query Parameters:
- unit_type: Filter by type (HO, CIRCLE, NETWORK, AO, RBO, BR)
- parent: Filter by parent unit ID
- search: Search by name or code
- ordering: Order by (name, code, created_at)
- page: Page number (default: 1)
```

#### Create Unit
```
POST /api/units/
Authorization: Token abc123...
Content-Type: application/json

{
    "name": "Circle 1",
    "code": "CIRCLE001",
    "unit_type": "CIRCLE",
    "parent": null  # or parent unit ID
}
```

#### Get Unit Details
```
GET /api/units/{id}/
Authorization: Token abc123...
```

#### Update Unit
```
PUT /api/units/{id}/
Authorization: Token abc123...
```

#### Delete Unit
```
DELETE /api/units/{id}/
Authorization: Token abc123...
```

#### Get Parent Chain (Hierarchy)
```
GET /api/units/{id}/parent-chain/
Authorization: Token abc123...

Response: List of parent units from current to HO
```

#### Get Child Units
```
GET /api/units/{id}/children/
Authorization: Token abc123...

Response: Direct child units only
```

#### Get All Descendants
```
GET /api/units/{id}/all-children/
Authorization: Token abc123...

Response: All descendant units (recursive)
```

#### Get Users in Unit
```
GET /api/units/{id}/users/
Authorization: Token abc123...

Response: All users in the unit and subordinate units
```

#### Get Unit Statistics
```
GET /api/units/{id}/statistics/
Authorization: Token abc123...

Response: Statistics including user count, children count, etc.
```

### User Management

#### List Users
```
GET /api/users/
Authorization: Token abc123...

Query Parameters:
- unit: Filter by unit ID
- is_active: Filter by active status (true/false)
- search: Search by username, email, name, employee_id
- ordering: Order by (username, first_name, last_name, created_at)
```

#### Create User
```
POST /api/users/
Authorization: Token abc123...
Content-Type: application/json

{
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "employee_id": "EMP004",
    "designation": "Senior Officer",
    "unit_id": 1,
    "role_ids": [1, 2],
    "password": "SecurePass@123",
    "password_confirm": "SecurePass@123"
}
```

#### Get User Details
```
GET /api/users/{id}/
Authorization: Token abc123...
```

#### Update User
```
PUT /api/users/{id}/
Authorization: Token abc123...
```

#### Delete User (Soft Delete)
```
DELETE /api/users/{id}/
Authorization: Token abc123...

Note: Sets is_active to False
```

#### Assign Roles to User
```
POST /api/users/{id}/assign-roles/
Authorization: Token abc123...
Content-Type: application/json

{
    "role_ids": [1, 2, 3]
}
```

#### Get User Roles
```
GET /api/users/{id}/roles/
Authorization: Token abc123...
```

#### Get Users by Unit
```
GET /api/users/by-unit/?unit_id=1
Authorization: Token abc123...
```

#### Get Users in Unit Hierarchy
```
GET /api/users/in-hierarchy/?unit_id=1
Authorization: Token abc123...
```

#### Activate User
```
POST /api/users/{id}/activate/
Authorization: Token abc123...
```

#### Deactivate User
```
POST /api/users/{id}/deactivate/
Authorization: Token abc123...
```

### Approval Requests (Maker-Checker Workflow)

#### List Approval Requests
```
GET /api/approvals/
Authorization: Token abc123...

Query Parameters:
- status: Filter by status (PENDING, APPROVED, REJECTED)
- action_type: Filter by action type
- maker: Filter by maker user ID
- checker: Filter by checker user ID
```

#### Create Approval Request
```
POST /api/approvals/
Authorization: Token abc123...
Content-Type: application/json

{
    "action_type": "CREATE_USER",
    "payload": {
        "username": "new_user",
        "email": "new@example.com",
        "first_name": "New",
        "last_name": "User"
    }
}

Note: Automatically routes to appropriate checker based on hierarchy
```

#### Get Approval Details
```
GET /api/approvals/{id}/
Authorization: Token abc123...
```

#### Approve Request
```
POST /api/approvals/{id}/approve/
Authorization: Token abc123...
Content-Type: application/json

{
    "comments": "Approved as requested"  # optional
}
```

#### Reject Request
```
POST /api/approvals/{id}/reject/
Authorization: Token abc123...
Content-Type: application/json

{
    "comments": "Requires more information"  # optional
}
```

#### Get Pending Approvals
```
GET /api/approvals/pending/
Authorization: Token abc123...

Returns: Approvals assigned to current user that are still pending
```

#### Get Approval Statistics
```
GET /api/approvals/statistics/
Authorization: Token abc123...

Returns: Count of approvals created, pending, approved, and rejected by current user
```

#### Get Approvals Created by Me
```
GET /api/approvals/created-by-me/
Authorization: Token abc123...
```

#### Get Approvals Assigned to Me
```
GET /api/approvals/assigned-to-me/
Authorization: Token abc123...
```

## Models

### User
Extends Django's AbstractUser with:
- `employee_id` (CharField, unique)
- `designation` (CharField)
- `unit` (ForeignKey to Unit)
- `roles` (ManyToMany to Role)

### Unit
Organizational hierarchy model:
- `name` (CharField)
- `code` (CharField, unique)
- `unit_type` (Choice: HO, CIRCLE, NETWORK, AO, RBO, BRANCH)
- `parent` (Self-referencing ForeignKey)

Helper methods:
- `get_parent_chain()`: Get all parent units up to HO
- `get_all_children()`: Get all descendant units recursively
- `get_root_unit()`: Get the Head Office unit
- `is_descendant_of(unit)`: Check if unit is descendant of another

### Role
Role-based access control:
- `name` (CharField, unique)
- `description` (TextField)

### ApprovalRequest
Maker-Checker workflow:
- `action_type` (CharField)
- `payload` (JSONField)
- `maker` (ForeignKey to User)
- `checker` (ForeignKey to User)
- `status` (Choice: PENDING, APPROVED, REJECTED)
- `comments` (TextField)

Methods:
- `approve(comments)`: Mark as approved
- `reject(comments)`: Mark as rejected
- `is_pending()`: Check if pending

### AuditLog
Audit trail:
- `user` (ForeignKey to User)
- `action` (CharField)
- `action_type` (Choice: CREATE, UPDATE, DELETE, APPROVE, REJECT, LOGIN, LOGOUT, VIEW, EXPORT)
- `metadata` (JSONField)
- `ip_address` (GenericIPAddressField)

## Services

### AuthService
Authentication and authorization:
- `authenticate_user(username, password, ip_address)`: Authenticate user
- `generate_token(user)`: Generate/retrieve token
- `logout_user(user, ip_address)`: Invalidate token
- `change_password(user, old_password, new_password)`: Change password

### HierarchyService
Organizational hierarchy operations:
- `get_subordinate_units(unit)`: Get all child units
- `get_superior_units(unit)`: Get all parent units
- `can_access_unit(user, unit)`: Check access permission
- `can_manage_unit(user, unit)`: Check management permission
- `get_users_in_hierarchy(unit)`: Get all users in hierarchy
- `get_immediate_superior(unit)`: Get parent unit
- `get_immediate_subordinates(unit)`: Get child units
- `create_hierarchy_level(parent, name, code, unit_type)`: Create new unit

### ApprovalService
Maker-Checker workflow:
- `create_approval_request(action_type, payload, maker)`: Create request
- `get_pending_approvals(checker)`: Get pending requests for user
- `approve_request(approval_request, checker, comments)`: Approve request
- `reject_request(approval_request, checker, comments)`: Reject request
- `route_approval(maker, action_type, payload)`: Create and route request
- `get_approval_statistics(user)`: Get user's approval statistics

## Security & Best Practices

1. **Authentication**: Token-based authentication via `rest_framework.authtoken`
2. **Permissions**: All endpoints require `IsAuthenticated` permission
3. **RBAC**: Role-based permissions enforced in services, not views
4. **Hierarchy-based Access**: Users can only access/manage their own unit and subordinates
5. **Audit Logging**: All actions are logged with user, timestamp, and metadata
6. **Password Security**: Uses Django's password hashing and validation
7. **Soft Deletes**: Users are deactivated rather than deleted
8. **CORS Support**: Configurable CORS for frontend integration

## Configuration

### Settings
See `admin_portal/settings.py` for:
- REST Framework configuration (authentication, pagination, filtering)
- Logging configuration
- CORS settings
- Database configuration (SQLite by default, easily swappable for Oracle/PostgreSQL)

### Environment Variables
Create a `.env` file for production (optional):
```
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=postgresql://user:password@localhost/dbname
```

## Testing

Run tests with:
```bash
python manage.py test
```

## Production Deployment

1. Set `DEBUG = False` in settings
2. Update `SECRET_KEY` to a secure value
3. Configure `ALLOWED_HOSTS`
4. Use a production database (PostgreSQL, Oracle, etc.)
5. Set up proper logging and error handling
6. Use a WSGI server (Gunicorn, uWSGI)
7. Configure CORS appropriately
8. Enable HTTPS/SSL
9. Set up environment variables

## License

Copyright © 2025. All rights reserved.

## Support

For issues and feature requests, please contact the development team.
