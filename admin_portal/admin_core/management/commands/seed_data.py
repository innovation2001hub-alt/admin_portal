"""
Django management command to seed initial data for the admin portal.

Usage: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from admin_core.models import Unit, Role, User


class Command(BaseCommand):
    help = 'Seed initial data for admin portal (units, roles, etc.)'

    def handle(self, *args, **options):
        """Execute the command."""
        self.stdout.write(self.style.SUCCESS('Starting data seeding...'))
        
        # Create roles
        self.create_roles()
        
        # Create organizational hierarchy
        self.create_hierarchy()
        
        # Create sample users
        self.create_sample_users()
        
        self.stdout.write(self.style.SUCCESS('Data seeding completed successfully!'))
    
    def create_roles(self):
        """Create default roles."""
        roles = [
            {
                'name': 'ADMIN',
                'description': 'Administrator with full system access',
            },
            {
                'name': 'MANAGER',
                'description': 'Manager who can approve requests and manage subordinate units',
            },
            {
                'name': 'MAKER',
                'description': 'User who can create and submit requests for approval',
            },
            {
                'name': 'CHECKER',
                'description': 'User who reviews and approves/rejects requests',
            },
            {
                'name': 'VIEWER',
                'description': 'User with read-only access to reports and data',
            },
        ]
        
        for role_data in roles:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults={'description': role_data['description']}
            )
            status = 'Created' if created else 'Already exists'
            self.stdout.write(f'  {status}: Role "{role.name}"')
    
    def create_hierarchy(self):
        """Create organizational hierarchy."""
        # Head Office
        ho, created = Unit.objects.get_or_create(
            code='HO001',
            defaults={
                'name': 'Head Office',
                'unit_type': 'HO',
                'parent': None,
            }
        )
        self.stdout.write(f'  {"Created" if created else "Already exists"}: Unit "HO001 - Head Office"')
        
        # Circles
        circle_codes = [('CIRCLE001', 'Circle - Region 1'), ('CIRCLE002', 'Circle - Region 2')]
        circles = []
        for code, name in circle_codes:
            circle, created = Unit.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'unit_type': 'CIRCLE',
                    'parent': ho,
                }
            )
            circles.append(circle)
            self.stdout.write(f'  {"Created" if created else "Already exists"}: Unit "{code} - {name}"')
        
        # Networks
        for circle in circles:
            for i in range(1, 3):
                net_code = f'NET{circle.code[6:]}{i:03d}'
                net_name = f'Network {i} - {circle.name}'
                network, created = Unit.objects.get_or_create(
                    code=net_code,
                    defaults={
                        'name': net_name,
                        'unit_type': 'NETWORK',
                        'parent': circle,
                    }
                )
                self.stdout.write(f'  {"Created" if created else "Already exists"}: Unit "{net_code}"')
        
        # Administrative Offices
        for circle in circles:
            ao_code = f'AO{circle.code[6:]}'
            ao_name = f'Administrative Office - {circle.name}'
            ao, created = Unit.objects.get_or_create(
                code=ao_code,
                defaults={
                    'name': ao_name,
                    'unit_type': 'AO',
                    'parent': circle,
                }
            )
            self.stdout.write(f'  {"Created" if created else "Already exists"}: Unit "{ao_code}"')
    
    def create_sample_users(self):
        """Create sample users with different roles."""
        ho = Unit.objects.get(code='HO001')
        
        # Get roles
        admin_role = Role.objects.get(name='ADMIN')
        manager_role = Role.objects.get(name='MANAGER')
        maker_role = Role.objects.get(name='MAKER')
        
        users = [
            {
                'username': 'admin',
                'email': 'admin@adminportal.com',
                'first_name': 'System',
                'last_name': 'Administrator',
                'employee_id': 'EMP001',
                'designation': 'System Administrator',
                'unit': ho,
                'password': 'AdminPortal@123',
                'roles': [admin_role],
                'is_superuser': True,
                'is_staff': True,
            },
            {
                'username': 'manager1',
                'email': 'manager1@adminportal.com',
                'first_name': 'John',
                'last_name': 'Manager',
                'employee_id': 'EMP002',
                'designation': 'Unit Manager',
                'unit': ho,
                'password': 'Manager@123',
                'roles': [manager_role],
                'is_superuser': False,
                'is_staff': True,
            },
            {
                'username': 'maker1',
                'email': 'maker1@adminportal.com',
                'first_name': 'Jane',
                'last_name': 'Maker',
                'employee_id': 'EMP003',
                'designation': 'Request Maker',
                'unit': ho,
                'password': 'Maker@123',
                'roles': [maker_role],
                'is_superuser': False,
                'is_staff': False,
            },
        ]
        
        for user_data in users:
            roles = user_data.pop('roles')
            password = user_data.pop('password')
            
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults=user_data
            )
            
            if created:
                user.set_password(password)
                user.save()
                user.roles.set(roles)
                self.stdout.write(f'  Created: User "{user.username}" with roles {[r.name for r in roles]}')
            else:
                self.stdout.write(f'  Already exists: User "{user.username}"')
