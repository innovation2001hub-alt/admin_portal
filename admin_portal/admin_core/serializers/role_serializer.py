"""
Serializers for Role model.
"""
from rest_framework import serializers
from admin_core.models import Role


class RoleSerializer(serializers.ModelSerializer):
    """
    Serializer for Role model.
    
    Handles serialization/deserialization of Role objects with full validation.
    """
    
    class Meta:
        model = Role
        fields = [
            'id',
            'name',
            'description',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'name': {'required': True, 'min_length': 3, 'max_length': 100},
            'description': {'required': True, 'min_length': 10},
        }
    
    def validate_name(self, value):
        """Validate that role name is unique (case-insensitive)."""
        existing = Role.objects.filter(name__iexact=value)
        if self.instance:
            existing = existing.exclude(id=self.instance.id)
        if existing.exists():
            raise serializers.ValidationError("A role with this name already exists.")
        return value.upper()
