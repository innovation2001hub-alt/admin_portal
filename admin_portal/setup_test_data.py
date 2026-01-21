"""
Setup script to create initial test data for the approval workflow system.
"""
import os
import django
from django.db import transaction

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_portal.settings')
django.setup()

from admin_core.models import User, Unit, Role

def create_test_data():
    """Create test data for the approval workflow."""
    
    print("🚀 Starting test data setup...\n")
    
    # Create Roles
    print("📝 Creating roles...")
    admin_role, _ = Role.objects.get_or_create(
        name='ADMIN',
        defaults={'description': 'Administrator role with full system access'}
    )
    maker_role, _ = Role.objects.get_or_create(
        name='MAKER',
        defaults={'description': 'Request maker - can create approval requests'}
    )
    checker_role, _ = Role.objects.get_or_create(
        name='CHECKER',
        defaults={'description': 'Checker/Approver - can approve or reject requests'}
    )
    print("✓ Roles created")
    
    # Create Unit Hierarchy
    print("\n📦 Creating organizational units...")
    
    # Head Office (Root)
    ho, _ = Unit.objects.get_or_create(
        code='HO',
        defaults={
            'name': 'Head Office (HO)',
            'unit_type': 'HO',
            'parent': None
        }
    )
    
    # Circle Units
    circle_north, _ = Unit.objects.get_or_create(
        code='CIRCLE_N',
        defaults={
            'name': 'Circle - North',
            'unit_type': 'CIRCLE',
            'parent': ho
        }
    )
    
    circle_south, _ = Unit.objects.get_or_create(
        code='CIRCLE_S',
        defaults={
            'name': 'Circle - South',
            'unit_type': 'CIRCLE',
            'parent': ho
        }
    )
    
    # Network/Regional Units
    region_ne, _ = Unit.objects.get_or_create(
        code='REGION_NE',
        defaults={
            'name': 'Network - Northeast',
            'unit_type': 'NETWORK',
            'parent': circle_north
        }
    )
    
    region_nw, _ = Unit.objects.get_or_create(
        code='REGION_NW',
        defaults={
            'name': 'Network - Northwest',
            'unit_type': 'NETWORK',
            'parent': circle_north
        }
    )
    
    # Branch Units
    branch_delhi, _ = Unit.objects.get_or_create(
        code='BRANCH_DL',
        defaults={
            'name': 'Branch - Delhi',
            'unit_type': 'BR',
            'parent': region_nw
        }
    )
    
    branch_mumbai, _ = Unit.objects.get_or_create(
        code='BRANCH_MM',
        defaults={
            'name': 'Branch - Mumbai',
            'unit_type': 'BR',
            'parent': circle_south
        }
    )
    
    print("✓ Units created: HO → Circles → Networks → Branches")
    
    # Create Users
    print("\n👥 Creating/checking test users...")
    
    with transaction.atomic():
        # Admin User (HO Level)
        admin_user, created = User.objects.get_or_create(
            employee_id='EMP001',
            defaults={
                'username': 'admin',
                'email': 'admin@sbi.com',
                'first_name': 'System',
                'last_name': 'Admin',
                'designation': 'System Administrator',
                'unit': ho,
                'is_active': True,
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
        admin_user.roles.add(admin_role)
        
        # Maker User 1 (Delhi Branch)
        maker1, created = User.objects.get_or_create(
            employee_id='EMP002',
            defaults={
                'username': 'maker_delhi_2',
                'email': 'maker.delhi2@sbi.com',
                'first_name': 'Rajesh',
                'last_name': 'Kumar',
                'designation': 'Branch Manager',
                'unit': branch_delhi,
                'is_active': True
            }
        )
        if created:
            maker1.set_password('maker123')
            maker1.save()
        maker1.roles.add(maker_role)
        
        # Maker User 2 (Mumbai Branch)
        maker2, created = User.objects.get_or_create(
            employee_id='EMP003',
            defaults={
                'username': 'maker_mumbai_2',
                'email': 'maker.mumbai2@sbi.com',
                'first_name': 'Priya',
                'last_name': 'Sharma',
                'designation': 'Deputy Manager',
                'unit': branch_mumbai,
                'is_active': True
            }
        )
        if created:
            maker2.set_password('maker123')
            maker2.save()
        maker2.roles.add(maker_role)
        
        # Checker User 1 (Northeast Network)
        checker1, created = User.objects.get_or_create(
            employee_id='EMP004',
            defaults={
                'username': 'checker_ne_2',
                'email': 'checker.ne2@sbi.com',
                'first_name': 'Amit',
                'last_name': 'Singh',
                'designation': 'Network Manager',
                'unit': region_ne,
                'is_active': True
            }
        )
        if created:
            checker1.set_password('checker123')
            checker1.save()
        checker1.roles.add(checker_role)
        
        # Checker User 2 (Northwest Network)
        checker2, created = User.objects.get_or_create(
            employee_id='EMP005',
            defaults={
                'username': 'checker_nw_2',
                'email': 'checker.nw2@sbi.com',
                'first_name': 'Vikram',
                'last_name': 'Patel',
                'designation': 'Network Manager',
                'unit': region_nw,
                'is_active': True
            }
        )
        if created:
            checker2.set_password('checker123')
            checker2.save()
        checker2.roles.add(checker_role)
        
        # Checker User 3 (Circle North)
        checker3, created = User.objects.get_or_create(
            employee_id='EMP006',
            defaults={
                'username': 'checker_circle_2',
                'email': 'checker.circle2@sbi.com',
                'first_name': 'Deepak',
                'last_name': 'Verma',
                'designation': 'Circle Manager',
                'unit': circle_north,
                'is_active': True
            }
        )
        if created:
            checker3.set_password('checker123')
            checker3.save()
        checker3.roles.add(checker_role)
    
    print("✓ Users created")
    
    # Print Summary
    print("\n" + "="*60)
    print("✅ TEST DATA SETUP COMPLETE!")
    print("="*60)
    
    print("\n📊 SUMMARY:")
    print(f"  Roles: {Role.objects.count()} created")
    print(f"  Units: {Unit.objects.count()} created")
    print(f"  Users: {User.objects.count()} created")
    
    print("\n🔐 TEST CREDENTIALS:")
    print("\n  ADMIN:")
    print("    Username: admin")
    print("    Password: admin123")
    print("    Role: Administrator")
    print("    Unit: Head Office (HO)")
    
    print("\n  MAKER 1:")
    print("    Username: maker_delhi")
    print("    Password: maker123")
    print("    Name: Rajesh Kumar")
    print("    Unit: Branch - Delhi (→ Region NW → Circle North → HO)")
    
    print("\n  MAKER 2:")
    print("    Username: maker_mumbai")
    print("    Password: maker123")
    print("    Name: Priya Sharma")
    print("    Unit: Branch - Mumbai (→ Circle South → HO)")
    
    print("\n  CHECKER 1:")
    print("    Username: checker_ne")
    print("    Password: checker123")
    print("    Name: Amit Singh")
    print("    Unit: Region - Northeast (→ Circle North → HO)")
    
    print("\n  CHECKER 2:")
    print("    Username: checker_nw")
    print("    Password: checker123")
    print("    Name: Vikram Patel")
    print("    Unit: Region - Northwest (→ Circle North → HO)")
    
    print("\n  CHECKER 3:")
    print("    Username: checker_circle")
    print("    Password: checker123")
    print("    Name: Deepak Verma")
    print("    Unit: Circle - North (→ HO)")
    
    print("\n📋 UNIT HIERARCHY:")
    print("""
    Head Office (HO)
    ├── Circle - North
    │   ├── Region - Northeast
    │   └── Region - Northwest
    │       └── Branch - Delhi
    └── Circle - South
        └── Branch - Mumbai
    """)
    
    print("\n🔄 APPROVAL ROUTING LOGIC:")
    print("  - Requests from Branch → auto-routed to Region → Circle → HO")
    print("  - Checkers in ancestor units can approve/reject requests")
    print("  - System enforces hierarchy-based access control")
    
    print("\n✨ Ready to test the approval workflow!\n")

if __name__ == '__main__':
    create_test_data()
