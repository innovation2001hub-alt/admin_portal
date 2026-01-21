"""
User Management Views - for Super Admin.

Allows super admin to:
- List all users
- Create new users
- Update user info, roles, and units
- Delete users
- Search/filter users
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.db import transaction
from django.core.exceptions import ValidationError

from admin_core.models import User, Role, Unit
from admin_core.serializers.user_management_serializer import (
    UserManagementSerializer,
    UserListSerializer,
)


class IsSuperAdmin:
    """Permission check for super admin access."""
    
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.roles.filter(name='SUPER_ADMIN').exists()
        )


class UserManagementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for super admin to manage users.
    
    Endpoints:
    - GET /api/user-management/ - List all users
    - POST /api/user-management/ - Create new user
    - GET /api/user-management/{id}/ - Get user details
    - PUT/PATCH /api/user-management/{id}/ - Update user
    - DELETE /api/user-management/{id}/ - Delete user
    - GET /api/user-management/available-roles/ - Get available roles
    - GET /api/user-management/available-units/ - Get available units
    - POST /api/user-management/{id}/assign-roles/ - Assign roles to user
    - POST /api/user-management/{id}/assign-unit/ - Assign unit to user
    - POST /api/user-management/{id}/reset-password/ - Reset user password
    """
    
    queryset = User.objects.all()
    serializer_class = UserManagementSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        return UserManagementSerializer
    
    def check_super_admin_permission(self):
        """Check if user is super admin."""
        if not self.request.user.roles.filter(name='SUPER_ADMIN').exists():
            raise PermissionDenied("Only super admin can access user management")
    
    def list(self, request, *args, **kwargs):
        """List all users (super admin only)."""
        self.check_super_admin_permission()
        
        queryset = self.get_queryset().select_related('unit').prefetch_related('roles')
        
        # Filter by unit if provided
        unit_id = request.query_params.get('unit_id')
        if unit_id:
            queryset = queryset.filter(unit_id=unit_id)
        
        # Filter by is_active if provided
        is_active = request.query_params.get('is_active')
        if is_active:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Search by username or email
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                username__icontains=search
            ) | queryset.filter(email__icontains=search)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """Create a new user (super admin only)."""
        self.check_super_admin_permission()
        
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """Update user (super admin only)."""
        self.check_super_admin_permission()
        
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Delete user (super admin only)."""
        self.check_super_admin_permission()
        
        user = self.get_object()
        
        # Don't allow deleting the super admin itself
        if user.roles.filter(name='SUPER_ADMIN').exists():
            return Response(
                {'error': 'Cannot delete super admin user'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'], url_path='available-roles')
    def available_roles(self, request):
        """Get all available roles."""
        self.check_super_admin_permission()
        
        roles = Role.objects.all()
        data = [
            {'id': role.id, 'name': role.name, 'description': role.description}
            for role in roles
        ]
        return Response(data)
    
    @action(detail=False, methods=['get'], url_path='available-units')
    def available_units(self, request):
        """Get all available units."""
        self.check_super_admin_permission()
        
        units = Unit.objects.all().select_related('parent')
        data = [
            {
                'id': unit.id,
                'code': unit.code,
                'name': unit.name,
                'unit_type': unit.unit_type,
                'parent_id': unit.parent_id,
            }
            for unit in units
        ]
        return Response(data)
    
    @action(detail=True, methods=['post'], url_path='assign-roles')
    def assign_roles(self, request, pk=None):
        """Assign roles to a user."""
        self.check_super_admin_permission()
        
        user = self.get_object()
        role_ids = request.data.get('role_ids', [])
        
        try:
            with transaction.atomic():
                user.roles.clear()
                for role_id in role_ids:
                    role = Role.objects.get(id=role_id)
                    user.roles.add(role)
            
            serializer = self.get_serializer(user)
            return Response(
                {'message': 'Roles assigned successfully', 'user': serializer.data},
                status=status.HTTP_200_OK
            )
        except Role.DoesNotExist:
            return Response(
                {'error': 'One or more roles not found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], url_path='assign-unit')
    def assign_unit(self, request, pk=None):
        """Assign a unit to a user."""
        self.check_super_admin_permission()
        
        user = self.get_object()
        unit_id = request.data.get('unit_id')
        
        try:
            if unit_id:
                unit = Unit.objects.get(id=unit_id)
                user.unit = unit
            else:
                user.unit = None
            
            user.save()
            serializer = self.get_serializer(user)
            return Response(
                {'message': 'Unit assigned successfully', 'user': serializer.data},
                status=status.HTTP_200_OK
            )
        except Unit.DoesNotExist:
            return Response(
                {'error': 'Unit not found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], url_path='reset-password')
    def reset_password(self, request, pk=None):
        """Reset user password."""
        self.check_super_admin_permission()
        
        user = self.get_object()
        new_password = request.data.get('password')
        
        if not new_password:
            return Response(
                {'error': 'Password is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user.set_password(new_password)
            user.save()
            return Response(
                {'message': f'Password reset successfully for {user.username}'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], url_path='toggle-active')
    def toggle_active(self, request, pk=None):
        """Toggle user active status."""
        self.check_super_admin_permission()
        
        user = self.get_object()
        
        # Don't allow deactivating super admin
        if user.roles.filter(name='SUPER_ADMIN').exists():
            return Response(
                {'error': 'Cannot deactivate super admin user'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.is_active = not user.is_active
        user.save()
        
        serializer = self.get_serializer(user)
        return Response(
            {'message': f'User status updated', 'user': serializer.data},
            status=status.HTTP_200_OK
        )
