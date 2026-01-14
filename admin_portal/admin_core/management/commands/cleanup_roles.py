"""
Management command to remove non-standard roles (MANAGER, VIEWER, etc.) from the system.
"""
from django.core.management.base import BaseCommand
from admin_core.models import Role, User
from admin_core.utils import ROLE_ADMIN, ROLE_MAKER, ROLE_CHECKER


class Command(BaseCommand):
    help = 'Remove non-standard roles (MANAGER, VIEWER) and clean up user role assignments'

    def handle(self, *args, **options):
        allowed_roles = [ROLE_ADMIN, ROLE_MAKER, ROLE_CHECKER]
        
        # Find non-standard roles
        non_standard_roles = Role.objects.exclude(name__in=allowed_roles)
        
        if not non_standard_roles.exists():
            self.stdout.write(self.style.SUCCESS('No non-standard roles found. System is clean.'))
            return
        
        self.stdout.write(f'Found {non_standard_roles.count()} non-standard role(s):')
        for role in non_standard_roles:
            user_count = role.users.count()
            self.stdout.write(f'  - {role.name} (assigned to {user_count} user(s))')
        
        # Remove non-standard roles from users
        for role in non_standard_roles:
            users_with_role = role.users.all()
            if users_with_role.exists():
                self.stdout.write(f'Removing {role.name} from {users_with_role.count()} user(s)...')
                for user in users_with_role:
                    user.roles.remove(role)
                    self.stdout.write(f'  - Removed from {user.username}')
        
        # Delete non-standard roles
        role_names = [role.name for role in non_standard_roles]
        deleted_count, _ = non_standard_roles.delete()
        
        self.stdout.write(self.style.SUCCESS(
            f'Successfully removed {deleted_count} non-standard role(s): {", ".join(role_names)}'
        ))
        self.stdout.write(self.style.SUCCESS('Only ADMIN, MAKER, and CHECKER roles remain in the system.'))
