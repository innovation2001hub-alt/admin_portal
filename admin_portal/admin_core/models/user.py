from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model extending AbstractUser with additional fields for admin portal.
    
    Fields:
    - employee_id: Unique identifier for the employee
    - designation: Job title/designation of the user
    - unit: The organizational unit (Unit) the user belongs to
    - roles: Many-to-many relationship with roles for RBAC
    """
    employee_id = models.CharField(max_length=20, unique=True, help_text="Unique employee identifier")
    designation = models.CharField(max_length=100, help_text="Job title or designation")
    unit = models.ForeignKey(
        'Unit',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        help_text="Organizational unit the user belongs to"
    )
    roles = models.ManyToManyField(
        'Role',
        blank=True,
        related_name='users',
        help_text="Roles assigned to this user"
    )
    is_active = models.BooleanField(default=True, help_text="Whether this user account is active")
    
    class Meta:
        db_table = 'admin_core_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.employee_id})"
    
    def get_parent_units(self):
        """
        Get the hierarchical chain of parent units for this user's unit.
        Returns a list from the user's unit up to the root (HO).
        """
        if not self.unit:
            return []
        return self.unit.get_parent_chain()
