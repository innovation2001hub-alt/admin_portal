# Django Admin Portal - Complete Setup Guide

This document provides a step-by-step guide to set up and run the Django Admin Portal backend.

## Quick Start (5 minutes)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run migrations
python manage.py migrate

# 3. Create superuser
python manage.py createsuperuser

# 4. Seed initial data
python manage.py seed_data

# 5. Run server
python manage.py runserver
```

Then visit:
- API: http://localhost:8000/api/
- Admin: http://localhost:8000/admin/

---

## Detailed Setup

### 1. Environment Setup

**Windows:**
```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- Django 6.0.1
- djangorestframework 3.14.0
- django-filter 24.1
- django-cors-headers 4.3.1
- python-dotenv 1.0.0

### 3. Database Migrations

```bash
# Create migrations for changes (usually not needed)
python manage.py makemigrations

# Apply all migrations
python manage.py migrate
```

### 4. Create Django Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin user.

### 5. Seed Initial Data (Optional but Recommended)

```bash
python manage.py seed_data
```

This creates:
- **5 Roles**: ADMIN, MANAGER, MAKER, CHECKER, VIEWER
- **Organizational Units**: 
  - Head Office (HO001)
  - 2 Circles (CIRCLE001, CIRCLE002)
  - Networks and Administrative Offices
- **Sample Users**:
  - admin / AdminPortal@123 (ADMIN role)
  - manager1 / Manager@123 (MANAGER role)
  - maker1 / Maker@123 (MAKER role)

### 6. Run Development Server

```bash
python manage.py runserver
```

Server runs at: http://localhost:8000

---

## Accessing the Application

### Django Admin Panel
- URL: http://localhost:8000/admin/
- Login with the superuser credentials

Features:
- Manage Users, Roles, Units, Approval Requests, Audit Logs
- View all organizational data
- Admin-only operations

### REST API

#### Base URL
```
http://localhost:8000/api/
```

#### Authentication
All API endpoints require a token. Get a token by logging in:

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "AdminPortal@123"}'
```

Response:
```json
{
    "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
    "user": { ... }
}
```

Use token in headers:
```bash
curl -X GET http://localhost:8000/api/users/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

---

## API Endpoints Summary

### Authentication
- `POST /api/auth/login/` - Login and get token
- `POST /api/auth/logout/` - Logout and invalidate token
- `POST /api/auth/change-password/` - Change password
- `GET /api/auth/current-user/` - Get current user info

### Units (Hierarchy)
- `GET /api/units/` - List all units
- `POST /api/units/` - Create new unit
- `GET /api/units/{id}/` - Get unit details
- `PUT /api/units/{id}/` - Update unit
- `DELETE /api/units/{id}/` - Delete unit
- `GET /api/units/{id}/parent-chain/` - Get parent hierarchy
- `GET /api/units/{id}/children/` - Get direct children
- `GET /api/units/{id}/all-children/` - Get all descendants
- `GET /api/units/{id}/users/` - Get users in unit
- `GET /api/units/{id}/statistics/` - Get unit statistics

### Users
- `GET /api/users/` - List all users
- `POST /api/users/` - Create new user
- `GET /api/users/{id}/` - Get user details
- `PUT /api/users/{id}/` - Update user
- `DELETE /api/users/{id}/` - Deactivate user
- `POST /api/users/{id}/assign-roles/` - Assign roles
- `GET /api/users/{id}/roles/` - Get user roles
- `GET /api/users/by-unit/?unit_id=X` - Get users in unit
- `GET /api/users/in-hierarchy/?unit_id=X` - Get users in hierarchy
- `POST /api/users/{id}/activate/` - Activate user
- `POST /api/users/{id}/deactivate/` - Deactivate user

### Approvals (Maker-Checker Workflow)
- `GET /api/approvals/` - List all approvals
- `POST /api/approvals/` - Create approval request
- `GET /api/approvals/{id}/` - Get approval details
- `POST /api/approvals/{id}/approve/` - Approve request
- `POST /api/approvals/{id}/reject/` - Reject request
- `GET /api/approvals/pending/` - Get pending approvals
- `GET /api/approvals/statistics/` - Get approval statistics
- `GET /api/approvals/created-by-me/` - Get my created requests
- `GET /api/approvals/assigned-to-me/` - Get assigned approvals

---

## Testing the API

### Using cURL

```bash
# 1. Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "AdminPortal@123"}' | jq -r '.token')

# 2. List units
curl -X GET http://localhost:8000/api/units/ \
  -H "Authorization: Token $TOKEN"

# 3. Create a new unit
curl -X POST http://localhost:8000/api/units/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Circle",
    "code": "CIRCLE003",
    "unit_type": "CIRCLE",
    "parent": 1
  }'

# 4. Get unit hierarchy
curl -X GET http://localhost:8000/api/units/1/parent-chain/ \
  -H "Authorization: Token $TOKEN"
```

### Using Postman

1. Create a new Postman collection
2. Set base URL: `http://localhost:8000/api`
3. In Authentication tab, set type to "Bearer Token"
4. Login first to get a token
5. Use the token for subsequent requests

### Using Python

```python
import requests

BASE_URL = 'http://localhost:8000/api'

# Login
response = requests.post(f'{BASE_URL}/auth/login/', json={
    'username': 'admin',
    'password': 'AdminPortal@123'
})
token = response.json()['token']

headers = {'Authorization': f'Token {token}'}

# List units
response = requests.get(f'{BASE_URL}/units/', headers=headers)
print(response.json())

# Create unit
response = requests.post(f'{BASE_URL}/units/', headers=headers, json={
    'name': 'New Circle',
    'code': 'CIRCLE003',
    'unit_type': 'CIRCLE',
    'parent': 1
})
print(response.json())
```

---

## Project Structure Explanation

```
admin_core/
├── models/                    # Data models
│   ├── user.py               # Custom User with employee_id, designation, unit, roles
│   ├── role.py               # Role for RBAC
│   ├── hierarchy.py          # Unit model with parent-child relationships
│   ├── workflow.py           # ApprovalRequest for Maker-Checker workflow
│   ├── audit.py              # AuditLog for tracking all actions
│
├── serializers/               # DRF Serializers for validation and conversion
│   ├── user_serializer.py    # User serialization with nested roles/unit
│   ├── role_serializer.py    # Simple role serialization
│   ├── unit_serializer.py    # Unit serialization with hierarchy info
│   ├── approval_serializer.py # Approval request serialization
│
├── services/                  # Business logic layer
│   ├── auth_service.py       # Authentication, token, password logic
│   ├── hierarchy_service.py  # Unit hierarchy operations, access control
│   ├── approval_service.py   # Approval routing, workflow logic
│
├── views/                     # API ViewSets
│   ├── auth_views.py         # Login, Logout, Change Password, Current User
│   ├── unit_views.py         # Unit CRUD, hierarchy queries
│   ├── user_views.py         # User CRUD, role assignment
│   ├── approval_views.py     # Approval CRUD, approve/reject actions
│
├── admin.py                   # Django admin interface configuration
├── urls.py                    # URL routing for the app
├── management/commands/       # Custom management commands
│   └── seed_data.py          # Initial data seeding script
```

---

## Key Features Explained

### 1. Custom User Model
```python
class User(AbstractUser):
    employee_id         # Unique employee identifier
    designation         # Job title
    unit                # FK to Unit (organizational assignment)
    roles               # M2M to Role (for RBAC)
```

### 2. Organizational Hierarchy
```python
class Unit(models.Model):
    unit_type          # HO, CIRCLE, NETWORK, AO, RBO, BRANCH
    parent             # FK to self (parent unit)
    
    # Methods for hierarchy traversal
    get_parent_chain()      # Get all parents up to HO
    get_all_children()      # Get all descendants
    get_root_unit()         # Get the Head Office
```

### 3. RBAC System
- Flexible role definition
- Users can have multiple roles
- Roles checked in services, not views
- Hierarchy-based permissions (can manage subordinates only)

### 4. Maker-Checker Workflow
```python
class ApprovalRequest(models.Model):
    action_type         # Type of action (CREATE_USER, UPDATE_UNIT, etc.)
    payload             # JSON data for the action
    maker               # User who created the request
    checker             # User assigned to approve/reject
    status              # PENDING, APPROVED, REJECTED
    
    # Approval routing based on:
    # - Action type (user ops vs hierarchy ops)
    # - Organizational hierarchy (immediate superior vs HO)
```

### 5. Audit Logging
```python
class AuditLog(models.Model):
    user                # User who performed action
    action              # Action description
    action_type         # CREATE, UPDATE, DELETE, APPROVE, etc.
    metadata            # JSON with request details
    ip_address          # Request IP
    created_at          # Timestamp
```

---

## Common Tasks

### Create a New User
```bash
curl -X POST http://localhost:8000/api/users/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

### Create Approval Request
```bash
curl -X POST http://localhost:8000/api/approvals/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action_type": "CREATE_USER",
    "payload": {
      "username": "new_user",
      "email": "new@example.com"
    }
  }'
```

### Approve/Reject Request
```bash
# Approve
curl -X POST http://localhost:8000/api/approvals/1/approve/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"comments": "Looks good!"}'

# Reject
curl -X POST http://localhost:8000/api/approvals/1/reject/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"comments": "Need more info"}'
```

---

## Troubleshooting

### Port Already in Use
```bash
# Use a different port
python manage.py runserver 8001
```

### Migration Errors
```bash
# Check status
python manage.py showmigrations

# Roll back to specific migration
python manage.py migrate admin_core 0001

# Reapply all
python manage.py migrate
```

### Token Errors
- Make sure to include `Authorization: Token YOUR_TOKEN` header
- Token must be generated via login endpoint
- Token is case-sensitive

### Database Issues
```bash
# Reset database (WARNING: Deletes all data)
rm db.sqlite3
python manage.py migrate
python manage.py seed_data
```

---

## Production Checklist

- [ ] Set `DEBUG = False`
- [ ] Change `SECRET_KEY`
- [ ] Update `ALLOWED_HOSTS`
- [ ] Configure database (PostgreSQL/Oracle)
- [ ] Set up email backend
- [ ] Enable HTTPS
- [ ] Configure CORS properly
- [ ] Set up logging to files
- [ ] Use production WSGI server (Gunicorn)
- [ ] Set up monitoring and alerting
- [ ] Configure backups
- [ ] Set environment variables

---

## Next Steps

1. ✅ Understand the project structure
2. ✅ Run seed_data to populate initial data
3. ✅ Test API endpoints using cURL or Postman
4. ✅ Create additional users and roles as needed
5. ✅ Integrate with frontend application
6. ✅ Configure for production deployment

---

## Support & Documentation

- **Django Docs**: https://docs.djangoproject.com/
- **DRF Docs**: https://www.django-rest-framework.org/
- **Admin Panel**: http://localhost:8000/admin/
- **API Browsable Interface**: http://localhost:8000/api/

---

Last Updated: 2025-01-08
