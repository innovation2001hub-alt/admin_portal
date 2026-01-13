# User Creation and Login Guide

## Overview
Your admin portal is **already configured** to create users with passwords using their PF ID (employee_id) and allow them to login on the frontend.

## How It Works

### 1. Creating a New User

When creating a new user via the API, you need to provide:
- **employee_id** (PF ID) - Required
- **username** - Required
- **password** - Required (minimum 8 characters)
- **password_confirm** - Required (must match password)
- **first_name** - Required
- **last_name** - Required
- **email** - Required
- **designation** - Required
- **unit_id** - Optional
- **role_ids** - Optional (array)

### 2. API Endpoint for User Creation

**POST** `/api/users/`

**Request Body Example:**
```json
{
  "employee_id": "PF12345",
  "username": "john.doe",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "designation": "Manager",
  "unit_id": 1,
  "role_ids": [1, 2]
}
```

**Response (Success):**
```json
{
  "id": 10,
  "employee_id": "PF12345",
  "username": "john.doe",
  "first_name": "John",
  "last_name": "Doe",
  "full_name": "John Doe",
  "email": "john.doe@example.com",
  "designation": "Manager",
  "unit": {
    "id": 1,
    "name": "Head Office",
    "code": "HO",
    "unit_type": "HO"
  },
  "roles": [
    {
      "id": 1,
      "name": "Admin"
    }
  ],
  "is_active": true
}
```

### 3. Login Using PF ID and Password

Once a user is created, they can login on the frontend using:
- **Employee ID (PF ID)**: `PF12345`
- **Password**: `SecurePass123!`

**API Endpoint:** POST `/api/auth/login/`

**Request Body:**
```json
{
  "employee_id": "PF12345",
  "password": "SecurePass123!"
}
```

**Response (Success):**
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user": {
    "id": 10,
    "employee_id": "PF12345",
    "username": "john.doe",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "email": "john.doe@example.com",
    "designation": "Manager",
    "unit": {...},
    "roles": [...]
  },
  "message": "Login successful."
}
```

### 4. Frontend Login

The frontend login page at `/` accepts:
- **Employee ID (PF ID)** field
- **Password** field

Users can login directly using their PF ID and the password set during user creation.

## Testing the Flow

### Step 1: Create a Test User

Use a tool like Postman, curl, or the Django admin to create a user:

```bash
curl -X POST http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_ADMIN_TOKEN" \
  -d '{
    "employee_id": "PF99999",
    "username": "test.user",
    "password": "TestPass123!",
    "password_confirm": "TestPass123!",
    "first_name": "Test",
    "last_name": "User",
    "email": "test.user@example.com",
    "designation": "Tester"
  }'
```

### Step 2: Login on Frontend

1. Open the frontend at `http://localhost:5173/`
2. Enter:
   - Employee ID: `PF99999`
   - Password: `TestPass123!`
3. Click "Sign In"
4. You should be redirected to the dashboard

### Step 3: Verify Login via API

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "PF99999",
    "password": "TestPass123!"
  }'
```

## Password Requirements

- **Minimum length**: 8 characters
- Uses Django's built-in password validation
- Passwords are securely hashed using Django's password hashing
- Password confirmation is required during creation

## Security Features

✅ **Password Hashing**: All passwords are hashed using Django's secure hashing algorithm  
✅ **Token Authentication**: After login, users receive a token for API requests  
✅ **Audit Logging**: All login attempts are logged  
✅ **Active Status Check**: Inactive users cannot login  
✅ **Password Validation**: Ensures strong passwords

## Admin Functions

### Create User via Django Admin

1. Access Django admin at `http://localhost:8000/admin/`
2. Go to Users section
3. Click "Add User"
4. Fill in all required fields including password
5. Save

### Create User via API (Programmatically)

The UserSerializer handles password hashing automatically when creating users through the API.

## Summary

Your system is **already fully functional** for:
1. ✅ Creating users with PF ID and password
2. ✅ Logging in using PF ID and password on the frontend
3. ✅ Secure password storage and authentication
4. ✅ Token-based session management

No additional configuration is needed!
