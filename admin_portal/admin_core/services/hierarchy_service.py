"""
Hierarchy Service.

Handles organizational hierarchy operations and hierarchy-based permissions.
"""
from admin_core.models import Unit, User, AuditLog


class HierarchyService:
    """
    Service class for handling organizational hierarchy operations.
    
    Methods:
    - get_subordinate_units: Get all units under a given unit
    - get_superior_units: Get all parent units
    - can_access_unit: Check if user can access a unit
    - can_manage_unit: Check if user can manage a unit
    - get_users_in_hierarchy: Get all users in a hierarchy
    """
    
    @staticmethod
    def get_subordinate_units(unit):
        """
        Get all subordinate (child) units of a given unit.
        
        Args:
            unit: Unit object
        
        Returns:
            QuerySet of Unit objects (all descendants)
        """
        subordinates = [unit]
        subordinates.extend(unit.get_all_children())
        return Unit.objects.filter(id__in=[u.id for u in subordinates])
    
    @staticmethod
    def get_superior_units(unit):
        """
        Get all superior (parent) units of a given unit.
        
        Args:
            unit: Unit object
        
        Returns:
            List of Unit objects from current to HO
        """
        return unit.get_parent_chain()
    
    @staticmethod
    def can_access_unit(user, unit):
        """
        Check if user can access a unit.
        User can access their own unit and all parent units.
        
        Args:
            user: User object
            unit: Unit object to check access
        
        Returns:
            Boolean indicating access permission
        """
        if not user.unit:
            return False
        
        # User can access their own unit
        if user.unit.id == unit.id:
            return True
        
        # User can access all parent units
        parent_chain = user.unit.get_parent_chain()
        return unit in parent_chain
    
    @staticmethod
    def can_manage_unit(user, unit):
        """
        Check if user can manage a unit.
        User can manage their own unit and all subordinate units.
        
        Args:
            user: User object
            unit: Unit object to check management permission
        
        Returns:
            Boolean indicating management permission
        """
        if not user.unit:
            return False
        
        # User can manage their own unit
        if user.unit.id == unit.id:
            return True
        
        # User can manage all subordinate units
        subordinates = HierarchyService.get_subordinate_units(user.unit)
        return subordinates.filter(id=unit.id).exists()
    
    @staticmethod
    def get_users_in_hierarchy(unit, include_self=True):
        """
        Get all users in a unit's hierarchy.
        
        Args:
            unit: Unit object
            include_self: Whether to include users in the unit itself
        
        Returns:
            QuerySet of User objects
        """
        subordinates = HierarchyService.get_subordinate_units(unit)
        users = User.objects.filter(unit__in=subordinates)
        
        if not include_self:
            users = users.exclude(unit=unit)
        
        return users
    
    @staticmethod
    def get_immediate_superior(unit):
        """
        Get the immediate superior unit.
        
        Args:
            unit: Unit object
        
        Returns:
            Parent unit or None if it's the root (HO)
        """
        return unit.parent
    
    @staticmethod
    def get_immediate_subordinates(unit):
        """
        Get immediate child units (direct reports).
        
        Args:
            unit: Unit object
        
        Returns:
            QuerySet of direct child units
        """
        return unit.children.all()
    
    @staticmethod
    def create_hierarchy_level(parent_unit, name, code, unit_type):
        """
        Create a new unit in the hierarchy.
        
        Args:
            parent_unit: Parent Unit object (None for creating HO)
            name: Name of the new unit
            code: Unique code
            unit_type: Type of unit
        
        Returns:
            Created Unit object
        """
        unit = Unit.objects.create(
            name=name,
            code=code,
            unit_type=unit_type,
            parent=parent_unit
        )
        
        # Log the creation
        AuditLog.log_action(
            user=None,
            action=f'Created unit: {name} ({code})',
            action_type='CREATE',
            metadata={
                'unit_id': unit.id,
                'unit_name': name,
                'unit_code': code,
                'unit_type': unit_type,
            }
        )
        
        return unit
