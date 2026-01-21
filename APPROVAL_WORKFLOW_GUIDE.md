# Approval Workflow Implementation Guide

## Overview

This document describes the complete Maker-Checker approval workflow with unit hierarchy-based routing implemented in the system.

## Architecture

### 1. Unit Hierarchy Model

**Location**: [models/hierarchy.py](admin_core/models/hierarchy.py)

The `Unit` model implements organizational hierarchy:

```python
# Example Structure:
HO (Head Office)
├── Circle 1
│   ├── Region 1.1
│   │   ├── Branch 1.1.1
│   │   └── Branch 1.1.2
│   └── Region 1.2
└── Circle 2
```

**Key Methods**:
- `get_ancestors()`: Get all parent units above this unit
- `get_descendants()`: Get all child units below this unit
- `is_ancestor_of(unit)`: Check if this unit is parent of given unit
- `is_descendant_of(unit)`: Check if this unit is child of given unit
- `get_eligible_checkers()`: Get CHECKER users from ancestor units

### 2. ApprovalRequest Model

**Location**: [models/workflow.py](admin_core/models/workflow.py)

Fields:
- `created_by`: MAKER user who created the request
- `maker_unit`: Unit of the maker (for hierarchy routing)
- `request_type`: Type of request (e.g., 'CREATE_USER', 'UPDATE_HIERARCHY')
- `title`: Short title of request
- `description`: Detailed description
- `payload`: JSON data for the request
- `assigned_checker`: Specific CHECKER assigned to review
- `checker_unit`: Unit of assigned checker (ancestor of maker_unit)
- `status`: PENDING, APPROVED, REJECTED
- `reviewed_by`: The CHECKER who approved/rejected
- `reviewed_at`: Timestamp of review
- `remarks`: Comments from the checker
- `created_at`, `updated_at`: Timestamps

### 3. ApprovalLog Model

**Location**: [models/workflow.py](admin_core/models/workflow.py)

Tracks all approval workflow actions:
- CREATE: Request created
- ASSIGN: Assigned to checker
- APPROVE: Request approved
- REJECT: Request rejected
- RESUBMIT: Request resubmitted
- VIEW: Request viewed

### 4. Approval Service

**Location**: [services/approval_service.py](admin_core/services/approval_service.py)

Core business logic for approval workflow:

```python
# Create a new approval request
approval = ApprovalService.create_approval_request(
    request_type='CREATE_USER',
    title='Add New User',
    description='Create user for new employee',
    payload={'user_data': {...}},
    maker=user_obj
)

# Get requests for makers
approvals = ApprovalService.get_maker_requests(maker)

# Get pending queue for checker
approvals = ApprovalService.get_checker_queue(checker)

# Approve a request
ApprovalService.approve_request(approval, checker, remarks='Approved')

# Reject a request
ApprovalService.reject_request(approval, checker, remarks='Need more details')

# Get statistics
stats = ApprovalService.get_statistics(unit)
```

## Workflow

### MAKER: Creating a Request

```
1. MAKER logs in to the system
2. Navigate to "Create Request" page
3. Fill form with:
   - Request Type
   - Title
   - Description
   - Payload (JSON data)
4. Submit request
5. System:
   - Creates ApprovalRequest with status='PENDING'
   - Sets maker_unit from MAKER's unit
   - Finds eligible CHECKERs in ancestor units
   - Auto-assigns to first available CHECKER
   - Logs action in ApprovalLog
6. MAKER sees: "Submitted for approval to upper unit checker"
```

### CHECKER: Reviewing Requests

```
1. CHECKER logs in to the system
2. Navigate to "Approval Queue"
3. System shows requests where:
   - Status = PENDING
   - Maker's unit is descendant of CHECKER's unit
4. CHECKER clicks "Review Request"
5. CHECKER can:
   - View all request details
   - View maker information + unit
   - Add remarks
   - Click "Approve" or "Reject"
6. System:
   - Updates status to APPROVED/REJECTED
   - Logs reviewed_by, reviewed_at, remarks
   - Logs action in ApprovalLog
   - Sends notification to MAKER
```

### MAKER: Viewing Decision

```
1. MAKER views "My Requests"
2. Sees final status: APPROVED, REJECTED, or PENDING
3. If APPROVED/REJECTED:
   - View reviewer's remarks
   - View review timestamp
4. If PENDING:
   - View assigned checker info
```

## Hierarchy Routing Rules

### Rule 1: Eligible Checkers

A CHECKER is eligible to review a request if:
1. User has CHECKER role
2. User is in an ancestor unit of the maker
3. Request status is PENDING

### Rule 2: Visibility

- **MAKER**: Can only see own requests
- **CHECKER**: Can only see requests from lower units (descendants)
- **ADMIN**: Can see all requests

### Rule 3: Assignment

- When a MAKER creates a request, system auto-finds eligible CHECKERs
- Assigns to first available CHECKER (can be improved with round-robin)
- If no eligible checkers, request stays unassigned (queue-based)

### Rule 4: Prevention

- Makers CANNOT approve their own requests
- Checkers can ONLY approve requests routed to them
- Duplicate approvals prevented by status check

## API Endpoints

### List Approvals
```
GET /api/approvals/
```
Filters based on role:
- ADMIN: All requests
- MAKER: Own requests only
- CHECKER: Requests from lower units

### Create Request (MAKER only)
```
POST /api/approvals/
{
  "request_type": "CREATE_USER",
  "title": "Add New Employee",
  "description": "Create user for John Doe",
  "payload": {
    "employee_id": "PF12345",
    "name": "John Doe"
  }
}
```

### Get Request Details
```
GET /api/approvals/{id}/
```
Shows full details including logs (if eligible)

### Approve Request (CHECKER only)
```
POST /api/approvals/{id}/approve/
{
  "remarks": "Approved as per policy"
}
```

### Reject Request (CHECKER only)
```
POST /api/approvals/{id}/reject/
{
  "remarks": "Missing required documentation"
}
```

### Get My Requests (MAKER)
```
GET /api/approvals/my-requests/
```

### Get Pending Queue (CHECKER)
```
GET /api/approvals/pending-queue/
```

### Get Statistics
```
GET /api/approvals/statistics/
```
Returns counts of total, pending, approved, rejected

## Database Schema

### approval_request table
```sql
CREATE TABLE admin_core_approval_request (
  id BIGINT PRIMARY KEY,
  created_by_id BIGINT NOT NULL,  -- FK User
  maker_unit_id BIGINT,            -- FK Unit
  request_type VARCHAR(100),
  title VARCHAR(200),
  description TEXT,
  payload JSON,
  assigned_checker_id BIGINT,      -- FK User
  checker_unit_id BIGINT,          -- FK Unit
  status VARCHAR(20),              -- PENDING, APPROVED, REJECTED
  reviewed_by_id BIGINT,           -- FK User
  reviewed_at DATETIME,
  remarks TEXT,
  created_at DATETIME,
  updated_at DATETIME,
  
  FOREIGN KEY (created_by_id) REFERENCES admin_core_user(id),
  FOREIGN KEY (maker_unit_id) REFERENCES admin_core_unit(id),
  FOREIGN KEY (assigned_checker_id) REFERENCES admin_core_user(id),
  FOREIGN KEY (checker_unit_id) REFERENCES admin_core_unit(id),
  FOREIGN KEY (reviewed_by_id) REFERENCES admin_core_user(id)
);

CREATE INDEX idx_approval_status_checker 
  ON admin_core_approval_request(status, assigned_checker_id);
CREATE INDEX idx_approval_created_by_status 
  ON admin_core_approval_request(created_by_id, status);
CREATE INDEX idx_approval_maker_unit_status 
  ON admin_core_approval_request(maker_unit_id, status);
```

### approval_log table
```sql
CREATE TABLE admin_core_approval_log (
  id BIGINT PRIMARY KEY,
  approval_request_id BIGINT NOT NULL,  -- FK ApprovalRequest
  action VARCHAR(20),                    -- CREATE, ASSIGN, APPROVE, REJECT, etc.
  performed_by_id BIGINT,               -- FK User (nullable)
  remarks TEXT,
  timestamp DATETIME,
  
  FOREIGN KEY (approval_request_id) REFERENCES admin_core_approval_request(id),
  FOREIGN KEY (performed_by_id) REFERENCES admin_core_user(id)
);
```

## Database Migrations

To create the new schema:

```bash
# Generate migration from models
python manage.py makemigrations admin_core

# Apply migrations
python manage.py migrate admin_core
```

You'll be prompted for field defaults for existing data migration. Choose appropriate defaults or create data migration if needed.

## Testing the Implementation

### Setup Test Data

```python
# Create units
ho = Unit.objects.create(name="Head Office", code="HO001", unit_type="HO")
circle = Unit.objects.create(name="Circle 1", code="C001", unit_type="CIRCLE", parent=ho)
region = Unit.objects.create(name="Region 1.1", code="R001", unit_type="RBO", parent=circle)
branch = Unit.objects.create(name="Branch 1.1.1", code="B001", unit_type="BR", parent=region)

# Create roles
admin_role = Role.objects.create(name="ADMIN", description="Administrator")
maker_role = Role.objects.create(name="MAKER", description="Request Maker")
checker_role = Role.objects.create(name="CHECKER", description="Request Checker")

# Create users
maker = User.objects.create_user(
    username='maker1',
    email='maker@example.com',
    password='pass123',
    employee_id='PF001',
    designation='Officer',
    unit=branch
)
maker.roles.add(maker_role)

checker = User.objects.create_user(
    username='checker1',
    email='checker@example.com',
    password='pass123',
    employee_id='PF002',
    designation='Manager',
    unit=circle
)
checker.roles.add(checker_role)
```

### Test Workflow

```python
from admin_core.services.approval_service import ApprovalService

# MAKER creates request
approval = ApprovalService.create_approval_request(
    request_type='CREATE_USER',
    title='New User',
    description='Create account for John',
    payload={'name': 'John'},
    maker=maker
)
print(f"Created: {approval.id}")
print(f"Status: {approval.status}")
print(f"Assigned to: {approval.assigned_checker.username}")

# CHECKER reviews
ApprovalService.approve_request(approval, checker, remarks='Looks good')
print(f"Approved by: {approval.reviewed_by.username}")
print(f"Status: {approval.status}")

# MAKER views result
requests = ApprovalService.get_maker_requests(maker)
for req in requests:
    print(f"Request: {req.id}, Status: {req.status}, Remarks: {req.remarks}")
```

## Django Admin Configuration

The ApprovalRequest model is registered in Django admin with:
- List display: id, created_by, maker_unit, status, reviewed_by, reviewed_at
- Filters: status, maker_unit, request_type
- Search: request_type, title, created_by__username
- Read-only fields: created_by, maker_unit, request_type, payload, status, reviewed_by
- Permissions: Only ADMIN can view/edit (role-based in admin)

## Frontend Components (React)

### MAKER Components
- `MakerDashboard.jsx`: Overview and navigation
- `CreateRequestForm.jsx`: Create new request
- `MyRequestsList.jsx`: List own requests
- `RequestDetail.jsx`: View request details

### CHECKER Components
- `CheckerDashboard.jsx`: Overview and navigation
- `ApprovalQueue.jsx`: List pending requests
- `RequestReview.jsx`: Review and approve/reject
- `ApprovalHistory.jsx`: View past decisions

### ADMIN Components
- `AdminDashboard.jsx`: System overview
- `AllRequests.jsx`: View all requests
- `ApprovalMetrics.jsx`: Statistics and charts

## Key Features

✅ **Hierarchy-Based Routing**: Requests auto-routed to appropriate checkers
✅ **Role-Based Access**: MAKER/CHECKER/ADMIN permissions enforced
✅ **Audit Trail**: All actions logged in ApprovalLog
✅ **Efficient Queries**: Optimized with select_related and prefetch_related
✅ **Transaction Safety**: Atomic approval/rejection operations
✅ **Validation**: Business rules enforced at model and service levels
✅ **API-First Design**: RESTful endpoints for all operations
✅ **Audit Logging**: Integration with AuditLog for compliance

## Security Considerations

1. **Access Control**: All endpoints validate user role and unit hierarchy
2. **Data Integrity**: Transactions ensure atomic operations
3. **Audit Trail**: All actions logged for compliance
4. **No Self-Approval**: System prevents makers from approving own requests
5. **Rate Limiting**: Consider adding rate limiting for production
6. **Encryption**: Payload field should be encrypted for sensitive data in production

## Performance Optimizations

1. **Database Indexes**: Created on frequently filtered columns
2. **Query Optimization**: Using select_related and prefetch_related
3. **Caching**: Consider caching hierarchy relationships
4. **Pagination**: List endpoints paginate by default
5. **Filtering**: Use filterset_fields for efficient queries

## Future Enhancements

1. **Delegation**: Allow checkers to delegate reviews
2. **Multi-Step Approval**: Route to multiple checkers
3. **SLA Tracking**: Track approval times and set reminders
4. **Notifications**: Email/SMS notifications for stakeholders
5. **Comments**: Allow back-and-forth comments between maker and checker
6. **Batch Operations**: Bulk approve/reject similar requests
7. **Analytics**: Dashboard with approval metrics and trends
8. **Integration**: Integrate with external systems via webhooks

