"""
Unit Management Views.

Implements organizational hierarchy endpoints:
- List, Create, Retrieve, Update units
- Get unit hierarchy information
"""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from admin_core.models import Unit
from admin_core.serializers import UnitSerializer, UnitDetailSerializer
from admin_core.services.hierarchy_service import HierarchyService
from admin_core.models import AuditLog


class UnitViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Unit management.
    
    Provides CRUD operations on organizational units with hierarchy support.
    
    Endpoints:
    - GET /api/units/ - List all units
    - POST /api/units/ - Create new unit
    - GET /api/units/{id}/ - Get unit details
    - PUT /api/units/{id}/ - Update unit
    - DELETE /api/units/{id}/ - Delete unit
    - GET /api/units/{id}/parent-chain/ - Get parent hierarchy
    - GET /api/units/{id}/children/ - Get child units
    - GET /api/units/{id}/users/ - Get users in unit
    """
    
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['unit_type', 'parent']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['code']
    
    def get_serializer_class(self):
        """Use detailed serializer for retrieve action."""
        if self.action == 'retrieve':
            return UnitDetailSerializer
        return UnitSerializer
    
    def perform_create(self, serializer):
        """Log unit creation."""
        unit = serializer.save()
        AuditLog.log_action(
            user=self.request.user,
            action=f'Created unit: {unit.name} ({unit.code})',
            action_type='CREATE',
            metadata={
                'unit_id': unit.id,
                'unit_name': unit.name,
                'unit_code': unit.code,
                'unit_type': unit.unit_type,
            }
        )
    
    def perform_update(self, serializer):
        """Log unit update."""
        unit = serializer.save()
        AuditLog.log_action(
            user=self.request.user,
            action=f'Updated unit: {unit.name} ({unit.code})',
            action_type='UPDATE',
            metadata={
                'unit_id': unit.id,
                'unit_name': unit.name,
                'unit_code': unit.code,
            }
        )
    
    def perform_destroy(self, instance):
        """Log unit deletion."""
        unit_info = {'id': instance.id, 'name': instance.name, 'code': instance.code}
        AuditLog.log_action(
            user=self.request.user,
            action=f'Deleted unit: {instance.name} ({instance.code})',
            action_type='DELETE',
            metadata=unit_info
        )
        instance.delete()
    
    @action(detail=True, methods=['get'])
    def parent_chain(self, request, pk=None):
        """
        Get the parent hierarchy chain for a unit.
        
        GET /api/units/{id}/parent-chain/
        
        Returns:
        - List of parent units from current to HO
        """
        unit = self.get_object()
        chain = unit.get_parent_chain()
        serializer = UnitSerializer(chain, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def children(self, request, pk=None):
        """
        Get all child units (direct children only).
        
        GET /api/units/{id}/children/
        
        Returns:
        - List of direct child units
        """
        unit = self.get_object()
        children = unit.children.all()
        serializer = UnitSerializer(children, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def all_children(self, request, pk=None):
        """
        Get all descendant units (recursive).
        
        GET /api/units/{id}/all-children/
        
        Returns:
        - List of all descendant units
        """
        unit = self.get_object()
        children = unit.get_all_children()
        serializer = UnitSerializer(children, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        """
        Get all users in a unit and its subordinates.
        
        GET /api/units/{id}/users/
        
        Returns:
        - List of users in the unit hierarchy
        """
        unit = self.get_object()
        users = HierarchyService.get_users_in_hierarchy(unit)
        
        from admin_core.serializers import UserListSerializer
        serializer = UserListSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """
        Get statistics for a unit.
        
        GET /api/units/{id}/statistics/
        
        Returns:
        - Statistics including user count, child unit count, etc.
        """
        unit = self.get_object()
        return Response({
            'unit_id': unit.id,
            'unit_name': unit.name,
            'unit_code': unit.code,
            'unit_type': unit.unit_type,
            'total_users': unit.users.count(),
            'direct_children': unit.children.count(),
            'all_descendants': len(unit.get_all_children()) + 1,
            'parent': unit.parent.id if unit.parent else None,
        }, status=status.HTTP_200_OK)
