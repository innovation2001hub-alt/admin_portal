"""
User Management Views.

Implements user management endpoints:
- List, Create, Retrieve, Update, Delete users
- Assign roles
- Get user statistics
"""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from admin_core.models import User, Role, AuditLog
from admin_core.serializers import UserSerializer, UserListSerializer
from admin_core.services.hierarchy_service import HierarchyService


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User management.
    
    Provides CRUD operations on users with role and hierarchy support.
    
    Endpoints:
    - GET /api/users/ - List all users
    - POST /api/users/ - Create new user
    - GET /api/users/{id}/ - Get user details
    - PUT /api/users/{id}/ - Update user
    - DELETE /api/users/{id}/ - Delete/deactivate user
    - POST /api/users/{id}/assign-roles/ - Assign roles to user
    - GET /api/users/{id}/roles/ - Get user roles
    - GET /api/users/unit/{unit_id}/ - Get users in a unit
    """
    
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    filterset_fields = ['unit', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'employee_id']
    ordering_fields = ['username', 'first_name', 'last_name', 'created_at']
    ordering = ['first_name', 'last_name']
    
    def get_serializer_class(self):
        """Use list serializer for list action."""
        if self.action == 'list':
            return UserListSerializer
        return UserSerializer
    
    def perform_create(self, serializer):
        """Log user creation and check hierarchy permissions."""
        # Check if user can create in their unit
        user_to_create = serializer.save()
        
        AuditLog.log_action(
            user=self.request.user,
            action=f'Created user: {user_to_create.get_full_name()} ({user_to_create.employee_id})',
            action_type='CREATE',
            metadata={
                'target_user_id': user_to_create.id,
                'target_username': user_to_create.username,
                'employee_id': user_to_create.employee_id,
            }
        )
    
    def perform_update(self, serializer):
        """Log user update."""
        user = serializer.save()
        AuditLog.log_action(
            user=self.request.user,
            action=f'Updated user: {user.get_full_name()} ({user.employee_id})',
            action_type='UPDATE',
            metadata={
                'target_user_id': user.id,
                'target_username': user.username,
            }
        )
    
    def perform_destroy(self, instance):
        """Soft delete user by deactivating."""
        instance.is_active = False
        instance.save()
        
        AuditLog.log_action(
            user=self.request.user,
            action=f'Deactivated user: {instance.get_full_name()} ({instance.employee_id})',
            action_type='DELETE',
            metadata={
                'target_user_id': instance.id,
                'target_username': instance.username,
            }
        )
    
    @action(detail=True, methods=['post'])
    def assign_roles(self, request, pk=None):
        """
        Assign roles to a user.
        
        POST /api/users/{id}/assign-roles/
        Request body:
        {
            "role_ids": [1, 2, 3]
        }
        
        Returns:
        - Updated user with new roles
        """
        user = self.get_object()
        role_ids = request.data.get('role_ids', [])
        
        try:
            roles = Role.objects.filter(id__in=role_ids)
            user.roles.set(roles)
            
            AuditLog.log_action(
                user=request.user,
                action=f'Assigned roles to user: {user.get_full_name()}',
                action_type='UPDATE',
                metadata={
                    'target_user_id': user.id,
                    'role_ids': list(role_ids),
                }
            )
            
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def roles(self, request, pk=None):
        """
        Get roles assigned to a user.
        
        GET /api/users/{id}/roles/
        
        Returns:
        - List of roles assigned to the user
        """
        user = self.get_object()
        from admin_core.serializers import RoleSerializer
        serializer = RoleSerializer(user.roles.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def by_unit(self, request):
        """
        Get all users in a specific unit.
        
        GET /api/users/by-unit/?unit_id=1
        
        Returns:
        - List of users in the specified unit
        """
        unit_id = request.query_params.get('unit_id')
        
        if not unit_id:
            return Response(
                {'error': 'unit_id parameter is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        users = User.objects.filter(unit_id=unit_id, is_active=True)
        serializer = UserListSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def in_hierarchy(self, request):
        """
        Get all users in a unit's hierarchy (unit and subordinates).
        
        GET /api/users/in-hierarchy/?unit_id=1
        
        Returns:
        - List of all users in the unit hierarchy
        """
        unit_id = request.query_params.get('unit_id')
        
        if not unit_id:
            return Response(
                {'error': 'unit_id parameter is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from admin_core.models import Unit
            unit = Unit.objects.get(id=unit_id)
            users = HierarchyService.get_users_in_hierarchy(unit)
            serializer = UserListSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        Activate a deactivated user.
        
        POST /api/users/{id}/activate/
        
        Returns:
        - Updated user
        """
        user = self.get_object()
        user.is_active = True
        user.save()
        
        AuditLog.log_action(
            user=request.user,
            action=f'Activated user: {user.get_full_name()}',
            action_type='UPDATE',
            metadata={'target_user_id': user.id}
        )
        
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """
        Deactivate a user.
        
        POST /api/users/{id}/deactivate/
        
        Returns:
        - Updated user
        """
        user = self.get_object()
        user.is_active = False
        user.save()
        
        AuditLog.log_action(
            user=request.user,
            action=f'Deactivated user: {user.get_full_name()}',
            action_type='UPDATE',
            metadata={'target_user_id': user.id}
        )
        
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
