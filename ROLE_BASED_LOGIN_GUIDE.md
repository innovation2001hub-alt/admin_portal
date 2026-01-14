# Role-Based Login & Dashboard Implementation Guide

## Overview
This document describes the complete role-based authentication and dashboard system integrated into Django Admin Portal and custom web views.

---

## What Was Implemented

### 1. **Role-Based Login Flow**
- Custom login view at `/login/` that accepts username or employee_id
- After successful authentication, users are automatically redirected to their role-based dashboard:
  - **ADMIN** → `/admin/dashboard/`
  - **MAKER** → `/maker/dashboard/`
  - **CHECKER** → `/checker/dashboard/`
- Graceful error handling for missing roles (user not logged in, shown error message)

### 2. **Dashboard Views**
Three protected views with role-based access control:
- `AdminDashboardView` - Only ADMIN role
- `MakerDashboardView` - Only MAKER role
- `CheckerDashboardView` - Only CHECKER role

### 3. **Access Control**
#### Decorator
```python
@role_required("ADMIN")
def my_view(request):
    pass
```

#### Mixin for Class-Based Views
```python
class MyAdminView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    allowed_roles = ["ADMIN"]
```

### 4. **Middleware Protection**
`RoleBasedDashboardRedirectMiddleware` ensures that:
- If a user tries to access a dashboard URL not matching their role, they're redirected to their allowed dashboard
- Works silently in the background

### 5. **Utility Functions**
- `get_primary_role_name(user)` → Returns the user's primary role name
- `get_dashboard_url(user)` → Returns the correct dashboard URL based on role

### 6. **Django Admin Panel Enhancements**

#### Role Admin
- Shows role names with **color badges** (ADMIN=red, MAKER=blue, CHECKER=green)
- Displays count of users assigned to each role
- Full CRUD operations for role management

#### User Admin
- **Roles column** with color-coded badges in list view
- **Dashboard column** with direct links to each user's dashboard
- **Dashboard Access fieldset** showing:
  - Assigned role information with descriptions
  - Dashboard URL
  - One-click link to open the user's dashboard
- **Role Information display** in detail view
- Optimized queries with `select_related()` and `prefetch_related()`

#### Admin Site Customization
- Custom site header and title
- Admin index page includes quick dashboard link (if staff/superuser has a role)
- Clean, consistent styling with badges

---

## File Structure

```
admin_core/
├── utils.py                          # NEW: Role utilities & URL mapping
├── decorators.py                     # NEW: role_required decorator & RoleRequiredMixin
├── middleware.py                     # NEW: RoleBasedDashboardRedirectMiddleware
├── views/
│   └── web_views.py                  # NEW: login_view, logout_view, dashboard views
├── admin.py                          # UPDATED: Enhanced Role/User admin
├── apps.py                           # UPDATED: Admin site customization
├── templates/
│   ├── login.html                    # NEW: Login page
│   ├── admin/
│   │   ├── index.html                # NEW: Admin index with dashboard links
│   │   └── dashboard.html            # NEW: Admin dashboard
│   ├── maker/
│   │   └── dashboard.html            # NEW: Maker dashboard
│   └── checker/
│       └── dashboard.html            # NEW: Checker dashboard
└── urls.py                           # (no changes needed for web routes)

admin_portal/
├── urls.py                           # UPDATED: Added web auth & dashboard routes
└── settings.py                       # UPDATED: Registered middleware & template dirs
```

---

## URL Routes

| URL | View | Role | Notes |
|-----|------|------|-------|
| `/login/` | `login_view` (GET, POST) | PUBLIC | Accept username or employee_id |
| `/logout/` | `logout_view` (GET) | Authenticated | Clear session |
| `/admin/dashboard/` | `AdminDashboardView` | ADMIN | Protected by mixin + middleware |
| `/maker/dashboard/` | `MakerDashboardView` | MAKER | Protected by mixin + middleware |
| `/checker/dashboard/` | `CheckerDashboardView` | CHECKER | Protected by mixin + middleware |

---

## How to Use

### 1. **Create Roles (if not already done)**
```bash
cd admin_portal
python manage.py shell
```

```python
from admin_core.models import Role

Role.objects.get_or_create(
    name="ADMIN",
    defaults={"description": "Administrator role with full access"}
)
Role.objects.get_or_create(
    name="MAKER",
    defaults={"description": "Maker role for creating requests"}
)
Role.objects.get_or_create(
    name="CHECKER",
    defaults={"description": "Checker role for approving requests"}
)
```

### 2. **Assign Roles to Users**
In Django Admin (`/admin/`):
1. Go to **Users**
2. Select a user
3. In **Roles & Assignments**, check the desired role(s)
4. Save

Or via shell:
```python
from admin_core.models import User, Role

user = User.objects.get(username="john")
admin_role = Role.objects.get(name="ADMIN")
user.roles.add(admin_role)
```

### 3. **Test Login**
1. Start server: `python manage.py runserver`
2. Visit: `http://127.0.0.1:8000/login/`
3. Enter username/employee_id and password
4. User redirects to their dashboard based on role
5. Try accessing another role's dashboard → redirected back

### 4. **Access Dashboard from Admin**
- In User list view, click the **Dashboard** link in the rightmost column
- Opens user's dashboard in new tab based on their role
- Quick link also available on Admin index page

---

## Features

✅ **Role-Based Redirection** - Login automatically routes to correct dashboard  
✅ **Access Control** - Unauthorized role access is blocked & redirected  
✅ **Middleware Fallback** - Extra layer of protection for direct URL access  
✅ **Admin Integration** - Full dashboard access from admin panel  
✅ **Color Badges** - Visual role identification (ADMIN=red, MAKER=blue, CHECKER=green)  
✅ **Helper Functions** - `get_primary_role_name()`, `get_dashboard_url()`  
✅ **Graceful Error Handling** - Missing roles show friendly messages  
✅ **Production-Ready Code** - Clean, documented, optimized queries  

---

## Error Scenarios

| Scenario | Behavior |
|----------|----------|
| User logs in with no role | Error message shown, not logged in |
| User tries to access wrong dashboard | Redirected to their allowed dashboard + warning message |
| User account deactivated | Cannot login, cannot access dashboards |
| Multiple roles assigned | Uses first role alphabetically |
| Super user/staff access | Can access all sections of admin panel |

---

## Customization

### Change Dashboard Template
Edit [admin_core/templates/{admin,maker,checker}/dashboard.html](admin_core/templates/{admin,maker,checker}/dashboard.html)

### Add New Role
```python
# In models/role.py (if adding new roles)
# In utils.py - add new constant and update ROLE_DASHBOARD_MAP
# In decorators.py - update allowed_roles
```

### Customize Role Colors
Edit color mappings in:
- `admin_core/admin.py` - Admin list/detail views
- Modify hex color codes in the `colors` dict

### Change Dashboard URLs
Edit URL patterns in [admin_portal/urls.py](admin_portal/urls.py)

---

## Dependencies

All required packages are already in your `requirements.txt`:
- Django 6.0.1
- Django REST Framework
- All auth/session middleware included

No additional packages needed!

---

## Production Notes

1. **Sessions** - Uses Django session framework (cookie-based)
2. **CSRF Protection** - Enabled on all POST requests
3. **Login Redirect** - Configurable via `LOGIN_URL` setting if needed
4. **Message Framework** - Uses Django's messages system
5. **Logging** - All failed login attempts should be logged (implement in service layer)

---

## Testing Checklist

- [ ] Create 3 test users with different roles
- [ ] Login as each role and verify correct dashboard loads
- [ ] Try accessing another role's dashboard (should redirect)
- [ ] Logout and verify redirect to login page
- [ ] Access admin panel and verify dashboard links work
- [ ] Deactivate a user and verify they can't login
- [ ] Check role badges render with correct colors
- [ ] Test with multiple browser tabs (session management)

---

## Files Changed Summary

| File | Changes | Type |
|------|---------|------|
| `admin_core/utils.py` | Created | NEW |
| `admin_core/decorators.py` | Created | NEW |
| `admin_core/middleware.py` | Created | NEW |
| `admin_core/views/web_views.py` | Created | NEW |
| `admin_core/admin.py` | Enhanced role/user admin + imports | UPDATED |
| `admin_core/apps.py` | Admin site customization | UPDATED |
| `admin_portal/urls.py` | Added web auth + dashboard routes | UPDATED |
| `admin_portal/settings.py` | Registered middleware | UPDATED |
| `admin_core/templates/login.html` | Created | NEW |
| `admin_core/templates/admin/index.html` | Created | NEW |
| `admin_core/templates/{admin,maker,checker}/dashboard.html` | Created (3 files) | NEW |

**Total:** 7 files created, 4 files updated = **11 changes**

