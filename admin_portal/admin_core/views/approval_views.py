"""
Approval Request Views.

Implements Maker-Checker workflow endpoints with hierarchy-based routing:
- MAKER creates and views their requests
- CHECKER approves/rejects requests from lower units
- ADMIN views all requests
"""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from django.db.models import Q

from admin_core.models import ApprovalRequest, AuditLog
from admin_core.serializers import (
    ApprovalRequestSerializer,
    ApprovalRequestDetailSerializer,
    ApprovalActionSerializer,
    ApprovalCreateSerializer,
)
from admin_core.services.approval_service import ApprovalService


class ApprovalRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Approval Request management with Maker-Checker workflow.
    
    ROLE-BASED BEHAVIOR:
    - MAKER: Create requests, view own requests
    - CHECKER: View pending requests from lower units, approve/reject
    - ADMIN: View all requests across organization
    
    Endpoints:
    - GET /api/approvals/ - List (filtered by role)
    - POST /api/approvals/ - Create new request (MAKER only)
    - GET /api/approvals/{id}/ - Get details (if eligible)
    - POST /api/approvals/{id}/approve/ - Approve (CHECKER only)
    - POST /api/approvals/{id}/reject/ - Reject (CHECKER only)
    - GET /api/approvals/my-requests/ - Get own requests (MAKER)
    - GET /api/approvals/pending-queue/ - Get pending for checker (CHECKER)
    """
    
    queryset = ApprovalRequest.objects.all()
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'request_type', 'maker_unit']
    search_fields = ['request_type', 'title', 'description', 'created_by__username']
    ordering_fields = ['created_at', 'status', 'request_type']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Use appropriate serializer based on action."""
        if self.action == 'retrieve':
            return ApprovalRequestDetailSerializer
        elif self.action == 'create':
            return ApprovalCreateSerializer
        elif self.action in ['approve', 'reject']:
            return ApprovalActionSerializer
        return ApprovalRequestSerializer
    
    def get_queryset(self):
        """
        Filter queryset based on user role and hierarchy.
        
        RULES:
        - ADMIN: See all
        - MAKER: See own requests only
        - CHECKER: See requests from lower units only
        """
        user = self.request.user
        
        # Check user roles
        is_admin = user.roles.filter(name='ADMIN').exists()
        is_maker = user.roles.filter(name='MAKER').exists()
        is_checker = user.roles.filter(name='CHECKER').exists()
        
        # ADMIN sees all
        if is_admin:
            return ApprovalRequest.objects.all().select_related(
                'created_by', 'assigned_checker', 'reviewed_by', 'maker_unit', 'checker_unit'
            )
        
        # MAKER sees only their own requests
        if is_maker and not is_checker:
            return ApprovalRequest.objects.filter(
                created_by=user
            ).select_related(
                'created_by', 'assigned_checker', 'reviewed_by', 'maker_unit', 'checker_unit'
            )
        
        # CHECKER sees requests from lower units
        if is_checker:
            if not user.unit:
                return ApprovalRequest.objects.none()
            
            # Get all descendant units (lower units)
            descendant_units = user.unit.get_all_children() + [user.unit]
            
            return ApprovalRequest.objects.filter(
                maker_unit__in=descendant_units
            ).select_related(
                'created_by', 'assigned_checker', 'reviewed_by', 'maker_unit', 'checker_unit'
            )
        
        # Default: no access
        return ApprovalRequest.objects.none()
    
    def perform_create(self, serializer):
        """
        Create approval request and route to eligible checker.
        
        RULES:
        - Only MAKER role can create
        - User must be assigned to a unit
        - Request is automatically routed to checker in ancestor unit
        """
        user = self.request.user
        
        # Verify MAKER role
        if not user.roles.filter(name='MAKER').exists():
            raise ValidationError("Only users with MAKER role can create approval requests")
        
        # Verify unit assignment
        if not user.unit:
            raise ValidationError("You must be assigned to a unit to create requests")
        
        # Create via service (handles routing) and save to instance
        approval = ApprovalService.create_approval_request(
            request_type=serializer.validated_data.get('request_type'),
            title=serializer.validated_data.get('title', ''),
            description=serializer.validated_data.get('description', ''),
            payload=serializer.validated_data.get('payload', {}),
            maker=user
        )
        # Set the instance for DRF response
        self.instance = approval
    
    def retrieve(self, request, *args, **kwargs):
        """Get approval detail with access control."""
        approval = self.get_object()
        
        # Access control
        user = request.user
        is_admin = user.roles.filter(name='ADMIN').exists()
        is_creator = approval.created_by == user
        is_assigned_checker = approval.assigned_checker == user
        
        # Check if eligible (ADMIN, creator, or assigned checker in upper unit)
        is_eligible_checker = (
            user.roles.filter(name='CHECKER').exists() and
            approval.is_eligible_for_checker(user)
        )
        
        if not (is_admin or is_creator or is_assigned_checker or is_eligible_checker):
            return Response(
                {'error': 'You do not have permission to view this request'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(approval)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Approve an approval request (CHECKER only).
        
        POST /api/approvals/{id}/approve/
        Request body:
        {
            "remarks": "Approved as requested"
        }
        """
        approval = self.get_object()
        
        try:
            remarks = request.data.get('remarks', '')
            
            # Verify CHECKER role
            if not request.user.roles.filter(name='CHECKER').exists():
                return Response(
                    {'error': 'Only CHECKER role can approve requests'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Verify eligibility
            if not approval.is_eligible_for_checker(request.user):
                return Response(
                    {'error': 'You are not eligible to review this request. Maker must be in a subordinate unit.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Approve via service
            ApprovalService.approve_request(approval, request.user, remarks)
            
            serializer = ApprovalRequestDetailSerializer(approval)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """
        Reject an approval request (CHECKER only).
        
        POST /api/approvals/{id}/reject/
        Request body:
        {
            "remarks": "Rejection reason"
        }
        """
        approval = self.get_object()
        
        try:
            remarks = request.data.get('remarks', '')
            
            # Verify CHECKER role
            if not request.user.roles.filter(name='CHECKER').exists():
                return Response(
                    {'error': 'Only CHECKER role can reject requests'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Verify eligibility
            if not approval.is_eligible_for_checker(request.user):
                return Response(
                    {'error': 'You are not eligible to review this request. Maker must be in a subordinate unit.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Reject via service
            ApprovalService.reject_request(approval, request.user, remarks)
            
            serializer = ApprovalRequestDetailSerializer(approval)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'], url_path='my-requests')
    def my_requests(self, request):
        """
        Get all requests created by current user (MAKER).
        
        GET /api/approvals/my-requests/
        """
        approvals = ApprovalService.get_maker_requests(request.user)
        serializer = ApprovalRequestSerializer(approvals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='pending-queue')
    def pending_queue(self, request):
        """
        Get pending approval queue for current user (CHECKER).
        
        GET /api/approvals/pending-queue/
        
        Returns requests from lower units eligible for this checker.
        """
        # Verify CHECKER role
        if not request.user.roles.filter(name='CHECKER').exists():
            return Response(
                {'error': 'Only CHECKER role can view approval queue'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        approvals = ApprovalService.get_checker_queue(request.user)
        serializer = ApprovalRequestSerializer(approvals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='statistics')
    def statistics(self, request):
        """
        Get approval statistics.
        
        GET /api/approvals/statistics/
        """
        user = request.user
        unit = user.unit
        
        stats = ApprovalService.get_statistics(unit)
        return Response(stats, status=status.HTTP_200_OK)
