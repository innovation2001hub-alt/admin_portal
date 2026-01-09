"""
Approval Request Views.

Implements Maker-Checker workflow endpoints:
- List, Create approval requests
- Approve/Reject requests
- Get pending approvals
"""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from admin_core.models import ApprovalRequest, AuditLog
from admin_core.serializers import (
    ApprovalRequestSerializer,
    ApprovalRequestDetailSerializer,
    ApprovalActionSerializer
)
from admin_core.services.approval_service import ApprovalService


class ApprovalRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Approval Request management.
    
    Implements Maker-Checker workflow with hierarchy-based routing.
    
    Endpoints:
    - GET /api/approvals/ - List approval requests
    - POST /api/approvals/ - Create approval request
    - GET /api/approvals/{id}/ - Get approval details
    - POST /api/approvals/{id}/approve/ - Approve request
    - POST /api/approvals/{id}/reject/ - Reject request
    - GET /api/approvals/pending/ - Get pending approvals for current user
    - GET /api/approvals/statistics/ - Get approval statistics
    """
    
    queryset = ApprovalRequest.objects.all()
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'action_type', 'maker', 'checker']
    search_fields = ['action_type', 'status']
    ordering_fields = ['created_at', 'status', 'action_type']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Use detailed serializer for retrieve action."""
        if self.action == 'retrieve':
            return ApprovalRequestDetailSerializer
        elif self.action in ['approve', 'reject']:
            return ApprovalActionSerializer
        return ApprovalRequestSerializer
    
    def perform_create(self, serializer):
        """Set maker to current user."""
        approval = serializer.save(maker=self.request.user)
        
        # Route to appropriate checker
        if not approval.checker:
            from admin_core.services.approval_service import ApprovalService
            routed_approval = ApprovalService.route_approval(
                self.request.user,
                approval.action_type,
                approval.payload
            )
            approval.checker = routed_approval.checker
            approval.save()
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Approve an approval request.
        
        POST /api/approvals/{id}/approve/
        Request body:
        {
            "comments": "Approved as requested"
        }
        
        Returns:
        - Updated approval request
        """
        approval = self.get_object()
        comments = request.data.get('comments', '')
        
        try:
            # Check if current user is the assigned checker
            if approval.checker.id != request.user.id:
                return Response(
                    {'error': 'Only the assigned checker can approve this request.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Approve the request
            ApprovalService.approve_request(approval, request.user, comments)
            
            serializer = ApprovalRequestDetailSerializer(approval)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """
        Reject an approval request.
        
        POST /api/approvals/{id}/reject/
        Request body:
        {
            "comments": "Rejection reason"
        }
        
        Returns:
        - Updated approval request
        """
        approval = self.get_object()
        comments = request.data.get('comments', '')
        
        try:
            # Check if current user is the assigned checker
            if approval.checker.id != request.user.id:
                return Response(
                    {'error': 'Only the assigned checker can reject this request.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Reject the request
            ApprovalService.reject_request(approval, request.user, comments)
            
            serializer = ApprovalRequestDetailSerializer(approval)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """
        Get all pending approval requests for the current user as checker.
        
        GET /api/approvals/pending/
        
        Returns:
        - List of pending approvals
        """
        approvals = ApprovalService.get_pending_approvals(request.user)
        serializer = ApprovalRequestSerializer(approvals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get approval statistics for the current user.
        
        GET /api/approvals/statistics/
        
        Returns:
        - Approval statistics
        """
        stats = ApprovalService.get_approval_statistics(request.user)
        return Response(stats, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def created_by_me(self, request):
        """
        Get all approval requests created by the current user.
        
        GET /api/approvals/created-by-me/
        
        Returns:
        - List of approval requests created by current user
        """
        approvals = ApprovalRequest.objects.filter(
            maker=request.user
        ).order_by('-created_at')
        
        serializer = ApprovalRequestSerializer(approvals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def assigned_to_me(self, request):
        """
        Get all approval requests assigned to the current user as checker.
        
        GET /api/approvals/assigned-to-me/
        
        Returns:
        - List of approval requests assigned to current user
        """
        approvals = ApprovalRequest.objects.filter(
            checker=request.user
        ).order_by('-created_at')
        
        serializer = ApprovalRequestSerializer(approvals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
