from django.db import models


class Role(models.Model):
    """
    Role model for Role-Based Access Control (RBAC).
    
    Fields:
    - name: Unique name of the role (e.g., 'ADMIN', 'MAKER', 'CHECKER')
    - description: Detailed description of the role's responsibilities
    - created_at: Timestamp when the role was created
    - updated_at: Timestamp when the role was last modified
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique name of the role"
    )
    description = models.TextField(
        help_text="Detailed description of role responsibilities"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'admin_core_role'
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
        ordering = ['name']
    
    def __str__(self):
        return self.name

