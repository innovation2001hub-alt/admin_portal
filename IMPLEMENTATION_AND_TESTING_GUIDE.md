# Implementation & Testing Guide - PF ID Login System

## Overview
This guide provides step-by-step instructions to implement, test, and verify the new PF ID-based login system.

---

## Phase 1: Pre-Implementation Verification

### Step 1: Verify Current System
Before starting, confirm your current setup:

```bash
# Navigate to project root
cd C:\Users\hp\Desktop\admin_portal

# Check Django version
python manage.py --version

# Check installed packages
pip list | findstr django

# Verify database exists
dir *.sqlite3
```

### Step 2: Backup Current Database
```bash
# Create a backup of current database
copy db.sqlite3 db.sqlite3.backup

# Keep this safe in case you need to rollback
```

---

## Phase 2: Implementation Steps

### Step 1: Apply Code Changes

All code changes have already been made to these files:

✅ **Backend:**
- `admin_portal/admin_core/services/auth_service.py`
- `admin_portal/admin_core/views/auth_views.py`
- `admin_portal/admin_core/models/user.py`

✅ **Frontend:**
- `frontend/src/components/Login.jsx`
- `frontend/src/services/api.js`

**Verify changes:** Review `CODE_CHANGES_SUMMARY.md` for exact modifications.

### Step 2: Database Migrations

```bash
# Navigate to admin_portal directory
cd admin_portal

# Check migration status
python manage.py showmigrations admin_core

# Apply any pending migrations
python manage.py migrate

# Verify migration was successful
python manage.py showmigrations admin_core | findstr admin_core
```

**Expected Output:** All migrations should show as applied `[X]`

### Step 3: Seed Initial Data

```bash
# Run the seed_data command to create sample users
python manage.py seed_data
```

**Expected Output:**
```
Starting data seeding...
  Created: Role "ADMIN"
  Created: Role "MANAGER"
  ... (more roles)
  Created: User "admin" with roles ['ADMIN']
  Created: User "manager1" with roles ['MANAGER']
  Created: User "maker1" with roles ['MAKER']
Data seeding completed successfully!
```

### Step 4: Verify Users in Database

```bash
# Open Django shell
python manage.py shell
```

In the shell, run:
```python
from admin_core.models import User

# List all users
for user in User.objects.all():
    print(f"Employee ID: {user.employee_id}, Username: {user.username}, Email: {user.email}")

# Check a specific user
admin_user = User.objects.get(employee_id='EMP001')
print(f"Admin user found: {admin_user.get_full_name()}")

# Verify password works
if admin_user.check_password('AdminPortal@123'):
    print("✓ Password verification successful!")
else:
    print("✗ Password verification failed!")

# Exit shell
exit()
```

---

## Phase 3: Starting the Application

### Step 1: Start Backend Server

```bash
# From admin_portal directory
python manage.py runserver
```

**Expected Output:**
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

Keep this terminal open.

### Step 2: Start Frontend Application (in new terminal)

```bash
# Navigate to frontend directory
cd C:\Users\hp\Desktop\admin_portal\frontend

# Install dependencies (if not already done)
npm install

# Start development server
npm run dev
```

**Expected Output:**
```
VITE v... ready in ... ms

➜  Local:   http://localhost:5173/
```

---

## Phase 4: Manual Testing

### Test 1: Login with Valid Credentials

1. **Open Browser:** Navigate to `http://localhost:5173` (or your frontend URL)
2. **Login Form Should Show:**
   - Input field labeled "Employee ID (PF ID)"
   - Password input field
   - "Sign In" button
3. **Enter Credentials:**
   - Employee ID: `EMP001`
   - Password: `AdminPortal@123`
4. **Click "Sign In"**
5. **Expected Result:** 
   - Page redirects to `/dashboard`
   - Dashboard displays with user information
   - Welcome message or user name appears

**Verification:**
```javascript
// Open browser DevTools (F12) → Console → Run:
console.log(localStorage.getItem('user'))
console.log(localStorage.getItem('token'))
```
Both should have values.

### Test 2: Login with Invalid Employee ID

1. **Enter Credentials:**
   - Employee ID: `INVALID123`
   - Password: `AdminPortal@123`
2. **Click "Sign In"**
3. **Expected Result:** 
   - Error message: "Invalid employee ID or password."
   - Stays on login page
   - localStorage is empty

### Test 3: Login with Wrong Password

1. **Enter Credentials:**
   - Employee ID: `EMP001`
   - Password: `WrongPassword123`
2. **Click "Sign In"**
3. **Expected Result:** 
   - Error message: "Invalid employee ID or password."
   - Stays on login page

### Test 4: Test Other Users

**Manager User:**
- Employee ID: `EMP002`
- Password: `Manager@123`
- Expected Role: MANAGER

**Maker User:**
- Employee ID: `EMP003`
- Password: `Maker@123`
- Expected Role: MAKER

### Test 5: API Testing with cURL

```bash
# Test login endpoint directly
curl -X POST http://127.0.0.1:8000/api/auth/login/ ^
  -H "Content-Type: application/json" ^
  -d "{\"employee_id\": \"EMP001\", \"password\": \"AdminPortal@123\"}"
```

**Expected Response:**
```json
{
  "token": "abc123def456...",
  "user": {
    "id": 1,
    "employee_id": "EMP001",
    "username": "admin",
    "first_name": "System",
    "last_name": "Administrator",
    "email": "admin@adminportal.com",
    "designation": "System Administrator"
  },
  "message": "Login successful."
}
```

### Test 6: Logout Test

1. **After successful login to dashboard**
2. **Click the logout button/link** (usually in header or menu)
3. **Expected Result:**
   - Redirect to login page
   - localStorage is cleared
   - Cannot access dashboard without logging in again

### Test 7: Session Persistence

1. **Login successfully**
2. **Refresh the page (F5)**
3. **Expected Result:**
   - Stay logged in
   - Dashboard content displays immediately
   - No redirect to login page

### Test 8: Token Authentication

```bash
# Get token from successful login response
set TOKEN=<your_token_from_login_response>

# Use token in API request
curl -X GET http://127.0.0.1:8000/api/users/ ^
  -H "Authorization: Token %TOKEN%"
```

**Expected Response:** User data list (401 error if token is invalid/missing)

---

## Phase 5: Audit Log Verification

### Check Login Audit Logs

```bash
# Open Django shell
python manage.py shell
```

In the shell:
```python
from admin_core.models import AuditLog

# View recent login logs
recent_logins = AuditLog.objects.filter(action_type='LOGIN').order_by('-created_at')[:10]

for log in recent_logins:
    print(f"User: {log.user.employee_id}, Time: {log.created_at}, IP: {log.ip_address}")

# Exit
exit()
```

**Expected Output:** Shows all login attempts with employee IDs and timestamps.

---

## Phase 6: Adding New Users

### Method 1: Django Admin (if enabled)

```bash
# Create superuser if not exists
python manage.py createsuperuser

# Then navigate to:
# http://127.0.0.1:8000/admin/
# And add users through the admin interface
```

### Method 2: Django Shell

```bash
python manage.py shell
```

```python
from admin_core.models import User, Unit, Role

# Get the Head Office unit
ho = Unit.objects.get(code='HO001')

# Get a role
manager_role = Role.objects.get(name='MANAGER')

# Create new user
new_user = User.objects.create_user(
    username='newuser_unique_id',  # Must be unique
    employee_id='PF999',             # This is the login ID
    email='newuser@example.com',
    password='SecurePass@123'        # Will be hashed automatically
)

# Set additional fields
new_user.first_name = 'John'
new_user.last_name = 'Doe'
new_user.designation = 'Manager'
new_user.unit = ho
new_user.is_active = True
new_user.save()

# Add role
new_user.roles.add(manager_role)

# Verify
print(f"Created user: {new_user.get_full_name()} ({new_user.employee_id})")

# Exit
exit()
```

### Method 3: Management Command (Create custom script)

Create `admin_portal/add_user.py`:

```python
from django.core.management.base import BaseCommand
from admin_core.models import User, Unit, Role

class Command(BaseCommand):
    help = 'Add a new user to the system'
    
    def add_arguments(self, parser):
        parser.add_argument('employee_id', type=str)
        parser.add_argument('password', type=str)
        parser.add_argument('--email', type=str, required=True)
        parser.add_argument('--first-name', type=str, required=True)
        parser.add_argument('--last-name', type=str, required=True)
        parser.add_argument('--designation', type=str, required=True)
    
    def handle(self, *args, **options):
        ho = Unit.objects.get(code='HO001')
        
        user = User.objects.create_user(
            username=options['employee_id'],
            employee_id=options['employee_id'],
            email=options['email'],
            password=options['password'],
            first_name=options['first_name'],
            last_name=options['last_name'],
            designation=options['designation'],
            unit=ho,
            is_active=True
        )
        
        self.stdout.write(self.style.SUCCESS(
            f'User {user.employee_id} created successfully!'
        ))
```

Usage:
```bash
python manage.py add_user PF999 "SecurePass@123" \
  --email newuser@example.com \
  --first-name John \
  --last-name Doe \
  --designation Manager
```

---

## Phase 7: Troubleshooting

### Issue: Login shows "Invalid employee ID or password" for correct credentials

**Diagnostics:**
```python
# Open Django shell
python manage.py shell

from admin_core.models import User

# Check if user exists
try:
    user = User.objects.get(employee_id='EMP001')
    print(f"User found: {user.username}")
except User.DoesNotExist:
    print("User does not exist!")

# Check password
if user.check_password('AdminPortal@123'):
    print("✓ Password is correct")
else:
    print("✗ Password is incorrect")

# Check if user is active
print(f"Is active: {user.is_active}")

exit()
```

**Solutions:**
- If user doesn't exist: Run `python manage.py seed_data`
- If password is wrong: Reset it using `user.set_password('NewPass@123'); user.save()`
- If not active: Set `user.is_active = True; user.save()`

### Issue: Frontend still shows "Username" field

**Solution:**
```bash
# Clear cache
# 1. Hard refresh in browser: Ctrl+Shift+R
# 2. Or clear browser cache (DevTools → Application → Clear Storage)
# 3. Verify code changes: Check if Login.jsx has "employeeId"
```

### Issue: API returns "Employee ID and password are required"

**Check:**
```python
# Verify request body format is correct
# Should be: {"employee_id": "PF001", "password": "Pass@123"}
# NOT: {"employee_id": "PF001", "password": "Pass@123"}
```

### Issue: CORS or API connection errors

**Verify:**
```bash
# Backend is running: http://127.0.0.1:8000/api/auth/login/
# Frontend is running: http://localhost:5173
# Check CORS settings in settings.py
```

---

## Phase 8: Performance Testing

### Load Test Login Endpoint

```bash
# Using Apache Bench (if installed)
ab -n 100 -c 10 -p data.json -T application/json ^
  http://127.0.0.1:8000/api/auth/login/
```

Where `data.json` contains:
```json
{"employee_id": "EMP001", "password": "AdminPortal@123"}
```

---

## Phase 9: Security Checklist

- [ ] All passwords are hashed (never plain text)
- [ ] User accounts are active (`is_active=True`)
- [ ] Audit logs record all login attempts
- [ ] Employee IDs are unique
- [ ] Tokens expire appropriately
- [ ] Password change functionality works
- [ ] Inactive users cannot login
- [ ] Error messages don't reveal valid employee IDs
- [ ] HTTPS is used in production
- [ ] Database is backed up

---

## Phase 10: Deployment Preparation

### Checklist

- [ ] All tests pass
- [ ] No hardcoded credentials in code
- [ ] Database backed up
- [ ] Environment variables configured
- [ ] CORS settings appropriate for production
- [ ] DEBUG mode is False in production
- [ ] Secret key is secure
- [ ] Static files collected
- [ ] API documentation updated
- [ ] User documentation created

### Pre-Deployment Commands

```bash
# Test the application
python manage.py test

# Check for errors
python manage.py check

# Collect static files (if using Django admin)
python manage.py collectstatic

# Migrate database
python manage.py migrate

# Create superuser for admin (if needed)
python manage.py createsuperuser
```

---

## Summary

✅ **Completed Implementation:**
- PF ID-based login implemented
- Password authentication from database
- Audit logging configured
- Frontend updated
- Security best practices applied

✅ **Testing Coverage:**
- Valid credentials
- Invalid credentials
- User roles and permissions
- Session management
- API endpoints
- Audit logs

✅ **Ready for:**
- Development testing
- Production deployment
- User onboarding
- System monitoring

---

