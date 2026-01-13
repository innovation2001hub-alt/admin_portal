# Quick Setup Checklist - PF ID Login Implementation

## ✅ What Was Changed

### Backend
- [x] `admin_core/services/auth_service.py` - Changed `authenticate_user()` to accept `employee_id` instead of `username`
- [x] `admin_core/views/auth_views.py` - Updated `LoginView` to expect `employee_id` and `password` in request
- [x] `admin_core/models/user.py` - Updated documentation (password field already existed via AbstractUser)

### Frontend
- [x] `frontend/src/components/Login.jsx` - Changed input from `username` to `employeeId`
- [x] `frontend/src/services/api.js` - Updated login function to send `employee_id` instead of `username`

---

## 🚀 Deployment Steps

### 1. Database Setup
```bash
# If updating existing database
cd admin_portal
python manage.py makemigrations admin_core
python manage.py migrate
```

### 2. Seed Initial Users
```bash
python manage.py seed_data
```

**Sample credentials created:**
- Employee ID: `EMP001` / Password: `AdminPortal@123`
- Employee ID: `EMP002` / Password: `Manager@123`
- Employee ID: `EMP003` / Password: `Maker@123`

### 3. Add More Users (Django Shell)
```bash
python manage.py shell
```

```python
from admin_core.models import User, Unit, Role

ho = Unit.objects.get(code='HO001')
user = User.objects.create_user(
    username='unique_id',
    employee_id='PF123',
    email='user@example.com',
    password='Secure@123'
)
user.unit = ho
user.is_active = True
user.save()
```

### 4. Start Backend Server
```bash
python manage.py runserver
```

### 5. Start Frontend (if separate)
```bash
cd frontend
npm install
npm run dev
```

---

## 📝 Login Page Changes

| Field | Old | New |
|-------|-----|-----|
| Input Label | "Username" | "Employee ID (PF ID)" |
| Input Placeholder | "Enter your username" | "Enter your Employee ID" |
| API Field Name | `username` | `employee_id` |
| Password Field | Same | Same (password field) |

---

## 🔐 Default Test Credentials

| Employee ID | Password | Role |
|------------|----------|------|
| EMP001 | AdminPortal@123 | ADMIN |
| EMP002 | Manager@123 | MANAGER |
| EMP003 | Maker@123 | MAKER |

---

## 🧪 Quick Test

1. **Navigate to login page** → `http://localhost:3000` (or your frontend URL)
2. **Enter Employee ID:** `EMP001`
3. **Enter Password:** `AdminPortal@123`
4. **Click Sign In**
5. **Expected Result:** Redirect to dashboard with admin access

---

## ⚠️ Common Issues & Solutions

### Issue: "Invalid employee ID or password"
- **Check:** Verify Employee ID exists in database
- **Check:** Ensure password was set using `user.set_password()`, not plain text
- **Check:** User account is active (`is_active=True`)

### Issue: Frontend still shows "Username" field
- **Solution:** Clear browser cache and reload
- **Or:** Check that `Login.jsx` file was properly updated

### Issue: API returns 400 Bad Request
- **Check:** API is expecting `employee_id` not `username`
- **Check:** Request headers include `Content-Type: application/json`

### Issue: Login works but no dashboard access
- **Check:** User has roles assigned
- **Check:** Check audit logs for login records

---

## 📊 Database Schema (User Table)

The User model includes:
- `id` - Primary key
- `employee_id` - **NEW UNIQUE LOGIN IDENTIFIER** (PF ID)
- `password` - **Hashed password from AbstractUser**
- `username` - Still required by Django (can be auto-generated)
- `email` - Email address
- `first_name` - First name
- `last_name` - Last name
- `is_active` - Account status
- `is_staff` - Staff status
- `is_superuser` - Superuser status
- `designation` - Job title
- `unit_id` - Foreign key to Unit
- `last_login` - Auto-updated on each login
- `date_joined` - Account creation timestamp

---

## 🔄 Password Management

### Reset User Password (Django Shell)
```python
from admin_core.models import User
user = User.objects.get(employee_id='PF123')
user.set_password('NewPassword@123')
user.save()
```

### Change Password Via API
**Endpoint:** `POST /api/auth/change-password/`
**Headers:** `Authorization: Token <your_token>`
**Body:**
```json
{
  "old_password": "OldPassword@123",
  "new_password": "NewPassword@123"
}
```

---

## 📋 Files Modified Summary

```
✅ admin_portal/admin_core/models/user.py
   - Updated documentation for employee_id

✅ admin_portal/admin_core/services/auth_service.py
   - authenticate_user() now uses employee_id
   - Uses check_password() instead of Django's authenticate()

✅ admin_portal/admin_core/views/auth_views.py
   - LoginView expects employee_id parameter
   - Updated error messages

✅ frontend/src/components/Login.jsx
   - Changed to use employeeId state
   - Updated labels and placeholders

✅ frontend/src/services/api.js
   - login() function now sends employee_id
```

---

## ✨ Implementation Complete!

All changes have been made. The system is now:
- ✅ Using PF ID (Employee ID) for login
- ✅ Using database-stored passwords
- ✅ Hashing passwords securely
- ✅ Maintaining full audit trails
- ✅ Supporting role-based access control

