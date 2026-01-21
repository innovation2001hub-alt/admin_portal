# Super Admin User Management Documentation

## Overview

The Super Admin role is a top-level administrative user with the ability to create, manage, and configure all other users in the system. Super Admin has global access and can assign any role (MAKER, CHECKER, ADMIN) to users and manage their units.

## Super Admin Credentials

```
Username: superadmin
Password: superadmin123
```

## Super Admin Capabilities

### 1. User Management Panel
- Access at: Dashboard → "👥 User Management" tab
- **List All Users**: View all users in the system with their details, roles, and status
- **Create Users**: Add new users with full configuration
- **Edit Users**: Update user information, roles, and unit assignments
- **Delete Users**: Remove users from the system
- **Reset Password**: Reset user passwords
- **Activate/Deactivate**: Toggle user active status

### 2. Role Assignment
Super Admin can assign any of these roles to users:
- **MAKER**: Can create approval requests
- **CHECKER**: Can review and approve/reject requests
- **ADMIN**: Has administrative access to dashboard features
- **SUPER_ADMIN**: Full system access (only 1 account recommended)

### 3. Unit Assignment
Super Admin can assign users to any unit in the hierarchy:
```
Corporate Office (CO)
├── Local Head Office (LHO)
│   └── Administrative Office (AO)
│       └── Regional Office (RO)
│           └── Branch (BR)
```

## API Endpoints

### List All Users
```
GET /api/user-management/
Authorization: Token {token}
```

Query Parameters:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 10)
- `search`: Search by username or email
- `unit_id`: Filter by unit ID
- `is_active`: Filter by active status (true/false)

Response:
```json
{
  "count": 12,
  "results": [
    {
      "id": 1,
      "username": "maker_karol_bagh",
      "email": "maker.kb@sbi.com",
      "first_name": "Rahul",
      "last_name": "Gupta",
      "unit_display": {
        "id": 8,
        "code": "BR_KAROL_BAGH",
        "name": "Branch - Karol Bagh",
        "unit_type": "BR"
      },
      "roles": ["MAKER"],
      "is_active": true,
      "created_at": "2026-01-20T12:00:00Z"
    }
  ]
}
```

### Create User
```
POST /api/user-management/
Authorization: Token {token}
Content-Type: application/json
```

Request Body:
```json
{
  "username": "newuser",
  "email": "newuser@sbi.com",
  "password": "SecurePass123",
  "first_name": "John",
  "last_name": "Doe",
  "employee_id": "EMP_NEW_001",
  "unit_id": 8,
  "role_ids": [2, 3],
  "is_active": true
}
```

Response: (201 Created)
```json
{
  "id": 13,
  "username": "newuser",
  "email": "newuser@sbi.com",
  "first_name": "John",
  "last_name": "Doe",
  "employee_id": "EMP_NEW_001",
  "unit_id": 8,
  "unit_display": { ... },
  "roles": [ ... ],
  "is_active": true
}
```

### Update User
```
PATCH /api/user-management/{id}/
Authorization: Token {token}
Content-Type: application/json
```

Request Body (all fields optional):
```json
{
  "email": "updated@sbi.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "unit_id": 9,
  "role_ids": [2],
  "is_active": true
}
```

### Delete User
```
DELETE /api/user-management/{id}/
Authorization: Token {token}
```

Response: (204 No Content)

### Get Available Roles
```
GET /api/user-management/available-roles/
Authorization: Token {token}
```

Response:
```json
[
  {
    "id": 1,
    "name": "ADMIN",
    "description": "Administrator role with full system access"
  },
  {
    "id": 2,
    "name": "MAKER",
    "description": "Request maker - can create approval requests"
  },
  {
    "id": 3,
    "name": "CHECKER",
    "description": "Checker/Approver - can approve or reject requests"
  },
  {
    "id": 4,
    "name": "SUPER_ADMIN",
    "description": "Super administrator - can manage all users and roles"
  }
]
```

### Get Available Units
```
GET /api/user-management/available-units/
Authorization: Token {token}
```

Response:
```json
[
  {
    "id": 1,
    "code": "CO",
    "name": "Corporate Office",
    "unit_type": "CO",
    "parent_id": null
  },
  {
    "id": 2,
    "code": "LHO_NORTH",
    "name": "Local Head Office - North",
    "unit_type": "LHO",
    "parent_id": 1
  }
  ...
]
```

### Assign Roles to User
```
POST /api/user-management/{id}/assign-roles/
Authorization: Token {token}
Content-Type: application/json
```

Request Body:
```json
{
  "role_ids": [1, 2]
}
```

### Assign Unit to User
```
POST /api/user-management/{id}/assign-unit/
Authorization: Token {token}
Content-Type: application/json
```

Request Body:
```json
{
  "unit_id": 8
}
```

### Reset User Password
```
POST /api/user-management/{id}/reset-password/
Authorization: Token {token}
Content-Type: application/json
```

Request Body:
```json
{
  "password": "NewPassword123"
}
```

### Toggle User Active Status
```
POST /api/user-management/{id}/toggle-active/
Authorization: Token {token}
```

## Frontend User Management Interface

### List View
- Shows all users in a table with pagination
- Columns: Username, Email, Name, Unit, Roles, Status, Actions
- Sorting and filtering options
- Quick actions: Edit, Reset Password, Delete

### Create User Form
- Username (required)
- Email (required)
- Password (required)
- First Name
- Last Name
- Employee ID
- Unit (dropdown)
- Roles (checkboxes for multiple selection)
- Active Status (toggle)

### Edit User Form
- All fields except username are editable
- Roles can be changed
- Unit can be reassigned
- Status can be toggled
- Password reset available from list view

## Security Considerations

1. **Super Admin Access**: Only create Super Admin accounts when absolutely necessary
2. **Password Policy**: Ensure all users have strong passwords
3. **Role Assignment**: Be careful when assigning SUPER_ADMIN or ADMIN roles
4. **Unit Hierarchy**: Users should be assigned to appropriate units in the hierarchy
5. **Audit Trail**: All user management actions are logged in the system
6. **Token Security**: Always use HTTPS in production for token transmission

## Common Tasks

### Create a New Maker
1. Go to User Management
2. Click "Create New User"
3. Enter username: `maker_xxx`
4. Enter password
5. Select unit (Branch)
6. Check "MAKER" role
7. Click "Create User"

### Create a New Checker
1. Go to User Management
2. Click "Create New User"
3. Enter username: `checker_xxx`
4. Enter password
5. Select unit (Regional Office, Administrative Office, or Local Head Office)
6. Check "CHECKER" role
7. Click "Create User"

### Change User Role
1. Go to User Management
2. Find the user in the list
3. Click "Edit"
4. Modify the "Roles" section
5. Click "Update User"

### Reset User Password
1. Go to User Management
2. Find the user in the list
3. Click "Reset PW"
4. Enter the new password
5. Confirm

### Deactivate a User
1. Go to User Management
2. Find the user in the list
3. Click "Edit"
4. Uncheck "Active"
5. Click "Update User"

## Troubleshooting

### Cannot See User Management Tab
- Ensure you're logged in as Super Admin (superadmin / superadmin123)
- Check that your user has SUPER_ADMIN role

### Failed to Create User
- Ensure username is unique
- Verify all required fields are filled
- Check that the employee_id is unique

### User Cannot Login
- Verify user is marked as "Active"
- Reset password using Super Admin panel
- Check that user has appropriate roles assigned

### API Permission Error
- Verify token is valid
- Ensure logged-in user has SUPER_ADMIN role
- Check that API request includes Authorization header

## Best Practices

1. **Create Role-Specific Accounts**: Don't give users multiple conflicting roles
2. **Use Meaningful IDs**: Employee IDs should follow your organization's format
3. **Regular Audits**: Periodically review active users and their assignments
4. **Principle of Least Privilege**: Assign only necessary roles to users
5. **Documentation**: Document all custom user setups and configurations
