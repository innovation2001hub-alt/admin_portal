from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe
from django.urls import reverse
from django import forms
from .models import User, Unit, Role, ApprovalRequest, AuditLog
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
    """Admin interface for ApprovalRequest model."""
    list_display = ('action_type', 'status', 'maker', 'checker', 'created_at', 'completed_at')
    list_filter = ('status', 'action_type', 'created_at', 'completed_at')
    search_fields = ('action_type', 'maker__username', 'checker__username')
    readonly_fields = ('created_at', 'updated_at', 'completed_at', 'payload')
    
    fieldsets = (
        ('Request Information', {
            'fields': ('action_type', 'status')
        }),
        ('Payload', {
            'fields': ('payload',),
            'classes': ('collapse',)
        }),
        ('Approval Workflow', {
            'fields': ('maker', 'checker', 'comments')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('maker', 'checker')


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




