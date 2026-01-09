from django.db import models


class Unit(models.Model):
    """
    Unit model representing organizational hierarchy.
    
    Supports self-referencing parent structure to create an organizational tree.
    
    Fields:
    - name: Display name of the unit
    - code: Unique code identifier (e.g., 'HO001', 'CIRCLE001')
    - unit_type: Type of unit (HO, CIRCLE, NETWORK, AO, RBO, BRANCH)
    - parent: Self-referencing ForeignKey for hierarchical structure
    - created_at: Timestamp when the unit was created
    - updated_at: Timestamp when the unit was last modified
    """
    UNIT_TYPES = [
        ('HO', 'Head Office'),
        ('CIRCLE', 'Circle'),
        ('NETWORK', 'Network'),
        ('AO', 'Administrative Office'),
        ('RBO', 'Regional Office'),
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
        """
        chain = [self]
        current = self
        while current.parent:
            chain.insert(0, current.parent)
            current = current.parent
        return chain
    
    def get_all_children(self):
        """
        Get all child units recursively (flattened list).
        """
        children = list(self.children.all())
        for child in self.children.all():
            children.extend(child.get_all_children())
        return children
    
    def get_root_unit(self):
        """
        Get the Head Office (HO) unit for this unit's hierarchy.
        """
        chain = self.get_parent_chain()
        return chain[0] if chain else self
    
    def is_descendant_of(self, unit):
        """
        Check if this unit is a descendant of the given unit.
        """
        parent_chain = self.get_parent_chain()
        return unit in parent_chain

