from django.db import models
from django.utils import timezone


class ApprovalRequest(models.Model):
    """
    ApprovalRequest model implementing Maker-Checker workflow with unit hierarchy routing.
    
    WORKFLOW:
    - MAKER (in unit X) creates a request
    - Request is routed to CHECKER in ancestor units (X's parent, grandparent, etc.)
    - CHECKER approves or rejects with remarks
    - MAKER can view final status and remarks
    
    HIERARCHY RULES:
    - maker_unit: The unit of the user who created the request
    - checker_unit: The unit of the assigned checker (must be ancestor of maker_unit)
    - eligible_checkers are CHECKER role users from ancestor units of maker_unit
    
    Fields:
    - created_by: The MAKER who created this request
    - maker_unit: Unit of the maker (for hierarchy routing)
    - request_type: Type of action (e.g., 'CREATE_USER', 'UPDATE_HIERARCHY')
    - title: Short title/subject of the request
    - description: Detailed description
    - payload: JSON data containing request details
    - assigned_checker: The specific CHECKER assigned to review this (FK to User)
    - checker_unit: The unit of the assigned checker (for filtering)
    - status: PENDING, APPROVED, REJECTED
    - reviewed_by: User who approved/rejected
    - reviewed_at: Timestamp of review action
    - remarks: Comments from the checker on approval/rejection
    - created_at: Request submission timestamp
    - updated_at: Last modification timestamp
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    
    # Maker Information
    created_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='approval_requests_created',
        help_text="MAKER user who created this request"
    )
    maker_unit = models.ForeignKey(
        'Unit',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approval_requests_made',
        help_text="Unit of the maker (for hierarchy-based routing)"
    )
    
    # Request Information
    request_type = models.CharField(
        max_length=100,
        help_text="Type of action being requested"
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        help_text="Short title/subject of the request"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of the request"
    )
    payload = models.JSONField(
        default=dict,
        blank=True,
        help_text="JSON data containing request details"
    )
    
    # Checker Assignment (Hierarchy-based)
    assigned_checker = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approval_requests_assigned',
        help_text="CHECKER user assigned to review this request (must be from upper unit)"
    )
    checker_unit = models.ForeignKey(
        'Unit',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approval_requests_to_review',
        help_text="Unit of the assigned checker (must be ancestor of maker_unit)"
    )
    
    # Approval Status & Review
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        help_text="Current approval status"
    )
    reviewed_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approval_requests_reviewed',
        help_text="CHECKER who reviewed this request"
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when request was approved/rejected"
    )
    remarks = models.TextField(
        blank=True,
        help_text="Comments/remarks from the checker"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'admin_core_approval_request'
        verbose_name = 'Approval Request'
        verbose_name_plural = 'Approval Requests'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'assigned_checker']),
            models.Index(fields=['created_by', 'status']),
            models.Index(fields=['maker_unit', 'status']),
            models.Index(fields=['checker_unit', 'status']),
        ]
    
    def __str__(self):
        return f"{self.request_type} - {self.status} ({self.created_at.strftime('%Y-%m-%d')})"
    
    def approve(self, checker_user, remarks=''):
        """Mark the request as approved by the checker."""
        self.status = 'APPROVED'
        self.reviewed_by = checker_user
        self.reviewed_at = timezone.now()
        self.remarks = remarks
        self.save()
    
    def reject(self, checker_user, remarks=''):
        """Mark the request as rejected by the checker."""
        self.status = 'REJECTED'
        self.reviewed_by = checker_user
        self.reviewed_at = timezone.now()
        self.remarks = remarks
        self.save()
    
    def is_pending(self):
        """Check if request is still pending."""
        return self.status == 'PENDING'
    
    def is_approved(self):
        """Check if request has been approved."""
        return self.status == 'APPROVED'
    
    def is_rejected(self):
        """Check if request has been rejected."""
        return self.status == 'REJECTED'
    
    def is_eligible_for_checker(self, user):
        """
        Check if a CHECKER user is eligible to review this request.
        
        RULES:
        1. User must have CHECKER role
        2. User must be from an ancestor unit of maker_unit
        3. Request must be PENDING
        
        Args:
            user: User object to check
            
        Returns:
            True if user is eligible to review this request
        """
        # Must be pending
        if not self.is_pending():
            return False
        
        # User must have CHECKER role
        if not user.roles.filter(name='CHECKER').exists():
            return False
        
        # User must be from an ancestor unit of maker_unit
        if not self.maker_unit:
            return False
        
        return user.unit and user.unit.is_ancestor_of(self.maker_unit)
    
    def can_be_approved_by(self, user):
        """
        Check if a user can approve this request.
        
        Args:
            user: User object to check
            
        Returns:
            True if user is the assigned checker and request is pending
        """
        if self.assigned_checker != user:
            return False
        if not self.is_pending():
            return False
        return True


class ApprovalLog(models.Model):
    """
    ApprovalLog model for tracking approval workflow actions.
    
    Maintains audit trail of all approval-related actions.
    """
    ACTION_TYPES = [
        ('CREATE', 'Request Created'),
        ('ASSIGN', 'Assigned to Checker'),
        ('APPROVE', 'Approved'),
        ('REJECT', 'Rejected'),
        ('RESUBMIT', 'Resubmitted'),
        ('VIEW', 'Viewed'),
    ]
    
    approval_request = models.ForeignKey(
        'ApprovalRequest',
        on_delete=models.CASCADE,
        related_name='logs',
        help_text="Associated approval request"
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_TYPES,
        help_text="Type of action"
    )
    performed_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approval_logs',
        help_text="User who performed the action"
    )
    remarks = models.TextField(
        blank=True,
        help_text="Additional remarks or comments"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'admin_core_approval_log'
        verbose_name = 'Approval Log'
        verbose_name_plural = 'Approval Logs'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.get_action_display()} - {self.approval_request.id} ({self.timestamp})"


