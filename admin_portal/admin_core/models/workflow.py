from django.db import models
from django.utils import timezone


class ApprovalRequest(models.Model):
    """
    ApprovalRequest model implementing Maker-Checker workflow pattern.
    
    Maker: User who creates/initiates the request
    Checker: User who approves/rejects the request
    
    Fields:
    - action_type: Type of action being requested (e.g., 'CREATE_USER', 'UPDATE_HIERARCHY')
    - payload: JSON data containing the request details
    - maker: User who created the request
    - checker: User assigned to approve/reject
    - status: Current status (PENDING, APPROVED, REJECTED)
    - created_at: Timestamp when request was created
    - updated_at: Timestamp when request was last modified
    - completed_at: Timestamp when request was approved/rejected
    - comments: Optional comments from the checker
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    
    action_type = models.CharField(
        max_length=100,
        help_text="Type of action being requested"
    )
    payload = models.JSONField(
        help_text="JSON data containing request details"
    )
    maker = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='approval_requests_made',
        help_text="User who created this request"
    )
    checker = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approval_requests_to_check',
        help_text="User assigned to approve/reject"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        help_text="Current approval status"
    )
    comments = models.TextField(
        blank=True,
        help_text="Comments from the checker"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the request was approved/rejected"
    )
    
    class Meta:
        db_table = 'admin_core_approval_request'
        verbose_name = 'Approval Request'
        verbose_name_plural = 'Approval Requests'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.action_type} - {self.status} ({self.created_at})"
    
    def approve(self, comments=''):
        """Mark the request as approved."""
        self.status = 'APPROVED'
        self.comments = comments
        self.completed_at = timezone.now()
        self.save()
    
    def reject(self, comments=''):
        """Mark the request as rejected."""
        self.status = 'REJECTED'
        self.comments = comments
        self.completed_at = timezone.now()
        self.save()
    
    def is_pending(self):
        """Check if request is still pending."""
        return self.status == 'PENDING'

