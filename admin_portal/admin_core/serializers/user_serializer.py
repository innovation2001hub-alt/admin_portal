"""
Serializers for User model.
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from admin_core.models import User, Role, Unit


class RoleSimpleSerializer(serializers.ModelSerializer):
    """Simple serializer for Role in nested contexts."""
    class Meta:
        model = Role
        fields = ['id', 'name']
    
    def to_representation(self, instance):
        """Include all roles including SUPER_ADMIN."""
        return super().to_representation(instance)


class UnitSimpleSerializer(serializers.ModelSerializer):
    """Simple serializer for Unit in nested contexts."""
    class Meta:
        model = Unit
        fields = ['id', 'name', 'code', 'unit_type']


class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer for User list representation.
    Returns essential user information for list views.
    """
    unit = UnitSimpleSerializer(read_only=True)
    roles = RoleSimpleSerializer(many=True, read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id',
            'employee_id',
            'username',
            'first_name',
            'last_name',
            'full_name',
            'email',
            'designation',
            'unit',
            'roles',
            'is_active',
        ]
        read_only_fields = ['id', 'full_name']
    
    def to_representation(self, instance):
        """Filter out non-standard roles from the roles list."""
        ret = super().to_representation(instance)
        if 'roles' in ret and ret['roles']:
            ret['roles'] = [role for role in ret['roles'] if role is not None]
        return ret


class UserSerializer(serializers.ModelSerializer):
    """
    Full serializer for User model.
    Handles creation, update, and detailed representation.
    """
    unit = UnitSimpleSerializer(read_only=True)
    unit_id = serializers.PrimaryKeyRelatedField(
        queryset=Unit.objects.all(),
        source='unit',
        write_only=True,
        required=False,
        allow_null=True,
    )
    roles = RoleSimpleSerializer(many=True, read_only=True)
    role_ids = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        source='roles',
        many=True,
        write_only=True,
        required=False,
    )
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, required=True, min_length=8)
    
    class Meta:
        model = User
        fields = [
            'id',
            'employee_id',
            'username',
            'password',
            'password_confirm',
            'first_name',
            'last_name',
            'full_name',
            'email',
            'designation',
            'unit',
            'unit_id',
            'roles',
            'role_ids',
            'is_active',
        ]
        read_only_fields = ['id', 'full_name']
        extra_kwargs = {
            'username': {'required': True, 'min_length': 3},
            'email': {'required': True},
            'employee_id': {'required': True},
            'designation': {'required': True},
        }
    
    def to_representation(self, instance):
        """Filter out non-standard roles from the roles list."""
        ret = super().to_representation(instance)
        if 'roles' in ret and ret['roles']:
            ret['roles'] = [role for role in ret['roles'] if role is not None]
        return ret
    
    def validate_password(self, value):
        """Validate password strength."""
        validate_password(value)
        return value
    
    def validate(self, data):
        """Validate password confirmation and username uniqueness."""
        password = data.get('password')
        password_confirm = self.initial_data.get('password_confirm')
        
        if password != password_confirm:
            raise serializers.ValidationError(
                {'password_confirm': 'Passwords do not match.'}
            )
        
        # Check username uniqueness
        username = data.get('username')
        if username:
            existing = User.objects.filter(username__iexact=username)
            if self.instance:
                existing = existing.exclude(id=self.instance.id)
            if existing.exists():
                raise serializers.ValidationError(
                    {'username': 'A user with this username already exists.'}
                )
        
        # Check employee_id uniqueness
        employee_id = data.get('employee_id')
        if employee_id:
            existing = User.objects.filter(employee_id=employee_id)
            if self.instance:
                existing = existing.exclude(id=self.instance.id)
            if existing.exists():
                raise serializers.ValidationError(
                    {'employee_id': 'A user with this employee ID already exists.'}
                )
        
        return data
    
    def create(self, validated_data):
        """Create user with hashed password."""
        password = validated_data.pop('password')
        validated_data.pop('password_confirm', None)  # Remove password_confirm as it's not a model field
        roles = validated_data.pop('roles', [])
        
        user = User.objects.create_user(password=password, **validated_data)
        user.roles.set(roles)
        return user
    
    def update(self, instance, validated_data):
        """Update user, handling password separately if provided."""
        password = validated_data.pop('password', None)
        roles = validated_data.pop('roles', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        
        if roles is not None:
            instance.roles.set(roles)
        
        return instance
