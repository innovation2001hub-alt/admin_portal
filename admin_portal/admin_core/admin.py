from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe
from django.urls import reverse
from django import forms
from .models import User, Unit, Role, ApprovalRequest, ApprovalLog, AuditLog
from .utils import (
    get_primary_role_name,
    get_dashboard_url,
    ROLE_ADMIN,
    ROLE_MAKER,
    ROLE_CHECKER,
)


class CustomUserCreationForm(UserCreationForm):
    """Custom user creation form with additional fields."""
    employee_id = forms.CharField(max_length=20, required=True, help_text="Unique employee identifier (PF ID)")
    designation = forms.CharField(max_length=100, required=True, help_text="Job title or designation")
    unit = forms.ModelChoiceField(queryset=Unit.objects.all(), required=False, help_text="Organizational unit")
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'employee_id', 'first_name', 'last_name', 'email', 'designation', 'unit', 'password1', 'password2')


class CustomUserChangeForm(UserChangeForm):
    """Custom user change form."""
    class Meta:
        model = User
        fields = '__all__'


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Admin interface for Role model."""
    list_display = ('name', 'get_colored_name', 'get_user_count', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Role Information', {
            'fields': ('name', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_colored_name(self, obj):
        """Display role name with color badge."""
        colors = {'ADMIN': '#d32f2f', 'MAKER': '#1976d2', 'CHECKER': '#388e3c'}
        color = colors.get(obj.name, '#757575')
        return format_html(
            '<span style="background-color:{}; color:#fff; padding:4px 8px; border-radius:4px; font-weight:bold;">{}</span>',
            color,
            obj.name
        )
    get_colored_name.short_description = 'Role'

    def get_user_count(self, obj):
        """Display number of users with this role."""
        count = obj.users.count()
        return format_html('<strong>{}</strong> user{}', count, '' if count == 1 else 's')
    get_user_count.short_description = 'Users'

    def has_add_permission(self, request):
        """Disallow adding new roles; roles are fixed."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Disallow deleting roles; roles are fixed."""
        return False

    def get_readonly_fields(self, request, obj=None):
        # Make role fields read-only to prevent edits
        return ('name', 'description', 'created_at', 'updated_at')
    
    def get_queryset(self, request):
        """Show only standard roles (ADMIN, MAKER, CHECKER)."""
        qs = super().get_queryset(request)
        return qs.filter(name__in=[ROLE_ADMIN, ROLE_MAKER, ROLE_CHECKER])


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    """Admin interface for Unit model with hierarchy support."""
    list_display = ('code', 'name', 'unit_type', 'parent', 'created_at')
    list_filter = ('unit_type', 'created_at', 'parent')
    search_fields = ('name', 'code')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Unit Information', {
            'fields': ('name', 'code', 'unit_type')
        }),
        ('Hierarchy', {
            'fields': ('parent',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('parent')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model with dashboard quick access."""
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    
    list_display = ('username', 'get_full_name', 'employee_id', 'designation', 'unit', 'get_roles_display', 'get_dashboard_link', 'is_active')
    list_filter = ('is_active', 'unit', 'roles', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'employee_id')
    filter_horizontal = ('roles', 'groups', 'user_permissions')
    readonly_fields = ('date_joined', 'last_login', 'get_role_info', 'get_dashboard_info')
    ordering = ('username',)
    
    # Fieldsets for editing existing users
    fieldsets = (
        ('User Information', {
            'fields': ('username', 'password', 'first_name', 'last_name', 'email')
        }),
        ('Employee Information', {
            'fields': ('employee_id', 'designation', 'unit')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Roles & Assignments', {
            'fields': ('roles', 'get_role_info')
        }),
        ('Dashboard Access', {
            'fields': ('get_dashboard_info',),
            'description': 'Quick links to this user\'s dashboard based on assigned role.'
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    # Fieldsets for adding new users
    add_fieldsets = (
        ('Authentication', {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
        ('Personal Information', {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'email'),
        }),
        ('Employee Information', {
            'classes': ('wide',),
            'fields': ('employee_id', 'designation', 'unit'),
        }),
        ('Permissions', {
            'classes': ('wide',),
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('unit').prefetch_related('roles')
    
    def get_full_name(self, obj):
        """Display user's full name."""
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'
    
    def get_roles_display(self, obj):
        """Display user's roles with color badges."""
        colors = {'ADMIN': '#d32f2f', 'MAKER': '#1976d2', 'CHECKER': '#388e3c'}
        roles_html = []
        for role in obj.roles.all():
            color = colors.get(role.name, '#757575')
            roles_html.append(
                format_html(
                    '<span style="background-color:{}; color:#fff; padding:2px 6px; border-radius:3px; margin-right:4px; font-size:11px; font-weight:bold;">{}</span>',
                    color,
                    role.name
                )
            )
        return format_html(' '.join(['{}'] * len(roles_html)), *roles_html) if roles_html else '—'
    get_roles_display.short_description = 'Roles'

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        """Limit role choices to fixed roles."""
        if db_field.name == 'roles':
            kwargs['queryset'] = Role.objects.filter(name__in=[ROLE_ADMIN, ROLE_MAKER, ROLE_CHECKER]).order_by('name')
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def get_role_info(self, obj):
        """Display assigned roles with descriptions."""
        if not obj.pk:
            return 'Save user first to see role assignments.'
        roles = obj.roles.all()
        if not roles.exists():
            return mark_safe('<em style="color:#f44336;">No roles assigned</em>')
        # Use format_html_join to escape role data safely
        items = format_html_join(
            '',
            '<li><strong>{}</strong>: {}</li>',
            ((role.name, role.description) for role in roles)
        )
        return format_html('<ul style="margin:0; padding-left:20px;">{}</ul>', items)
    get_role_info.short_description = 'Role Information'

    def get_dashboard_link(self, obj):
        """Display clickable link to user's dashboard."""
        if not obj.pk or not obj.is_active:
            return '—'
        role = get_primary_role_name(obj)
        if not role:
            return mark_safe('<span style="color:#f44336;">No role</span>')
        colors = {'ADMIN': '#d32f2f', 'MAKER': '#1976d2', 'CHECKER': '#388e3c'}
        color = colors.get(role, '#757575')
        return format_html(
            '<a href="{}" target="_blank" style="background-color:{}; color:#fff; padding:6px 12px; border-radius:4px; text-decoration:none; font-weight:bold;" title="View {}\' {} dashboard">{} Dashboard</a>',
            get_dashboard_url(obj),
            color,
            obj.get_full_name(),
            role,
            role
        )
    get_dashboard_link.short_description = 'Dashboard'

    def get_dashboard_info(self, obj):
        """Display dashboard access information and quick link."""
        if not obj.pk:
            return 'Save user first to see dashboard access.'
        role = get_primary_role_name(obj)
        if not role:
            return mark_safe('<em style="color:#f44336;">User has no role assigned. Cannot access dashboard.</em>')
        colors = {'ADMIN': '#d32f2f', 'MAKER': '#1976d2', 'CHECKER': '#388e3c'}
        color = colors.get(role, '#757575')
        if not obj.is_active:
            return mark_safe('<em style="color:#f44336;">User account is inactive.</em>')
        return format_html(
            '<div style="padding:12px; background:#f5f5f5; border-left:4px solid {}; border-radius:4px;">' 
            '<p><strong>Role:</strong> {}</p>'
            '<p><strong>Dashboard URL:</strong> <code>{}</code></p>'
            '<p><a href="{}" class="button" target="_blank" style="background:{}; color:#fff; padding:8px 16px; border-radius:4px; text-decoration:none; display:inline-block; margin-top:8px;">Open Dashboard</a></p>'
            '</div>',
            color,
            role,
            get_dashboard_url(obj),
            get_dashboard_url(obj),
            color
        )
    get_dashboard_info.short_description = 'Dashboard Access'
    
    def save_model(self, request, obj, form, change):
        """Save model and handle roles after user creation."""
        super().save_model(request, obj, form, change)
        # For new users, we can set default roles here if needed
        if not change and not obj.roles.exists():
            # Optionally assign a default role
            pass


@admin.register(ApprovalRequest)
class ApprovalRequestAdmin(admin.ModelAdmin):
    """
    Admin interface for ApprovalRequest model.
    
    PERMISSIONS:
    - ADMIN: Can view all requests
    - MAKER: No access (requests are created via API)
    - CHECKER: Can view own assignments (optional)
    """
    list_display = (
        'get_request_id',
        'get_created_by',
        'get_maker_unit',
        'request_type',
        'get_status_badge',
        'get_reviewed_by',
        'reviewed_at',
    )
    list_filter = ('status', 'request_type', 'maker_unit', 'created_at')
    search_fields = ('request_type', 'title', 'created_by__username', 'created_by__first_name', 'created_by__last_name')
    readonly_fields = (
        'created_by',
        'maker_unit',
        'request_type',
        'title',
        'description',
        'payload',
        'assigned_checker',
        'checker_unit',
        'status',
        'reviewed_by',
        'reviewed_at',
        'created_at',
        'updated_at',
        'get_audit_trail',
    )
    ordering = ['-created_at']
    
    fieldsets = (
        ('Request Information', {
            'fields': ('request_type', 'title', 'description')
        }),
        ('Maker Details', {
            'fields': ('created_by', 'maker_unit')
        }),
        ('Request Payload', {
            'fields': ('payload',),
            'classes': ('collapse',)
        }),
        ('Assignment', {
            'fields': ('assigned_checker', 'checker_unit')
        }),
        ('Review Status', {
            'fields': ('status', 'reviewed_by', 'reviewed_at', 'remarks')
        }),
        ('Audit Trail', {
            'fields': ('get_audit_trail',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_request_id(self, obj):
        """Display request ID."""
        return f"#{obj.id}"
    get_request_id.short_description = 'ID'
    
    def get_created_by(self, obj):
        """Display maker information."""
        if obj.created_by:
            return f"{obj.created_by.get_full_name()} ({obj.created_by.employee_id})"
        return "—"
    get_created_by.short_description = 'Created By'
    
    def get_maker_unit(self, obj):
        """Display maker's unit."""
        if obj.maker_unit:
            return f"{obj.maker_unit.name} ({obj.maker_unit.code})"
        return "—"
    get_maker_unit.short_description = 'Maker Unit'
    
    def get_status_badge(self, obj):
        """Display status with color badge."""
        colors = {
            'PENDING': '#ffc107',
            'APPROVED': '#28a745',
            'REJECTED': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color:{}; color:#fff; padding:4px 8px; border-radius:4px; font-weight:bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    get_status_badge.short_description = 'Status'
    
    def get_reviewed_by(self, obj):
        """Display reviewer information."""
        if obj.reviewed_by:
            return f"{obj.reviewed_by.get_full_name()} ({obj.reviewed_by.employee_id})"
        return "—"
    get_reviewed_by.short_description = 'Reviewed By'
    
    def get_audit_trail(self, obj):
        """Display approval workflow audit trail."""
        logs = obj.logs.all().order_by('timestamp')
        if not logs:
            return "No logs"
        
        html_items = []
        for log in logs:
            action_color = {
                'CREATE': '#007bff',
                'ASSIGN': '#17a2b8',
                'APPROVE': '#28a745',
                'REJECT': '#dc3545',
            }.get(log.action, '#6c757d')
            
            performed = f"{log.performed_by.get_full_name()}" if log.performed_by else "System"
            html_items.append(
                f'<div style="margin: 8px 0; padding: 8px; background: #f8f9fa; border-left: 4px solid {action_color};">'
                f'<strong style="color: {action_color};">{log.get_action_display()}</strong> '
                f'by {performed} on {log.timestamp.strftime("%Y-%m-%d %H:%M")}'
                f'{f"<br/><em>{log.remarks}</em>" if log.remarks else ""}</div>'
            )
        return format_html(''.join(html_items))
    get_audit_trail.short_description = 'Workflow History'
    
    def has_add_permission(self, request):
        """Disable adding requests via admin."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Only ADMIN can delete requests."""
        return request.user.roles.filter(name='ADMIN').exists()
    
    def has_change_permission(self, request, obj=None):
        """Only ADMIN can view/edit requests."""
        return request.user.roles.filter(name='ADMIN').exists()
    
    def get_queryset(self, request):
        """Optimize queryset and filter by role."""
        qs = super().get_queryset(request)
        qs = qs.select_related(
            'created_by', 'maker_unit', 'assigned_checker',
            'checker_unit', 'reviewed_by'
        ).prefetch_related('logs')
        
        # Only ADMIN can view all
        is_admin = request.user.roles.filter(name='ADMIN').exists()
        if not is_admin:
            # Non-admin users see empty queryset
            qs = qs.none()
        
        return qs


@admin.register(ApprovalLog)
class ApprovalLogAdmin(admin.ModelAdmin):
    """
    Admin interface for ApprovalLog model (audit trail).
    
    Shows all workflow actions for approval requests.
    """
    list_display = (
        'get_request_id',
        'get_action_badge',
        'get_performed_by',
        'timestamp',
        'get_remarks_preview',
    )
    list_filter = ('action', 'timestamp', 'approval_request__request_type')
    search_fields = (
        'approval_request__id',
        'performed_by__username',
        'remarks',
    )
    readonly_fields = (
        'approval_request',
        'action',
        'performed_by',
        'remarks',
        'timestamp',
    )
    ordering = ['-timestamp']
    
    fieldsets = (
        ('Log Information', {
            'fields': ('approval_request', 'action', 'timestamp')
        }),
        ('Details', {
            'fields': ('performed_by', 'remarks')
        }),
    )
    
    def get_request_id(self, obj):
        """Display request ID with link."""
        url = reverse('admin:admin_core_approvalrequest_change', args=[obj.approval_request.id])
        return format_html('<a href="{}"># {}</a>', url, obj.approval_request.id)
    get_request_id.short_description = 'Request'
    
    def get_action_badge(self, obj):
        """Display action with color badge."""
        colors = {
            'CREATE': '#007bff',
            'ASSIGN': '#17a2b8',
            'APPROVE': '#28a745',
            'REJECT': '#dc3545',
            'RESUBMIT': '#ffc107',
            'VIEW': '#6c757d',
        }
        color = colors.get(obj.action, '#6c757d')
        return format_html(
            '<span style="background-color:{}; color:#fff; padding:4px 8px; border-radius:4px; font-weight:bold;">{}</span>',
            color,
            obj.get_action_display()
        )
    get_action_badge.short_description = 'Action'
    
    def get_performed_by(self, obj):
        """Display who performed the action."""
        if obj.performed_by:
            return f"{obj.performed_by.get_full_name()} ({obj.performed_by.username})"
        return "System"
    get_performed_by.short_description = 'Performed By'
    
    def get_remarks_preview(self, obj):
        """Display first 100 chars of remarks."""
        if obj.remarks:
            preview = obj.remarks[:100]
            if len(obj.remarks) > 100:
                preview += "..."
            return preview
        return "—"
    get_remarks_preview.short_description = 'Remarks'
    
    def has_add_permission(self, request):
        """Disable manual creation of logs."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Disable deletion of logs."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Only ADMIN can view logs."""
        return request.user.roles.filter(name='ADMIN').exists()
    
    def get_queryset(self, request):
        """Optimize queryset and filter by role."""
        qs = super().get_queryset(request)
        qs = qs.select_related(
            'approval_request', 'performed_by'
        ).order_by('-timestamp')
        
        # Only ADMIN can view
        is_admin = request.user.roles.filter(name='ADMIN').exists()
        if not is_admin:
            qs = qs.none()
        
        return qs


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin interface for AuditLog model."""
    list_display = ('get_user_name', 'action', 'action_type', 'ip_address', 'created_at')
    list_filter = ('action_type', 'created_at', 'user')
    search_fields = ('action', 'user__username', 'ip_address')
    readonly_fields = ('user', 'action', 'action_type', 'metadata', 'ip_address', 'created_at')
    
    fieldsets = (
        ('Audit Information', {
            'fields': ('user', 'action', 'action_type')
        }),
        ('Network', {
            'fields': ('ip_address',)
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_user_name(self, obj):
        """Display user's name or 'Anonymous'."""
        return obj.user.get_full_name() if obj.user else 'Anonymous'
    get_user_name.short_description = 'User'
    
    def has_add_permission(self, request):
        """Prevent manual creation of audit logs."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of audit logs."""
        return False
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('user')




