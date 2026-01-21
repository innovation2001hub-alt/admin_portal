"""
Serializers for ApprovalRequest model (Maker-Checker Workflow with Hierarchy Routing).
"""
from rest_framework import serializers
from admin_core.models import ApprovalRequest, ApprovalLog, User, Unit


class UserSimpleSerializer(serializers.ModelSerializer):
    """Simple serializer for User in nested contexts."""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'employee_id']


class UnitSimpleSerializer(serializers.ModelSerializer):
    """Simple serializer for Unit in nested contexts."""
    class Meta:
        model = Unit
        fields = ['id', 'name', 'code', 'unit_type']


class ApprovalLogSerializer(serializers.ModelSerializer):
    """Serializer for ApprovalLog audit trail."""
    performed_by = UserSimpleSerializer(read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = ApprovalLog
        fields = ['id', 'action', 'action_display', 'performed_by', 'remarks', 'timestamp']
        read_only_fields = ['id', 'action', 'action_display', 'performed_by', 'timestamp']


class ApprovalRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for ApprovalRequest model.
    Handles creation and listing of approval requests.
    
    Used by MAKER to create requests and ADMIN/CHECKER to view.
    """
    created_by = UserSimpleSerializer(read_only=True)
    assigned_checker = UserSimpleSerializer(read_only=True)
    maker_unit = UnitSimpleSerializer(read_only=True)
    checker_unit = UnitSimpleSerializer(read_only=True)
    is_pending = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ApprovalRequest
        fields = [
            'id',
            'request_type',
            'title',
            'description',
            'payload',
            'created_by',
            'maker_unit',
            'assigned_checker',
            'checker_unit',
            'status',
            'status_display',
            'is_pending',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_by',
            'maker_unit',
            'assigned_checker',
            'checker_unit',
            'status',
            'status_display',
            'created_at',
            'updated_at',
            'is_pending',
        ]
        extra_kwargs = {
            'request_type': {'required': True, 'min_length': 3},
            'payload': {'required': False, 'allow_null': True},
        }
    
    def get_is_pending(self, obj):
        """Check if approval request is still pending."""
        return obj.is_pending()


class ApprovalRequestDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for ApprovalRequest.
    
    Includes full user information, remarks, review timestamps, and audit logs.
    Used for detail view by all roles.
    """
    created_by = UserSimpleSerializer(read_only=True)
    assigned_checker = UserSimpleSerializer(read_only=True)
    reviewed_by = UserSimpleSerializer(read_only=True)
    maker_unit = UnitSimpleSerializer(read_only=True)
    checker_unit = UnitSimpleSerializer(read_only=True)
    is_pending = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    logs = ApprovalLogSerializer(many=True, read_only=True)
    
    class Meta:
        model = ApprovalRequest
        fields = [
            'id',
            'request_type',
            'title',
            'description',
            'payload',
            'created_by',
            'maker_unit',
            'assigned_checker',
            'checker_unit',
            'status',
            'status_display',
            'is_pending',
            'reviewed_by',
            'reviewed_at',
            'remarks',
            'created_at',
            'updated_at',
            'logs',
        ]
        read_only_fields = [
            'id',
            'request_type',
            'created_by',
            'maker_unit',
            'assigned_checker',
            'checker_unit',
            'payload',
            'status',
            'status_display',
            'is_pending',
            'reviewed_by',
            'reviewed_at',
            'remarks',
            'created_at',
            'updated_at',
            'logs',
        ]
    
    def get_is_pending(self, obj):
        """Check if approval request is still pending."""
        return obj.is_pending()


class ApprovalCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for MAKER to create new approval requests.
    
    Validates hierarchy and enforces business rules.
    """
    class Meta:
        model = ApprovalRequest
        fields = [
            'request_type',
            'title',
            'description',
            'payload',
        ]
        extra_kwargs = {
            'request_type': {'required': True, 'min_length': 3},
            'title': {'required': False, 'allow_blank': True},
            'description': {'required': False, 'allow_blank': True},
            'payload': {'required': False, 'allow_null': True},
        }
    
    def validate(self, data):
        """Validate that payload is valid JSON."""
        payload = data.get('payload')
        if payload and not isinstance(payload, dict):
            raise serializers.ValidationError(
                {'payload': 'Payload must be a valid JSON object'}
            )
        return data


class ApprovalActionSerializer(serializers.Serializer):
    """
    Serializer for approval actions (approve/reject).
    Accepts remarks from CHECKER when approving/rejecting.
    """
    remarks = serializers.CharField(required=False, allow_blank=True, max_length=1000)
    
    class Meta:
        fields = ['remarks']
