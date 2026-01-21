"""
User Management Serializer - for Super Admin to manage users.
"""
from rest_framework import serializers
from admin_core.models import User, Role, Unit


class UserManagementSerializer(serializers.ModelSerializer):
    """Serializer for super admin user management."""
    
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    roles = serializers.SerializerMethodField()
    role_ids = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        write_only=True,
        required=False,
        many=True,
        source='roles'
    )
    unit_id = serializers.PrimaryKeyRelatedField(
        queryset=Unit.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
        source='unit'
    )
    unit_display = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'password',
            'first_name',
            'last_name',
            'employee_id',
            'unit_id',
            'unit_display',
            'roles',
            'role_ids',
            'is_active',
            'is_staff',
            'is_superuser',
            'date_joined',
            'last_login',
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }
    
    def get_roles(self, obj):
        """Get role details."""
        return [
            {'id': role.id, 'name': role.name, 'description': role.description}
            for role in obj.roles.all()
        ]
    
    def get_unit_display(self, obj):
        """Get unit details."""
        if obj.unit:
            return {
                'id': obj.unit.id,
                'code': obj.unit.code,
                'name': obj.unit.name,
                'unit_type': obj.unit.unit_type,
            }
        return None
    
    def create(self, validated_data):
        """Create a new user."""
        roles = validated_data.pop('roles', [])
        password = validated_data.pop('password', None)
        
        # Create user
        user = User.objects.create_user(
            username=validated_data.get('username'),
            email=validated_data.get('email', ''),
            password=password or 'Temp@123',  # Default temp password
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            employee_id=validated_data.get('employee_id', ''),
            unit=validated_data.get('unit'),
            is_active=validated_data.get('is_active', True),
        )
        
        # Assign roles
        for role in roles:
            user.roles.add(role)
        
        return user
    
    def update(self, instance, validated_data):
        """Update user."""
        roles = validated_data.pop('roles', None)
        
        # Update fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update roles if provided
        if roles is not None:
            instance.roles.clear()
            for role in roles:
                instance.roles.add(role)
        
        return instance


class UserListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing users."""
    
    roles = serializers.SerializerMethodField()
    unit_display = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'employee_id',
            'unit_display',
            'roles',
            'is_active',
            'date_joined',
        ]
    
    def get_roles(self, obj):
        """Get role details."""
        return [{'id': role.id, 'name': role.name} for role in obj.roles.all()]
    
    def get_unit_display(self, obj):
        """Get unit details."""
        if obj.unit:
            return {
                'id': obj.unit.id,
                'name': obj.unit.name,
                'code': obj.unit.code,
            }
        return None
