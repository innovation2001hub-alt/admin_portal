# Frontend Implementation Guide - Approval Workflow

## Overview

The frontend has been completely implemented with all components for MAKER, CHECKER, and ADMIN roles to work with the Maker-Checker approval workflow system.

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Dashboard.jsx (Main dashboard with role-based tabs)
│   │   ├── Dashboard.css
│   │   ├── ApprovalWorkflow.css (Comprehensive styling)
│   │   ├── Login.jsx
│   │   ├── Login.css
│   │   ├── ProtectedRoute.jsx
│   │   │
│   │   ├── Shared Components/
│   │   ├── StatusBadge.jsx (Status display with colors)
│   │   ├── AuditTrail.jsx (Workflow history display)
│   │   ├── UnitHierarchy.jsx (Unit hierarchy visualization)
│   │   ├── LoadingSpinner.jsx (Loading state)
│   │   ├── ErrorAlert.jsx (Error message display)
│   │   ├── SuccessAlert.jsx (Success message display)
│   │   │
│   │   ├── MAKER Components/
│   │   ├── CreateRequestForm.jsx (Create new requests)
│   │   ├── MyRequestsList.jsx (View own requests)
│   │   │
│   │   ├── CHECKER Components/
│   │   ├── ApprovalQueue.jsx (Pending approvals list)
│   │   ├── RequestReview.jsx (Review and approve/reject)
│   │   │
│   │   └── ADMIN Components/
│   │       ├── AllRequests.jsx (View all requests)
│   │       └── ApprovalMetrics.jsx (System statistics)
│   │
│   ├── context/
│   │   └── AuthContext.jsx (Authentication + role helpers)
│   │
│   └── services/
│       └── api.js (API endpoints for approvals)
│
├── package.json
├── vite.config.js
└── index.html
```

## Components Overview

### 1. Shared Components

#### StatusBadge.jsx
- Displays approval status with color coding
- Statuses: PENDING (yellow), APPROVED (green), REJECTED (red)
- **Usage**: `<StatusBadge status={request.status} />`

#### AuditTrail.jsx
- Shows workflow history with timeline visualization
- Displays: Action, performer, timestamp, remarks
- **Usage**: `<AuditTrail logs={request.logs} />`

#### UnitHierarchy.jsx
- Visualizes organizational unit hierarchy
- Shows path: HO → Circle → Region → Branch
- **Usage**: `<UnitHierarchy unit={request.maker_unit} />`

#### LoadingSpinner.jsx
- Loading state component with animation
- Sizes: small, medium, large
- **Usage**: `<LoadingSpinner text="Loading..." />`

#### ErrorAlert.jsx
- Error notification with close button
- **Usage**: `<ErrorAlert message={error} onClose={() => setError('')} />`

#### SuccessAlert.jsx
- Success notification with close button
- **Usage**: `<SuccessAlert message={success} onClose={() => setSuccess('')} />`

### 2. MAKER Components

#### CreateRequestForm.jsx
- Form to create new approval requests
- Fields:
  - Request Type (dropdown)
  - Title (text)
  - Description (textarea)
  - Payload (JSON, optional)
- Validation:
  - All required fields must be filled
  - Payload must be valid JSON
- API Call: `POST /api/approvals/`
- Features:
  - Auto-routing to checker
  - Success feedback
  - Form reset on success

**Usage**:
```jsx
<CreateRequestForm onSuccess={() => setCurrentTab('my-requests')} />
```

#### MyRequestsList.jsx
- Displays all requests created by the maker
- Features:
  - Status filtering
  - Request details modal
  - Workflow audit trail
  - Review information display
- API Call: `GET /api/approvals/my-requests/`

**Usage**:
```jsx
<MyRequestsList />
```

### 3. CHECKER Components

#### ApprovalQueue.jsx
- List of pending requests for approval
- Features:
  - Card-based layout
  - Shows maker, unit hierarchy, request details
  - Request count stat
  - Refresh functionality
- API Call: `GET /api/approvals/pending-queue/`

**Usage**:
```jsx
<ApprovalQueue onSelectRequest={(request) => setSelectedRequest(request)} />
```

#### RequestReview.jsx
- Modal for reviewing and approving/rejecting requests
- Features:
  - Full request details
  - Maker information with unit hierarchy
  - Request payload display
  - Workflow history
  - Remarks field (required)
  - Approve/Reject buttons
- API Calls:
  - `POST /api/approvals/{id}/approve/`
  - `POST /api/approvals/{id}/reject/`

**Usage**:
```jsx
<RequestReview
  request={selectedRequest}
  onClose={() => setSelectedRequest(null)}
  onApproveReject={handleRefresh}
/>
```

### 4. ADMIN Components

#### AllRequests.jsx
- View all requests in the system
- Features:
  - Advanced filtering (status, request type)
  - Table layout
  - Request details modal
  - Search and sort
  - Full audit trail
- API Call: `GET /api/approvals/`

**Usage**:
```jsx
<AllRequests />
```

#### ApprovalMetrics.jsx
- System-wide statistics dashboard
- Displays:
  - Total requests
  - Pending count
  - Approved count
  - Rejected count
  - Percentages
  - Progress bars
- API Call: `GET /api/approvals/statistics/`

**Usage**:
```jsx
<ApprovalMetrics />
```

### 5. Main Dashboard Component

The updated `Dashboard.jsx` now:
- Detects user roles automatically
- Renders role-based tabs
- Shows appropriate components per role
- Handles request selection and modal display
- Auto-refreshes lists after approve/reject

**Role Tab Mapping**:
- **MAKER**:
  - Create Request
  - My Requests
- **CHECKER**:
  - Approval Queue
- **ADMIN**:
  - Create Request (optional)
  - My Requests (optional)
  - Approval Queue
  - All Requests
  - Metrics

## API Integration

All components use the `approvalsAPI` service from `src/services/api.js`:

### Available Endpoints

```javascript
// Create new request
approvalsAPI.create(requestType, title, description, payload)

// Get all requests
approvalsAPI.getAll(filters)

// Get single request
approvalsAPI.get(id)

// Get my requests (MAKER)
approvalsAPI.getMyRequests()

// Get pending queue (CHECKER)
approvalsAPI.getPendingQueue()

// Get statistics
approvalsAPI.getStatistics()

// Approve request
approvalsAPI.approve(id, remarks)

// Reject request
approvalsAPI.reject(id, remarks)
```

## Authentication Context

Enhanced `AuthContext.jsx` now includes role-checking helpers:

```javascript
const { user, isMaker, isChecker, isAdmin, hasRole, hasAnyRole } = useAuth();

if (isMaker()) {
  // Show maker components
}

if (isChecker()) {
  // Show checker components
}

if (isAdmin()) {
  // Show admin components
}
```

## Styling

All components use the comprehensive styling system:

### Main Stylesheets
- `Dashboard.css` - Main dashboard styling
- `ApprovalWorkflow.css` - All workflow-related components

### CSS Classes Available
- `.form-card`, `.list-card` - Card containers
- `.btn`, `.btn-primary`, `.btn-secondary`, `.btn-success`, `.btn-danger` - Buttons
- `.status-badge` - Status badges
- `.audit-trail` - Audit trail display
- `.modal-content`, `.modal-overlay` - Modal styling
- `.requests-table`, `.requests-grid` - List layouts
- `.metrics-grid`, `.metric-card` - Metrics display
- `.tabs-header`, `.tab-button` - Tab navigation

## Features Implemented

### MAKER Features
✅ Create new approval requests
✅ View all own requests
✅ Filter requests by status
✅ View request details
✅ See approval status
✅ View remarks from checker
✅ View complete audit trail
✅ Track request lifecycle

### CHECKER Features
✅ View pending approval queue
✅ Filter by unit hierarchy
✅ Review full request details
✅ Approve requests with remarks
✅ Reject requests with remarks
✅ View maker information and unit
✅ See request payload
✅ View request history

### ADMIN Features
✅ View all requests system-wide
✅ Filter by status and type
✅ Search through all requests
✅ View request details
✅ See audit trails
✅ Access approval metrics
✅ Monitor approval rates
✅ System oversight

## State Management

Components use React hooks for state management:
- `useState` for component-level state
- `useEffect` for data fetching
- `useAuth` for authentication context
- `useNavigate` for routing

## Error Handling

All components include:
- Try-catch blocks for API calls
- Error state display
- Error alerts with dismiss
- Loading states
- Graceful fallbacks

## Loading States

All API calls show loading indicators:
- Loading spinner during fetch
- Disabled buttons during submission
- Loading text feedback

## Responsive Design

All components are responsive:
- Mobile: 480px and below
- Tablet: 481px to 768px
- Desktop: 769px and above

Media queries adjust:
- Grid layouts
- Modal sizes
- Font sizes
- Button sizing
- Table display

## Key Features

### Auto-Routing
- Requests automatically routed to appropriate checker based on unit hierarchy
- No manual assignment needed

### Role-Based Access
- MAKER: Can only create and view own requests
- CHECKER: Can only see requests from their units
- ADMIN: Can see everything

### Unit Hierarchy Display
- Shows complete organizational path
- Helps understand approval routing
- Visual hierarchy in UI

### Audit Trail
- Complete workflow history
- Timestamps for all actions
- Remarks from reviewers
- Visual timeline

### Real-time Updates
- Refresh buttons on all lists
- Auto-refresh after approve/reject
- List pagination ready

## Setup Instructions

### Installation

```bash
cd frontend
npm install
```

### Environment Configuration

Create `.env` file:
```env
VITE_API_URL=http://127.0.0.1:8000/api
```

### Development Server

```bash
npm run dev
```

Server runs on: http://localhost:5173

### Production Build

```bash
npm run build
```

## Testing the Workflow

### Test Scenario 1: Create & Approve

1. Login as MAKER
2. Go to "Create Request" tab
3. Fill form and submit
4. Should see success message
5. Switch to "My Requests" tab
6. Verify request appears with PENDING status
7. Login as CHECKER (different window)
8. Go to "Approval Queue"
9. Click "Review & Approve"
10. Add remarks and click "Approve"
11. Verify success message
12. Original MAKER can now see APPROVED status

### Test Scenario 2: Rejection

1. Login as MAKER, create request
2. Login as CHECKER
3. Go to "Approval Queue"
4. Click "Review & Approve"
5. Add remarks and click "Reject"
6. Verify MAKER can see REJECTED status with remarks

### Test Scenario 3: Admin Oversight

1. Login as ADMIN
2. Go to "All Requests" tab
3. Verify all requests visible
4. Apply filters
5. Go to "Metrics" tab
6. Verify statistics display

## Troubleshooting

### Requests Not Showing
- Check API URL in `.env`
- Verify backend is running
- Check authentication token
- See browser console for errors

### Auto-Routing Not Working
- Verify unit hierarchy set up in backend
- Check user unit assignments
- Verify CHECKER role users exist

### Styles Not Applied
- Clear browser cache
- Restart dev server
- Check ApprovalWorkflow.css import

### API Errors
- Verify backend endpoints
- Check authentication token
- Review API documentation
- Check browser console

## Performance Optimization

Implemented optimizations:
- Component lazy loading ready
- List pagination support
- Efficient re-renders with React hooks
- CSS transitions for smooth UX
- Debounced filters ready

## Future Enhancements

Potential features to add:
- Email notifications
- Multi-level approvals
- Delegation of reviews
- Batch operations
- Advanced search
- Export to CSV
- Dashboard widgets
- Real-time notifications
- SLA tracking
- Comments/discussions

## Browser Support

Tested on:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Dependencies

See `package.json` for all dependencies:
- React 18+
- React Router 6+
- Axios (for API calls)
- Vite (build tool)

