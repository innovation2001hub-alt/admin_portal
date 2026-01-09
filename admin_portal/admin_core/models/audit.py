from django.db import models
import json


class AuditLog(models.Model):
    """
    AuditLog model for tracking all user actions in the system.
    
    Captures comprehensive metadata for audit trails and compliance.
    
    Fields:
    - user: User who performed the action
    - action: Description of the action performed
    - action_type: Categorized action type for filtering
    - metadata: JSON field for request/response metadata
    - ip_address: IP address of the request
    - created_at: Timestamp of the action
    """
    ACTION_TYPES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('APPROVE', 'Approve'),
        ('REJECT', 'Reject'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('VIEW', 'View'),
        ('EXPORT', 'Export'),
    ]
    
    user = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        help_text="User who performed the action"
    )
    action = models.CharField(
        max_length=255,
        help_text="Description of the action"
    )
    action_type = models.CharField(
        max_length=20,
        choices=ACTION_TYPES,
        help_text="Categorized action type"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata (request data, response status, etc.)"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of the request"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'admin_core_audit_log'
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action_type', '-created_at']),
        ]
    
    def __str__(self):
        user_str = self.user.get_full_name() if self.user else 'Anonymous'
        return f"{user_str} - {self.action} ({self.created_at})"
    
    @staticmethod
    def log_action(user, action, action_type, metadata=None, ip_address=None):
        """
        Convenience method to create an audit log entry.
        
        Args:
            user: User object performing the action
            action: Description of the action
            action_type: Type of action (one of ACTION_TYPES)
            metadata: Optional dictionary of additional data
            ip_address: Optional IP address
        """
        return AuditLog.objects.create(
            user=user,
            action=action,
            action_type=action_type,
            metadata=metadata or {},
            ip_address=ip_address
        )

