from django.contrib import admin
from .models import User, Unit, Role, ApprovalRequest, AuditLog


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Admin interface for Role model."""
    list_display = ('name', 'created_at', 'updated_at')
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
class UserAdmin(admin.ModelAdmin):
    """Admin interface for User model."""
    list_display = ('username', 'get_full_name', 'employee_id', 'designation', 'unit', 'is_active')
    list_filter = ('is_active', 'unit', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'employee_id')
    filter_horizontal = ('roles', 'groups', 'user_permissions')
    readonly_fields = ('date_joined', 'last_login')
    
    fieldsets = (
        ('User Information', {
            'fields': ('username', 'first_name', 'last_name', 'email')
        }),
        ('Employee Information', {
            'fields': ('employee_id', 'designation', 'unit')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Roles & Assignments', {
            'fields': ('roles',)
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
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




