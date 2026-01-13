# Login System Migration Guide
## From Username/Password to PF ID/Password Authentication

This guide documents the changes made to migrate the login system from username-based authentication to Employee ID (PF ID) based authentication with passwords stored in the database.

---

## Changes Made

### 1. **Backend Changes**

#### A. User Model (`admin_core/models/user.py`)
- The `User` model already extends Django's `AbstractUser`, which includes a built-in `password` field
- Updated the `employee_id` field documentation to clarify it's the PF ID
- The password field is managed by Django's AbstractUser and supports secure password hashing

#### B. Authentication Service (`admin_core/services/auth_service.py`)
**Method: `authenticate_user()`**
- **Changed from:** `authenticate_user(username, password, ip_address=None)`
- **Changed to:** `authenticate_user(employee_id, password, ip_address=None)`
- **Logic update:**
  - Now fetches user by `employee_id` instead of using Django's `authenticate()` function
  - Manually checks password using `user.check_password()` method
  - Provides consistent error message for both invalid employee ID and password attempts
  - Still logs audit trail and updates last login timestamp

#### C. Login View (`admin_core/views/auth_views.py`)
**View: `LoginView.create()`**
- **Changed from:** Username-based login endpoint
- **Changed to:** Employee ID-based login endpoint
- **Request parameters update:**
  - From: `username` and `password`
  - To: `employee_id` and `password`
- **Error messages updated** to reference "Employee ID" instead of "Username"

---

### 2. **Frontend Changes**

#### A. Login Component (`frontend/src/components/Login.jsx`)
- **State variables updated:**
  - From: `username` → To: `employeeId`
- **Form label:** "Username" → "Employee ID (PF ID)"
- **Input placeholder:** Updated to reflect Employee ID input
- **Form validation:** Updated error messages for Employee ID and password
- **Footer message:** Changed from hardcoded credentials message to guidance message

#### B. API Service (`frontend/src/services/api.js`)
**Function: `authAPI.login()`**
- **Parameter name change:** `username` → `employeeId`
- **API payload update:**
  - From: `{ username, password }`
  - To: `{ employee_id: employeeId, password }`

---

## Implementation Steps

### Step 1: Apply Database Migration
If this is an existing database with the User model, you may need to create a migration:

```bash
python manage.py makemigrations admin_core
python manage.py migrate
```

### Step 2: Seed Data with Passwords
The existing `seed_data.py` management command already supports password setting:

```bash
python manage.py seed_data
```

This creates sample users with the following credentials:
- **Admin User:**
  - Employee ID: `EMP001`
  - Password: `AdminPortal@123`

- **Manager User:**
  - Employee ID: `EMP002`
  - Password: `Manager@123`

- **Maker User:**
  - Employee ID: `EMP003`
  - Password: `Maker@123`

### Step 3: Add Existing Users
To add users to the system with passwords, use Django's management shell:

```bash
python manage.py shell
```

Then in the shell:
```python
from admin_core.models import User, Unit, Role

# Get the Head Office unit
ho = Unit.objects.get(code='HO001')

# Create a user
user = User.objects.create_user(
    username='unique_username',  # Still needed for Django's internal use
    employee_id='PF001',          # Use the PF ID
    email='user@example.com',
    password='SecurePassword@123' # Password will be hashed
)

# Add the user to a unit
user.unit = ho
user.is_active = True
user.save()

# Assign roles if needed
admin_role = Role.objects.get(name='ADMIN')
user.roles.add(admin_role)
```

### Step 4: Update Frontend (if running separately)
Make sure to rebuild the frontend:

```bash
cd frontend
npm install
npm run dev
```

---

## Login Flow

### Old Flow (Username-based):
1. User enters username and password in login form
2. Frontend sends to `POST /api/auth/login/` with `{ username, password }`
3. Backend authenticates using Django's `authenticate()` function
4. On success, returns token and user data

### New Flow (Employee ID-based):
1. User enters Employee ID (PF ID) and password in login form
2. Frontend sends to `POST /api/auth/login/` with `{ employee_id, password }`
3. Backend:
   - Looks up user by `employee_id` field
   - Verifies password using `check_password()` method
   - Returns authentication token and user data on success
4. Frontend stores token and user info in localStorage
5. Subsequent API requests include the token in Authorization header

---

## Security Features

✅ **Passwords are hashed** using Django's default PBKDF2 algorithm  
✅ **Audit logging** records all login attempts with IP address  
✅ **Token-based authentication** using Django REST Framework's Token Authentication  
✅ **User account status** checked - inactive accounts cannot login  
✅ **Last login timestamp** automatically updated  
✅ **Generic error messages** prevent employee ID enumeration attacks  

---

## Testing the Login

### Test Case 1: Valid Credentials
```
Employee ID: EMP001
Password: AdminPortal@123
Expected: Successful login with admin role
```

### Test Case 2: Invalid Employee ID
```
Employee ID: INVALID
Password: AdminPortal@123
Expected: "Invalid employee ID or password." error
```

### Test Case 3: Invalid Password
```
Employee ID: EMP001
Password: WrongPassword
Expected: "Invalid employee ID or password." error
```

### Test Case 4: Inactive Account
- Create a user with `is_active=False`
- Attempt login with correct credentials
- Expected: "This user account is inactive." error

---

## API Endpoint Reference

### Login Endpoint
- **URL:** `POST /api/auth/login/`
- **Request Body:**
  ```json
  {
    "employee_id": "PF001",
    "password": "SecurePassword@123"
  }
  ```
- **Success Response (200 OK):**
  ```json
  {
    "token": "abc123def456",
    "user": {
      "id": 1,
      "employee_id": "PF001",
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com",
      "designation": "Manager",
      "roles": ["ADMIN"]
    },
    "message": "Login successful."
  }
  ```
- **Error Response (401 Unauthorized):**
  ```json
  {
    "error": "Invalid employee ID or password."
  }
  ```

---

## Password Management

### Setting a Password (Django Shell)
```python
from admin_core.models import User
user = User.objects.get(employee_id='PF001')
user.set_password('NewPassword@123')
user.save()
```

### Changing Password (Via API)
The existing `change_password` endpoint is available at:
- **URL:** `POST /api/auth/change-password/`
- **Headers:** `Authorization: Token <token>`
- **Request Body:**
  ```json
  {
    "old_password": "OldPassword@123",
    "new_password": "NewPassword@123"
  }
  ```

---

## Rollback Instructions (if needed)

If you need to revert to username-based authentication:

1. Revert the backend files:
   - `admin_core/services/auth_service.py` - restore `authenticate()` usage
   - `admin_core/views/auth_views.py` - restore `username` parameter

2. Revert the frontend files:
   - `frontend/src/components/Login.jsx` - restore `username` state
   - `frontend/src/services/api.js` - restore `username` in API call

3. Note: The password field will remain in the User model (no harm in this)

---

## Migration Notes

- **No data loss:** All existing user data is preserved
- **Backward compatibility:** The `username` field still exists and is required by Django's AbstractUser
- **Password field:** Uses Django's built-in password field with secure hashing
- **Employee ID:** Is now the primary login identifier
- **Existing sessions:** Users will need to log in again with new credentials

---

## Support

For issues or questions:
1. Check the audit logs for login attempts
2. Verify user's `is_active` status
3. Ensure user's `employee_id` is unique
4. Check that password was set using `set_password()` method, not plain text assignment

