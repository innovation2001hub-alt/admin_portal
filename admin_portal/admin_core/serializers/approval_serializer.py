"""
Serializers for ApprovalRequest model (Maker-Checker Workflow).
"""
from rest_framework import serializers
from admin_core.models import ApprovalRequest, User


class UserSimpleSerializer(serializers.ModelSerializer):
    """Simple serializer for User in nested contexts."""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'employee_id']


class ApprovalRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for ApprovalRequest model.
    Handles creation and listing of approval requests.
    """
    maker = UserSimpleSerializer(read_only=True)
    checker = UserSimpleSerializer(read_only=True)
    is_pending = serializers.SerializerMethodField()
    
    class Meta:
        model = ApprovalRequest
        fields = [
            'id',
            'action_type',
            'payload',
            'maker',
            'checker',
            'status',
            'is_pending',
            'created_at',
            'updated_at',
            'completed_at',
        ]
        read_only_fields = [
            'id',
            'maker',
            'checker',
            'created_at',
            'updated_at',
            'completed_at',
            'is_pending',
        ]
        extra_kwargs = {
            'action_type': {'required': True, 'min_length': 3},
            'payload': {'required': True},
            'status': {'read_only': True},
        }
    
    def get_is_pending(self, obj):
        """Check if approval request is still pending."""
        return obj.is_pending()


class ApprovalRequestDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for ApprovalRequest.
    Includes full user information and comments.
    """
    maker = UserSimpleSerializer(read_only=True)
    checker = UserSimpleSerializer(read_only=True)
    is_pending = serializers.SerializerMethodField()
    
    class Meta:
        model = ApprovalRequest
        fields = [
            'id',
            'action_type',
            'payload',
            'maker',
            'checker',
            'status',
            'is_pending',
            'comments',
            'created_at',
            'updated_at',
            'completed_at',
        ]
        read_only_fields = [
            'id',
            'maker',
            'checker',
            'payload',
            'action_type',
            'created_at',
            'updated_at',
            'completed_at',
            'is_pending',
        ]
    
    def get_is_pending(self, obj):
        """Check if approval request is still pending."""
        return obj.is_pending()


class ApprovalActionSerializer(serializers.Serializer):
    """
    Serializer for approval actions (approve/reject).
    """
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    comments = serializers.CharField(
        max_length=1000,
        allow_blank=True,
        required=False
    )
    
    def validate(self, data):
        """Additional validation for approval action."""
        action = data.get('action')
        if action not in ['approve', 'reject']:
            raise serializers.ValidationError('Invalid action.')
        return data
