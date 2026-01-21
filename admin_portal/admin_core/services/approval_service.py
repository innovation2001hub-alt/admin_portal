"""
Approval Service.

Implements Maker-Checker workflow with unit hierarchy-based routing.

KEY CONCEPTS:
- MAKER: User creating a request (belongs to a unit)
- CHECKER: User approving requests (belongs to ancestor unit of maker)
- Approval routing: Maker in unit X -> request goes to CHECKER in ancestor of X
"""
from django.db import transaction, models
from django.core.exceptions import ValidationError
from admin_core.models import ApprovalRequest, ApprovalLog, User, AuditLog, Unit


class ApprovalService:
    """
    Service for Maker-Checker approval workflow with hierarchy-based routing.
    
    APPROVAL FLOW:
    1. MAKER creates request from their unit
    2. System routes to eligible CHECKERs in ancestor units
    3. CHECKER approves or rejects with remarks
    4. MAKER views result
    
    Methods:
    - create_approval_request: Create and route a new request
    - get_pending_approvals_for_checker: Get queue for checker
    - get_maker_requests: Get requests for maker
    - approve_request: Approve with validation
    - reject_request: Reject with validation
    - get_eligible_checkers: Get eligible checkers by hierarchy
    """
    
    @staticmethod
    def create_approval_request(request_type, title, description, payload, maker, title_display=None):
        """
        Create a new approval request and route to eligible checkers.
        
        BUSINESS LOGIC:
        - Set maker_unit from maker.unit
        - Find eligible CHECKER users in ancestor units
        - Auto-assign to first available checker (or keep unassigned for queue)
        
        Args:
            request_type: Type of request (e.g., 'CREATE_USER', 'UPDATE_HIERARCHY')
            title: Short title
            description: Detailed description
            payload: JSON data for the request
            maker: User object who created the request (MAKER role)
            title_display: Optional display title
        
        Returns:
            ApprovalRequest object
            
        Raises:
            ValidationError: If maker is not assigned to a unit
        """
        if not maker.unit:
            raise ValidationError("Maker must be assigned to a unit")
        
        if not maker.roles.filter(name='MAKER').exists():
            raise ValidationError("User must have MAKER role to create approval requests")
        
        with transaction.atomic():
            # Create the approval request
            approval = ApprovalRequest.objects.create(
                created_by=maker,
                maker_unit=maker.unit,
                request_type=request_type,
                title=title,
                description=description,
                payload=payload or {},
                status='PENDING'
            )
            
            # Route to checker
            ApprovalService.assign_checker(approval)
            
            # Log creation
            ApprovalLog.objects.create(
                approval_request=approval,
                action='CREATE',
                performed_by=maker,
                remarks=f"Created by {maker.get_full_name()}"
            )
            
            # Audit log
            AuditLog.log_action(
                user=maker,
                action=f'Created approval request: {request_type}',
                action_type='CREATE',
                metadata={
                    'approval_id': approval.id,
                    'request_type': request_type,
                    'maker_unit': maker.unit.code,
                }
            )
        
        return approval
    
    @staticmethod
    def assign_checker(approval):
        """
        Assign a CHECKER to an approval request based on hierarchy.
        
        ALGORITHM:
        1. Get eligible checkers (CHECKER role in ancestor units)
        2. Assign to first available checker (can be improved with round-robin)
        3. Set checker_unit to checker's unit
        4. Log the assignment
        
        Args:
            approval: ApprovalRequest object
        """
        if not approval.maker_unit:
            return
        
        # Get ancestor units ordered nearest-to-root. We need nearest parent first for routing.
        ancestors = approval.maker_unit.get_ancestors()
        if not ancestors:
            # No ancestors - maker is at root unit, cannot route
            return

        # Prefer the closest ancestor that has an active checker
        selected_checker = None
        for ancestor in ancestors:  # ancestors are ordered closest parent -> root
            checker_qs = User.objects.filter(
                unit=ancestor,
                roles__name='CHECKER',
                is_active=True
            ).order_by('id')
            if checker_qs.exists():
                selected_checker = checker_qs.first()
                break

        if selected_checker:
            approval.assigned_checker = selected_checker
            approval.checker_unit = selected_checker.unit
            approval.save()

            # Log assignment
            ApprovalLog.objects.create(
                approval_request=approval,
                action='ASSIGN',
                performed_by=None,
                remarks=f"Auto-assigned to {selected_checker.get_full_name()} ({selected_checker.unit.code})"
            )
    
    @staticmethod
    def get_pending_approvals_for_checker(checker):
        """
        Get all pending approvals routed to this checker.
        
        CRITERIA:
        - Status is PENDING
        - assigned_checker is the given user
        - User must have CHECKER role
        
        Args:
            checker: User object (should have CHECKER role)
            
        Returns:
            QuerySet of ApprovalRequest objects
        """
        if not checker.roles.filter(name='CHECKER').exists():
            return ApprovalRequest.objects.none()
        
        return ApprovalRequest.objects.filter(
            assigned_checker=checker,
            status='PENDING'
        ).select_related('created_by', 'maker_unit', 'assigned_checker').order_by('-created_at')
    
    @staticmethod
    def get_checker_queue(checker):
        """
        Get ALL requests eligible for this checker (assigned or unassigned).
        
        CRITERIA:
        - Status is PENDING
        - Maker's unit is a descendant of checker's unit
        - Checker has CHECKER role
        
        This is useful for showing full queue, not just assigned to this specific checker.
        
        Args:
            checker: User object (should have CHECKER role)
            
        Returns:
            QuerySet of ApprovalRequest objects
        """
        if not checker.roles.filter(name='CHECKER').exists():
            return ApprovalRequest.objects.none()
        
        if not checker.unit:
            return ApprovalRequest.objects.none()
        
        # Get all units where this checker is ancestor
        descendant_units = checker.unit.get_all_children() + [checker.unit]
        
        return ApprovalRequest.objects.filter(
            maker_unit__in=descendant_units,
            status='PENDING'
        ).select_related('created_by', 'maker_unit', 'assigned_checker').order_by('-created_at')
    
    @staticmethod
    def get_maker_requests(maker):
        """
        Get all approval requests created by a maker.
        
        Args:
            maker: User object (should have MAKER role)
            
        Returns:
            QuerySet of ApprovalRequest objects ordered by creation date
        """
        return ApprovalRequest.objects.filter(
            created_by=maker
        ).select_related('assigned_checker', 'maker_unit', 'reviewed_by').order_by('-created_at')
    
    @staticmethod
    @transaction.atomic
    def approve_request(approval, checker, remarks=''):
        """
        Approve an approval request.
        
        VALIDATIONS:
        - Request must be PENDING
        - Checker must be assigned or eligible
        - Checker must have CHECKER role
        
        Args:
            approval: ApprovalRequest object
            checker: User object doing the approval (CHECKER)
            remarks: Optional remarks/comments
            
        Raises:
            ValidationError: If approval conditions not met
        """
        if not approval.is_pending():
            raise ValidationError(f"Cannot approve a {approval.status.lower()} request")
        
        if not checker.roles.filter(name='CHECKER').exists():
            raise ValidationError("Only users with CHECKER role can approve requests")
        
        # Verify checker is eligible
        if not approval.is_eligible_for_checker(checker):
            raise ValidationError(
                "You are not eligible to review this request. "
                "Request maker must be in a subordinate unit."
            )
        
        # Approve
        approval.approve(checker, remarks)
        
        # Log the action
        ApprovalLog.objects.create(
            approval_request=approval,
            action='APPROVE',
            performed_by=checker,
            remarks=remarks
        )
        
        # Audit log
        AuditLog.log_action(
            user=checker,
            action=f'Approved request: {approval.request_type}',
            action_type='APPROVE',
            metadata={
                'approval_id': approval.id,
                'request_type': approval.request_type,
                'maker': approval.created_by.username,
            }
        )
    
    @staticmethod
    @transaction.atomic
    def reject_request(approval, checker, remarks=''):
        """
        Reject an approval request.
        
        VALIDATIONS:
        - Request must be PENDING
        - Checker must be assigned or eligible
        - Checker must have CHECKER role
        
        Args:
            approval: ApprovalRequest object
            checker: User object doing the rejection (CHECKER)
            remarks: Optional remarks/comments (recommended)
            
        Raises:
            ValidationError: If rejection conditions not met
        """
        if not approval.is_pending():
            raise ValidationError(f"Cannot reject a {approval.status.lower()} request")
        
        if not checker.roles.filter(name='CHECKER').exists():
            raise ValidationError("Only users with CHECKER role can reject requests")
        
        # Verify checker is eligible
        if not approval.is_eligible_for_checker(checker):
            raise ValidationError(
                "You are not eligible to review this request. "
                "Request maker must be in a subordinate unit."
            )
        
        # Reject
        approval.reject(checker, remarks)
        
        # Log the action
        ApprovalLog.objects.create(
            approval_request=approval,
            action='REJECT',
            performed_by=checker,
            remarks=remarks
        )
        
        # Audit log
        AuditLog.log_action(
            user=checker,
            action=f'Rejected request: {approval.request_type}',
            action_type='REJECT',
            metadata={
                'approval_id': approval.id,
                'request_type': approval.request_type,
                'maker': approval.created_by.username,
            }
        )
    
    @staticmethod
    def get_eligible_checkers(maker_unit):
        """
        Get all CHECKER users eligible to review requests from makers in given unit.
        
        CRITERIA:
        - Must have CHECKER role
        - Must be in an ancestor unit of maker_unit
        - Must be active
        
        Args:
            maker_unit: Unit object where makers reside
            
        Returns:
            QuerySet of User objects
        """
        ancestors = maker_unit.get_ancestors()
        if not ancestors:
            return User.objects.none()

        # Preserve hierarchy order: nearest parent first
        ordered_users = []
        for ancestor in ancestors:  # ancestors ordered parent -> root
            for user in User.objects.filter(
                unit=ancestor,
                roles__name='CHECKER',
                is_active=True
            ).order_by('id'):
                ordered_users.append(user.id)

        # Return queryset respecting collected order
        return User.objects.filter(id__in=ordered_users).order_by(
            models.Case(
                *[models.When(id=pk, then=pos) for pos, pk in enumerate(ordered_users)]
            )
        )
    
    @staticmethod
    def get_statistics(unit=None):
        """
        Get approval statistics.
        
        Args:
            unit: Optional Unit to filter by
            
        Returns:
            Dictionary with statistics
        """
        query = ApprovalRequest.objects.all()
        if unit:
            query = query.filter(maker_unit=unit)
        
        return {
            'total': query.count(),
            'pending': query.filter(status='PENDING').count(),
            'approved': query.filter(status='APPROVED').count(),
            'rejected': query.filter(status='REJECTED').count(),
        }
    
    @transaction.atomic
    def reject_request(approval_request, checker, comments=''):
        """
        Reject an approval request.
        
        Args:
            approval_request: ApprovalRequest object
            checker: User object who is rejecting
            comments: Optional rejection comments/reason
        
        Returns:
            ApprovalRequest object
        
        Raises:
            ValueError: If request is not pending or checker mismatch
        """
        if not approval_request.is_pending():
            raise ValueError(f'Cannot reject request with status: {approval_request.status}')
        
        if approval_request.checker.id != checker.id:
            raise ValueError('Only the assigned checker can reject this request.')
        
        approval_request.reject(comments=comments)
        
        # Log the rejection
        AuditLog.log_action(
            user=checker,
            action=f'Rejected request: {approval_request.action_type}',
            action_type='REJECT',
            metadata={
                'approval_id': approval_request.id,
                'action_type': approval_request.action_type,
                'comments': comments,
            }
        )
        
        return approval_request
    
    @staticmethod
    def route_approval(maker, action_type, payload):
        """
        Create an approval request and route it to the appropriate checker.
        
        Routing logic:
        - For user operations: Route to immediate superior
        - For hierarchy operations: Route to HO
        
        Args:
            maker: User object creating the request
            action_type: Type of action
            payload: Request payload
        
        Returns:
            ApprovalRequest object or None if no checker found
        """
        approval = ApprovalRequest.objects.create(
            action_type=action_type,
            payload=payload,
            maker=maker,
            status='PENDING'
        )
        
        # Determine checker based on action type and hierarchy
        checker = ApprovalService._determine_checker(maker, action_type)
        
        if checker:
            approval.checker = checker
            approval.save()
        
        # Log the routed approval
        AuditLog.log_action(
            user=maker,
            action=f'Routed approval request: {action_type}',
            action_type='CREATE',
            metadata={
                'approval_id': approval.id,
                'action_type': action_type,
                'assigned_to': checker.username if checker else 'unassigned',
            }
        )
        
        return approval
    
    @staticmethod
    def _determine_checker(maker, action_type):
        """
        Determine the appropriate checker for an approval request.
        
        Args:
            maker: User creating the request
            action_type: Type of action
        
        Returns:
            User object (checker) or None
        """
        if not maker.unit:
            return None
        
        # For user creation/updates: route to immediate superior
        if action_type in ['CREATE_USER', 'UPDATE_USER', 'DELETE_USER']:
            superior_unit = maker.unit.parent
            if superior_unit:
                # Get the first admin user in the superior unit
                checker = superior_unit.users.filter(
                    roles__name='ADMIN'
                ).first()
                return checker
        
        # For hierarchy/approval operations: route to Head Office
        if action_type in ['CREATE_UNIT', 'UPDATE_UNIT', 'DELETE_UNIT', 'APPROVE_REQUEST']:
            ho_unit = maker.unit.get_root_unit()
            if ho_unit:
                checker = ho_unit.users.filter(
                    roles__name='ADMIN'
                ).first()
                return checker
        
        return None
    
    @staticmethod
    def get_approval_statistics(user):
        """
        Get approval statistics for a user.
        
        Args:
            user: User object
        
        Returns:
            Dictionary with approval statistics
        """
        return {
            'total_created': ApprovalRequest.objects.filter(maker=user).count(),
            'pending_to_check': ApprovalRequest.objects.filter(
                checker=user,
                status='PENDING'
            ).count(),
            'approved': ApprovalRequest.objects.filter(
                checker=user,
                status='APPROVED'
            ).count(),
            'rejected': ApprovalRequest.objects.filter(
                checker=user,
                status='REJECTED'
            ).count(),
        }
