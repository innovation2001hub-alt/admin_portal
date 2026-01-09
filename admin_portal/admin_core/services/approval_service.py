"""
Approval Service.

Implements Maker-Checker workflow and approval routing based on unit hierarchy.
"""
from django.db import transaction
from admin_core.models import ApprovalRequest, User, AuditLog
from .hierarchy_service import HierarchyService


class ApprovalService:
    """
    Service class for handling approval workflow (Maker-Checker pattern).
    
    Methods:
    - create_approval_request: Create new approval request
    - get_pending_approvals: Get pending approvals for a checker
    - approve_request: Approve a request
    - reject_request: Reject a request
    - route_approval: Route approval to appropriate checker based on hierarchy
    """
    
    @staticmethod
    def create_approval_request(action_type, payload, maker):
        """
        Create a new approval request.
        
        Args:
            action_type: Type of action (e.g., 'CREATE_USER', 'UPDATE_UNIT')
            payload: JSON data for the request
            maker: User object who created the request
        
        Returns:
            ApprovalRequest object
        """
        approval = ApprovalRequest.objects.create(
            action_type=action_type,
            payload=payload,
            maker=maker,
            status='PENDING'
        )
        
        # Log the approval request creation
        AuditLog.log_action(
            user=maker,
            action=f'Created approval request: {action_type}',
            action_type='CREATE',
            metadata={
                'approval_id': approval.id,
                'action_type': action_type,
            }
        )
        
        return approval
    
    @staticmethod
    def get_pending_approvals(checker):
        """
        Get all pending approval requests assigned to a checker.
        
        Args:
            checker: User object (checker/approver)
        
        Returns:
            QuerySet of pending ApprovalRequest objects
        """
        return ApprovalRequest.objects.filter(
            checker=checker,
            status='PENDING'
        ).order_by('-created_at')
    
    @staticmethod
    @transaction.atomic
    def approve_request(approval_request, checker, comments=''):
        """
        Approve an approval request.
        
        Args:
            approval_request: ApprovalRequest object
            checker: User object who is approving
            comments: Optional approval comments
        
        Returns:
            ApprovalRequest object
        
        Raises:
            ValueError: If request is not pending or checker mismatch
        """
        if not approval_request.is_pending():
            raise ValueError(f'Cannot approve request with status: {approval_request.status}')
        
        if approval_request.checker.id != checker.id:
            raise ValueError('Only the assigned checker can approve this request.')
        
        approval_request.approve(comments=comments)
        
        # Log the approval
        AuditLog.log_action(
            user=checker,
            action=f'Approved request: {approval_request.action_type}',
            action_type='APPROVE',
            metadata={
                'approval_id': approval_request.id,
                'action_type': approval_request.action_type,
                'comments': comments,
            }
        )
        
        return approval_request
    
    @staticmethod
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
                # Get the first admin/manager user in the superior unit
                checker = superior_unit.users.filter(
                    roles__name__in=['ADMIN', 'MANAGER']
                ).first()
                return checker
        
        # For hierarchy/approval operations: route to Head Office
        if action_type in ['CREATE_UNIT', 'UPDATE_UNIT', 'DELETE_UNIT', 'APPROVE_REQUEST']:
            ho_unit = maker.unit.get_root_unit()
            if ho_unit:
                checker = ho_unit.users.filter(
                    roles__name__in=['ADMIN', 'HEAD_OFFICE']
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
