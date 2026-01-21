from django.db import models


class Unit(models.Model):
    """
    Unit model representing organizational hierarchy.
    
    Supports self-referencing parent structure to create an organizational tree.
    Implements hierarchy-based access control for approval workflows.
    
    Fields:
    - name: Display name of the unit
    - code: Unique code identifier (e.g., 'HO001', 'CIRCLE001')
    - unit_type: Type of unit (HO, CIRCLE, NETWORK, AO, RBO, BRANCH)
    - parent: Self-referencing ForeignKey for hierarchical structure
    - created_at: Timestamp when the unit was created
    - updated_at: Timestamp when the unit was last modified
    """
    UNIT_TYPES = [
        ('CO', 'Corporate Office'),
        ('LHO', 'Local Head Office'),
        ('AO', 'Administrative Office'),
        ('RO', 'Regional Office'),
        ('BR', 'Branch'),
    ]

    name = models.CharField(max_length=100, help_text="Display name of the unit")
    code = models.CharField(max_length=20, unique=True, help_text="Unique unit code")
    unit_type = models.CharField(
        max_length=10,
        choices=UNIT_TYPES,
        help_text="Type of organizational unit"
    )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children',
        help_text="Parent unit in the hierarchy"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'admin_core_unit'
        verbose_name = 'Unit'
        verbose_name_plural = 'Units'
        ordering = ['code']
        unique_together = ['code', 'unit_type']
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def get_parent_chain(self):
        """
        Get all parent units up to the root (Head Office).
        Returns a list of units from current unit to HO, inclusive.
        
        Example: Branch -> Region -> Circle -> HO returns [HO, Circle, Region, Branch]
        """
        chain = [self]
        current = self
        while current.parent:
            chain.insert(0, current.parent)
            current = current.parent
        return chain
    
    def get_ancestors(self):
        """
        Get all ancestor (parent and above) units.
        Does NOT include the current unit.
        Returns a list from immediate parent to root.
        
        Example: if self is Branch, returns [Region, Circle, HO]
        """
        ancestors = []
        current = self.parent
        while current:
            ancestors.append(current)
            current = current.parent
        return ancestors
    
    def get_all_children(self):
        """
        Get all child units recursively (flattened list).
        Does NOT include the current unit.
        Returns all descendants at any level.
        
        Example: if self is Circle, returns all Regions, Branches under it
        """
        children = list(self.children.all())
        for child in self.children.all():
            children.extend(child.get_all_children())
        return children
    
    def get_descendants(self):
        """
        Alias for get_all_children() - returns all descendant units recursively.
        """
        return self.get_all_children()
    
    def get_root_unit(self):
        """
        Get the Head Office (HO) unit for this unit's hierarchy.
        """
        chain = self.get_parent_chain()
        return chain[0] if chain else self
    
    def is_ancestor_of(self, unit):
        """
        Check if this unit is an ancestor (parent/above) of the given unit.
        
        Args:
            unit: The Unit to check against
            
        Returns:
            True if this unit is in the given unit's parent chain (above it)
        """
        if not unit:
            return False
        return self in unit.get_ancestors()
    
    def is_descendant_of(self, unit):
        """
        Check if this unit is a descendant (child/below) of the given unit.
        
        Args:
            unit: The Unit to check against
            
        Returns:
            True if this unit is in the given unit's descendants (below it)
        """
        if not unit:
            return False
        return self in unit.get_all_children()
    
    def is_sibling_of(self, unit):
        """
        Check if this unit shares the same parent as the given unit.
        """
        if not unit:
            return False
        return self.parent == unit.parent and self.id != unit.id
    
    def get_eligible_checkers(self):
        """
        Get all CHECKER role users from this unit's ancestors.
        
        Used for routing approval requests from makers in lower units
        to checkers in upper units.
        
        Returns:
            QuerySet of User objects with CHECKER role in ancestor units
        """
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        ancestors = self.get_ancestors()
        
        if not ancestors:
            # If no ancestors, return empty queryset
            return User.objects.none()
        
        return User.objects.filter(
            unit__in=ancestors,
            roles__name='CHECKER',
            is_active=True
        ).distinct()


