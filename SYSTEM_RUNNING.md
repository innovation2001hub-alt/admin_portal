# ✅ Complete System Setup & Running Guide

## 🚀 System Status: RUNNING

### Backend Server
- **Status**: ✅ Running
- **URL**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **API Base**: http://localhost:8000/api

### Frontend Server
- **Status**: ✅ Running
- **URL**: http://localhost:3001
- **Auto-refresh**: Enabled (port 3000 was in use, using 3001)

---

## 📋 Test Credentials

### Administrator Account
```
Username: admin
Password: admin123
Role: Administrator
Unit: Head Office (HO)
Access: All system features, user management, metrics
```

### Maker Accounts (Can Create Requests)
```
MAKER 1:
  Username: maker_delhi_2
  Password: maker123
  Name: Rajesh Kumar
  Unit: Branch - Delhi
  
MAKER 2:
  Username: maker_mumbai_2
  Password: maker123
  Name: Priya Sharma
  Unit: Branch - Mumbai
```

### Checker Accounts (Can Approve/Reject)
```
CHECKER 1:
  Username: checker_ne_2
  Password: checker123
  Name: Amit Singh
  Unit: Region - Northeast
  
CHECKER 2:
  Username: checker_nw_2
  Password: checker123
  Name: Vikram Patel
  Unit: Region - Northwest
  
CHECKER 3:
  Username: checker_circle_2
  Password: checker123
  Name: Deepak Verma
  Unit: Circle - North
```

---

## 🌐 Unit Hierarchy

```
Head Office (HO)
├── Circle - North
│   ├── Region - Northeast (checker_ne)
│   └── Region - Northwest (checker_nw)
│       └── Branch - Delhi (maker_delhi)
└── Circle - South
    └── Branch - Mumbai (maker_mumbai)
```

**Approval Routing Logic:**
- Requests from Branch → auto-routed to Region Checker → Circle Checker → HO Admin
- Each checker can approve/reject requests from their subordinate units
- Only assigned checkers can approve requests

---

## 🧪 Complete End-to-End Test Workflow

### Step 1: Login as MAKER (Rajesh Kumar)
1. Go to http://localhost:3001
2. Enter credentials:
   - Employee ID: maker_delhi (or username: maker_delhi)
   - Password: maker123
3. Click "Sign In"

### Step 2: Create an Approval Request
1. Go to "Create Request" tab
2. Fill in the form:
   - **Request Type**: Select "Create New User"
   - **Title**: "Add New Employee"
   - **Description**: "Need to create account for John Doe, Software Engineer"
   - **Payload** (optional): `{"name": "John Doe", "email": "john@example.com"}`
3. Click "Submit Request"
4. See success message with request ID
5. Go to "My Requests" tab to see the request status (should be PENDING)

### Step 3: Approve as CHECKER (Vikram Patel)
1. Open new browser window or logout
2. Go to http://localhost:3001
3. Login as checker_nw_2 (Vikram Patel):
   - Employee ID: checker_nw_2
   - Password: checker123
4. Go to "Approval Queue" tab
5. See the pending request from Rajesh Kumar
6. Click "Review & Approve"
7. In the modal:
   - Review all request details
   - See maker unit hierarchy
   - Add remarks: "Approved for processing"
   - Click "✓ Approve"
8. See success message

### Step 4: Check Result as MAKER
1. Switch back to maker_delhi_2 browser/window
2. Go to "My Requests" tab
3. Refresh the page
4. See request status changed to "APPROVED"
5. Click "View" to see reviewer remarks and full audit trail

### Step 5: Try Rejection Workflow
1. Login as maker_mumbai_2:
   - Employee ID: maker_mumbai_2
   - Password: maker123
2. Create another request for "Delete User"
3. Login as checker_ne_2 (Amit Singh):
   - Employee ID: checker_ne_2
   - Password: checker123
4. Go to Approval Queue
5. Review the request and click "✕ Reject"
6. Add remarks: "Insufficient information provided"
7. Click "✕ Reject"
8. Switch back to maker_mumbai and verify status is "REJECTED" with remarks

### Step 6: Admin Dashboard
1. Login as admin:
   - Employee ID: admin
   - Password: admin123
2. Go to "All Requests" tab
   - See all requests from all makers
   - Filter by status or request type
   - Click view to see full details
3. Go to "Metrics" tab
   - See total requests: 2
   - See approved: 1
   - See rejected: 1
   - See approval/rejection rates

---

## 🔧 Backend Django Admin

Access at: http://localhost:8000/admin

**Login with admin credentials:**
- Username: admin
- Password: admin123

**Available Features:**
- Manage Users and Roles
- View Organizational Units
- View/Monitor Approval Requests
- See Approval Logs with full audit trail
- View Audit Logs for all system actions

---

## 📊 API Endpoints (Use Postman or curl)

### Authentication
```bash
# Login
POST http://localhost:8000/api/auth/login/
Content-Type: application/json

{
  "employee_id": "maker_delhi_2",
  "password": "maker123"
}

# Response includes token
{
  "token": "abc123...",
  "user": {...}
}
```

### Approval Endpoints
```bash
# All endpoints require Authorization header:
# Authorization: Token abc123...

# Create approval request
POST /api/approvals/
{
  "request_type": "CREATE_USER",
  "title": "Add New User",
  "description": "...",
  "payload": {}
}

# Get my requests (MAKER)
GET /api/approvals/my-requests/

# Get pending queue (CHECKER)
GET /api/approvals/pending-queue/

# Get all requests (ADMIN)
GET /api/approvals/

# Get single request
GET /api/approvals/{id}/

# Approve request
POST /api/approvals/{id}/approve/
{
  "remarks": "Approved"
}

# Reject request
POST /api/approvals/{id}/reject/
{
  "remarks": "Need more info"
}

# Get statistics
GET /api/approvals/statistics/
```

---

## 🐛 Troubleshooting

### Frontend Not Loading
- Check if port 3001 is open
- Clear browser cache (Ctrl+Shift+Delete)
- Restart frontend: `npm run dev`

### Cannot Login
- Verify credentials in Test Credentials section
- Check backend is running (http://localhost:8000)
- See browser console for error messages

### API Errors
- Check backend console for detailed errors
- Verify Authorization token is valid
- Check request payload format matches API spec

### Database Issues
- Delete `db.sqlite3` and run migrations again
- Run `setup_test_data.py` to recreate test data

### Port Already in Use
- Change Django port: `python manage.py runserver 0.0.0.0:8001`
- Change Vite port: `npm run dev -- --port 3002`

---

## 📁 Project Structure

```
admin_portal/
├── admin_portal/                 # Django project settings
│   ├── settings.py              # Project configuration
│   ├── urls.py                  # URL routing
│   └── wsgi.py                  # Production WSGI
│
├── admin_core/                   # Main Django app
│   ├── models/
│   │   ├── user.py              # Custom User model
│   │   ├── hierarchy.py         # Unit hierarchy
│   │   ├── role.py              # Role model
│   │   └── workflow.py          # ApprovalRequest, ApprovalLog
│   ├── views/
│   │   ├── auth_views.py        # Authentication
│   │   ├── approval_views.py    # Approval endpoints
│   │   └── user_views.py        # User management
│   ├── services/
│   │   └── approval_service.py  # Business logic
│   ├── serializers/
│   │   └── approval_serializer.py  # API serializers
│   └── admin.py                 # Django admin
│
├── frontend/                     # React app
│   ├── src/
│   │   ├── components/          # All React components
│   │   ├── context/             # AuthContext
│   │   ├── services/            # API service (api.js)
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
│
├── db.sqlite3                    # SQLite database
└── manage.py                     # Django management
```

---

## 🚀 Next Steps

### To Stop Servers
Press `CTRL+C` in the terminal running the server

### To Restart
1. Backend: `python manage.py runserver 0.0.0.0:8000`
2. Frontend: `npm run dev`

### To Reset Everything
1. Delete `db.sqlite3`
2. Run migrations: `python manage.py migrate`
3. Setup test data: `python setup_test_data.py`
4. Restart servers

### To Add More Test Data
Edit `setup_test_data.py` and add more users/units, then run it again

### To Deploy to Production
1. See DEPLOYMENT.md (coming soon)
2. Configure environment variables
3. Use proper WSGI server (Gunicorn)
4. Build and optimize frontend: `npm run build`

---

## ✨ System Features Implemented

✅ **Backend (Django)**
- Complete approval workflow system
- Unit hierarchy-based routing
- Role-based access control (RBAC)
- RESTful API with token authentication
- Comprehensive audit logging
- Database migrations and models
- Django admin integration

✅ **Frontend (React)**
- Role-based dashboard (MAKER/CHECKER/ADMIN)
- Request creation form
- My requests list with filtering
- Approval queue for checkers
- Request review and decision modal
- System metrics and statistics
- Audit trail visualization
- Unit hierarchy display
- Responsive design
- Error handling and loading states

✅ **Database**
- Unit hierarchy management
- User roles and permissions
- Approval workflow tracking
- Audit logging for compliance
- Proper indexing for performance

---

## 📞 Support

For issues or questions:
1. Check the documentation files
2. Review test credentials
3. Check browser console for errors
4. Check backend console/logs
5. Verify all services are running

---

## 🎉 Ready to Go!

The system is now **fully functional** and ready for testing. Use the test credentials above to explore all features. Enjoy! 🚀

