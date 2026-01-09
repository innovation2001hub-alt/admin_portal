# API Testing Guide - Example cURL Commands

This guide provides ready-to-use cURL commands for testing the Admin Portal API.

## Prerequisites

- API running at `http://localhost:8000`
- Seed data populated (run `python manage.py seed_data`)
- cURL installed (or use Postman with the same syntax)
- jq installed (optional, for JSON parsing: `brew install jq` or `apt-get install jq`)

---

## 1. Authentication Tests

### 1.1 Login with Admin User
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "AdminPortal@123"
  }' | jq .
```

**Expected Response**:
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bb...",
  "user": {
    "id": 1,
    "username": "admin",
    "first_name": "System",
    "last_name": "Administrator",
    ...
  }
}
```

### 1.2 Save Token for Reuse
```bash
# On Linux/Mac
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "AdminPortal@123"}' | jq -r '.token')

echo "Token: $TOKEN"

# On Windows (PowerShell)
$response = curl.exe -s -X POST http://localhost:8000/api/auth/login/ `
  -H "Content-Type: application/json" `
  -d '{"username":"admin","password":"AdminPortal@123"}' | ConvertFrom-Json
$TOKEN = $response.token
Write-Host "Token: $TOKEN"
```

### 1.3 Get Current User Info
```bash
curl -X GET http://localhost:8000/api/auth/current-user/ \
  -H "Authorization: Token $TOKEN" | jq .
```

### 1.4 Change Password
```bash
curl -X POST http://localhost:8000/api/auth/change-password/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "AdminPortal@123",
    "new_password": "NewPassword@123",
    "new_password_confirm": "NewPassword@123"
  }' | jq .
```

### 1.5 Logout
```bash
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Authorization: Token $TOKEN"
```

---

## 2. Unit Management Tests

### 2.1 List All Units
```bash
curl -X GET 'http://localhost:8000/api/units/' \
  -H "Authorization: Token $TOKEN" | jq .
```

### 2.2 List Units with Filtering
```bash
# Filter by unit type
curl -X GET 'http://localhost:8000/api/units/?unit_type=CIRCLE' \
  -H "Authorization: Token $TOKEN" | jq .

# Search by name
curl -X GET 'http://localhost:8000/api/units/?search=Head' \
  -H "Authorization: Token $TOKEN" | jq .

# Order by code
curl -X GET 'http://localhost:8000/api/units/?ordering=code' \
  -H "Authorization: Token $TOKEN" | jq .
```

### 2.3 Create a New Unit
```bash
curl -X POST http://localhost:8000/api/units/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Circle Three",
    "code": "CIRCLE003",
    "unit_type": "CIRCLE",
    "parent": null
  }' | jq .
```

### 2.4 Get Specific Unit
```bash
curl -X GET http://localhost:8000/api/units/1/ \
  -H "Authorization: Token $TOKEN" | jq .
```

### 2.5 Get Unit Parent Chain (Hierarchy)
```bash
curl -X GET http://localhost:8000/api/units/2/parent-chain/ \
  -H "Authorization: Token $TOKEN" | jq .
```

**Expected Response**: List of parents from current unit to HO

### 2.6 Get Unit Children
```bash
# Direct children only
curl -X GET http://localhost:8000/api/units/1/children/ \
  -H "Authorization: Token $TOKEN" | jq .

# All descendants recursively
curl -X GET http://localhost:8000/api/units/1/all-children/ \
  -H "Authorization: Token $TOKEN" | jq .
```

### 2.7 Get Users in Unit
```bash
curl -X GET http://localhost:8000/api/units/1/users/ \
  -H "Authorization: Token $TOKEN" | jq .
```

### 2.8 Get Unit Statistics
```bash
curl -X GET http://localhost:8000/api/units/1/statistics/ \
  -H "Authorization: Token $TOKEN" | jq .
```

**Expected Response**:
```json
{
  "unit_id": 1,
  "unit_name": "Head Office",
  "unit_code": "HO001",
  "unit_type": "HO",
  "total_users": 3,
  "direct_children": 2,
  "all_descendants": 7,
  "parent": null
}
```

### 2.9 Update Unit
```bash
curl -X PUT http://localhost:8000/api/units/3/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Circle Three - Updated",
    "code": "CIRCLE003",
    "unit_type": "CIRCLE",
    "parent": 1
  }' | jq .
```

### 2.10 Delete Unit
```bash
curl -X DELETE http://localhost:8000/api/units/3/ \
  -H "Authorization: Token $TOKEN"
```

---

## 3. User Management Tests

### 3.1 List All Users
```bash
curl -X GET 'http://localhost:8000/api/users/' \
  -H "Authorization: Token $TOKEN" | jq .
```

### 3.2 List Users with Filters
```bash
# Filter by unit
curl -X GET 'http://localhost:8000/api/users/?unit=1' \
  -H "Authorization: Token $TOKEN" | jq .

# Filter by active status
curl -X GET 'http://localhost:8000/api/users/?is_active=true' \
  -H "Authorization: Token $TOKEN" | jq .

# Search user
curl -X GET 'http://localhost:8000/api/users/?search=john' \
  -H "Authorization: Token $TOKEN" | jq .
```

### 3.3 Create New User
```bash
curl -X POST http://localhost:8000/api/users/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "newuser@example.com",
    "first_name": "New",
    "last_name": "User",
    "employee_id": "EMP005",
    "designation": "Officer",
    "unit_id": 1,
    "role_ids": [3],
    "password": "SecurePass@123",
    "password_confirm": "SecurePass@123"
  }' | jq .
```

### 3.4 Get User Details
```bash
curl -X GET http://localhost:8000/api/users/4/ \
  -H "Authorization: Token $TOKEN" | jq .
```

### 3.5 Get User Roles
```bash
curl -X GET http://localhost:8000/api/users/1/roles/ \
  -H "Authorization: Token $TOKEN" | jq .
```

### 3.6 Assign Roles to User
```bash
curl -X POST http://localhost:8000/api/users/4/assign-roles/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role_ids": [1, 3]
  }' | jq .
```

### 3.7 Get Users by Unit
```bash
curl -X GET 'http://localhost:8000/api/users/by-unit/?unit_id=1' \
  -H "Authorization: Token $TOKEN" | jq .
```

### 3.8 Get Users in Unit Hierarchy
```bash
curl -X GET 'http://localhost:8000/api/users/in-hierarchy/?unit_id=1' \
  -H "Authorization: Token $TOKEN" | jq .
```

### 3.9 Activate/Deactivate User
```bash
# Deactivate
curl -X POST http://localhost:8000/api/users/4/deactivate/ \
  -H "Authorization: Token $TOKEN" | jq .

# Activate
curl -X POST http://localhost:8000/api/users/4/activate/ \
  -H "Authorization: Token $TOKEN" | jq .
```

### 3.10 Update User
```bash
curl -X PUT http://localhost:8000/api/users/4/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "designation": "Senior Officer"
  }' | jq .
```

---

## 4. Approval Workflow Tests

### 4.1 List All Approvals
```bash
curl -X GET 'http://localhost:8000/api/approvals/' \
  -H "Authorization: Token $TOKEN" | jq .
```

### 4.2 List Approvals with Filters
```bash
# Filter by status
curl -X GET 'http://localhost:8000/api/approvals/?status=PENDING' \
  -H "Authorization: Token $TOKEN" | jq .

# Filter by action type
curl -X GET 'http://localhost:8000/api/approvals/?action_type=CREATE_USER' \
  -H "Authorization: Token $TOKEN" | jq .
```

### 4.3 Create Approval Request
```bash
curl -X POST http://localhost:8000/api/approvals/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action_type": "CREATE_USER",
    "payload": {
      "username": "approval_user",
      "email": "approval@example.com",
      "first_name": "Approval",
      "last_name": "User"
    }
  }' | jq .
```

### 4.4 Get Approval Details
```bash
curl -X GET http://localhost:8000/api/approvals/1/ \
  -H "Authorization: Token $TOKEN" | jq .
```

### 4.5 Approve Request
```bash
curl -X POST http://localhost:8000/api/approvals/1/approve/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "comments": "Approved! All details look good."
  }' | jq .
```

### 4.6 Reject Request
```bash
curl -X POST http://localhost:8000/api/approvals/1/reject/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "comments": "Need additional documentation."
  }' | jq .
```

### 4.7 Get Pending Approvals (for current user)
```bash
curl -X GET http://localhost:8000/api/approvals/pending/ \
  -H "Authorization: Token $TOKEN" | jq .
```

### 4.8 Get Approval Statistics
```bash
curl -X GET http://localhost:8000/api/approvals/statistics/ \
  -H "Authorization: Token $TOKEN" | jq .
```

**Expected Response**:
```json
{
  "total_created": 5,
  "pending_to_check": 2,
  "approved": 2,
  "rejected": 1
}
```

### 4.9 Get Approvals Created by Me
```bash
curl -X GET http://localhost:8000/api/approvals/created-by-me/ \
  -H "Authorization: Token $TOKEN" | jq .
```

### 4.10 Get Approvals Assigned to Me
```bash
curl -X GET http://localhost:8000/api/approvals/assigned-to-me/ \
  -H "Authorization: Token $TOKEN" | jq .
```

---

## 5. Advanced Testing Scenarios

### 5.1 Complete Workflow - Create User via Approval
```bash
# 1. Create approval request for new user
APPROVAL=$(curl -s -X POST http://localhost:8000/api/approvals/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action_type": "CREATE_USER",
    "payload": {
      "username": "workflow_test",
      "email": "workflow@example.com",
      "first_name": "Workflow",
      "last_name": "Test"
    }
  }')

APPROVAL_ID=$(echo $APPROVAL | jq -r '.id')
echo "Created approval: $APPROVAL_ID"

# 2. View the pending approval
curl -s -X GET http://localhost:8000/api/approvals/$APPROVAL_ID/ \
  -H "Authorization: Token $TOKEN" | jq .

# 3. Approve the request (as checker user)
curl -s -X POST http://localhost:8000/api/approvals/$APPROVAL_ID/approve/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"comments": "Creating user as approved"}' | jq .
```

### 5.2 Hierarchy Navigation
```bash
# 1. Get all units in tree
curl -s -X GET 'http://localhost:8000/api/units/' \
  -H "Authorization: Token $TOKEN" | jq '.results[] | {id, name, code, unit_type, parent}'

# 2. For each unit, get its hierarchy
UNIT_ID=2
curl -s -X GET http://localhost:8000/api/units/$UNIT_ID/parent-chain/ \
  -H "Authorization: Token $TOKEN" | jq '.[] | {id, name, code}'

# 3. Get all users under a unit
curl -s -X GET http://localhost:8000/api/units/$UNIT_ID/users/ \
  -H "Authorization: Token $TOKEN" | jq '.[] | {id, username, designation}'
```

### 5.3 Role-Based Queries
```bash
# Get all MAKER users
curl -s -X GET 'http://localhost:8000/api/users/?search=maker' \
  -H "Authorization: Token $TOKEN" | jq '.results[] | {username, roles}'

# Get all users with ADMIN role
curl -s -X GET 'http://localhost:8000/api/users/' \
  -H "Authorization: Token $TOKEN" | jq '.results[] | select(.roles[].name == "ADMIN") | {username, roles}'
```

---

## 6. Pagination and Filtering

### 6.1 Pagination
```bash
# Get page 2 with 10 items per page
curl -X GET 'http://localhost:8000/api/users/?page=2' \
  -H "Authorization: Token $TOKEN" | jq '{count: .count, next: .next, results: (.results | length)}'
```

### 6.2 Complex Filtering
```bash
# Active users in unit 1, ordered by username
curl -X GET 'http://localhost:8000/api/users/?unit=1&is_active=true&ordering=username' \
  -H "Authorization: Token $TOKEN" | jq .

# PENDING approvals, ordered by creation date (newest first)
curl -X GET 'http://localhost:8000/api/approvals/?status=PENDING&ordering=-created_at' \
  -H "Authorization: Token $TOKEN" | jq .
```

---

## 7. Error Handling Tests

### 7.1 Missing Authorization
```bash
curl -X GET http://localhost:8000/api/units/ \
  -H "Content-Type: application/json"
```

**Expected Response**: 401 Unauthorized

### 7.2 Invalid Token
```bash
curl -X GET http://localhost:8000/api/units/ \
  -H "Authorization: Token invalid_token_123"
```

**Expected Response**: 401 Unauthorized

### 7.3 Non-existent Resource
```bash
curl -X GET http://localhost:8000/api/users/99999/ \
  -H "Authorization: Token $TOKEN"
```

**Expected Response**: 404 Not Found

### 7.4 Invalid Data
```bash
curl -X POST http://localhost:8000/api/users/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test",
    "password": "short"
  }'
```

**Expected Response**: 400 Bad Request with validation errors

---

## 8. Batch Operations

### 8.1 Create Multiple Users
```bash
for i in {1..5}; do
  curl -s -X POST http://localhost:8000/api/users/ \
    -H "Authorization: Token $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"username\": \"user_$i\",
      \"email\": \"user$i@example.com\",
      \"first_name\": \"User\",
      \"last_name\": \"$i\",
      \"employee_id\": \"EMP00$i\",
      \"designation\": \"Officer\",
      \"unit_id\": 1,
      \"role_ids\": [3],
      \"password\": \"SecurePass@123\",
      \"password_confirm\": \"SecurePass@123\"
    }" | jq '.username'
done
```

### 8.2 Approve All Pending (if you're the checker)
```bash
curl -s -X GET 'http://localhost:8000/api/approvals/?status=PENDING' \
  -H "Authorization: Token $TOKEN" | jq '.results[] | .id' | while read id; do
  curl -s -X POST http://localhost:8000/api/approvals/$id/approve/ \
    -H "Authorization: Token $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"comments": "Auto-approved"}' | jq '.id, .status'
done
```

---

## Tips & Tricks

### Pretty Print JSON
```bash
curl -s ... | jq .
curl -s ... | python -m json.tool
```

### Extract Specific Fields
```bash
curl -s ... | jq '.results[] | {id, username, email}'
```

### Count Results
```bash
curl -s ... | jq '.results | length'
```

### Filter Results
```bash
curl -s ... | jq '.results[] | select(.is_active == true)'
```

### Save to File
```bash
curl -s ... | jq . > results.json
```

### Test with File Input
```bash
curl -X POST http://localhost:8000/api/users/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d @user_data.json
```

---

## Postman Collection Alternative

Instead of cURL, you can import these as Postman requests:
1. New -> Workspace -> Create Collection
2. Create requests for each endpoint
3. Use Variables for {{TOKEN}} and {{BASE_URL}}
4. Create pre-request scripts to extract tokens
5. Save and share the collection

---

## Performance Testing

```bash
# Load test - Create 100 users quickly
time for i in {1..100}; do
  curl -s -X POST http://localhost:8000/api/users/ \
    -H "Authorization: Token $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{...}" > /dev/null &
done
wait
```

---

## Next Steps

1. ✅ Try basic authentication
2. ✅ Explore unit hierarchy
3. ✅ Create and manage users
4. ✅ Create approval requests
5. ✅ Complete full workflow
6. ✅ Test error scenarios
7. ✅ Performance test if needed

---

Last Updated: January 8, 2025
