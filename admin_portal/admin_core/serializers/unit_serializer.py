"""
Serializers for Unit model (Organizational Hierarchy).
"""
from rest_framework import serializers
from admin_core.models import Unit


class UnitSerializer(serializers.ModelSerializer):
    """
    Basic serializer for Unit model.
    Used for listing and nested representations.
    """
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    children_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Unit
        fields = [
            'id',
            'name',
            'code',
            'unit_type',
            'parent',
            'parent_name',
            'children_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'children_count']
        extra_kwargs = {
            'name': {'required': True, 'min_length': 3},
            'code': {'required': True, 'min_length': 2},
            'unit_type': {'required': True},
        }
    
    def get_children_count(self, obj):
        """Get count of direct children."""
        return obj.children.count()
    
    def validate_code(self, value):
        """Validate that unit code is unique."""
        existing = Unit.objects.filter(code__iexact=value)
        if self.instance:
            existing = existing.exclude(id=self.instance.id)
        if existing.exists():
            raise serializers.ValidationError("A unit with this code already exists.")
        return value.upper()
    
    def validate(self, data):
        """Validate unit hierarchy constraints."""
        if 'parent' in data and data['parent']:
            parent = data['parent']
            # Cannot be its own parent
            if self.instance and parent.id == self.instance.id:
                raise serializers.ValidationError(
                    {'parent': 'A unit cannot be its own parent.'}
                )
            # Parent cannot be a descendant
            if self.instance and self.instance.is_descendant_of(parent):
                raise serializers.ValidationError(
                    {'parent': 'Cannot set a descendant unit as parent.'}
                )
        return data


class UnitDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for Unit model.
    Includes parent chain and children information.
    """
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    parent_chain = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()
    user_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Unit
        fields = [
            'id',
            'name',
            'code',
            'unit_type',
            'parent',
            'parent_name',
            'parent_chain',
            'children',
            'user_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'parent_chain',
            'children',
            'user_count',
        ]
    
    def get_parent_chain(self, obj):
        """Get the hierarchical chain of parent units."""
        chain = obj.get_parent_chain()
        return [{'id': u.id, 'name': u.name, 'code': u.code} for u in chain[:-1]]
    
    def get_children(self, obj):
        """Get direct children units."""
        children = obj.children.all()
        return UnitSerializer(children, many=True).data
    
    def get_user_count(self, obj):
        """Get count of users in this unit."""
        return obj.users.count()
