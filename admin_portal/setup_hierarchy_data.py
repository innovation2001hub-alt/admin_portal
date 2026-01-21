"""
Setup script for new hierarchy: Corporate Office → Local Head Office → Administrative Office → Regional Office → Branch
"""
import os
import django
from django.db import transaction

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_portal.settings')
django.setup()

from admin_core.models import User, Unit, Role

def create_hierarchy_data():
    """Create test data with new 5-level hierarchy."""
    
    print("🚀 Starting new hierarchy setup...\n")
    
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
    print("✓ Roles created\n")
    
    # Clear old data (but keep superuser)
    print("🗑️  Clearing old units and users...")
    User.objects.exclude(username='superadmin').delete()
    Unit.objects.all().delete()
    print("✓ Old data cleared\n")
    
    # Create Super Admin (if not exists)
    print("👑 Creating Super Admin user...")
    super_admin_role, _ = Role.objects.get_or_create(
        name='SUPER_ADMIN',
        defaults={'description': 'Super administrator - can manage all users and roles'}
    )
    
    super_admin_user, created = User.objects.get_or_create(
        username='superadmin',
        defaults={
            'email': 'superadmin@sbi.com',
            'first_name': 'Super',
            'last_name': 'Administrator',
            'employee_id': 'SA001',
            'is_staff': True,
            'is_superuser': True,
            'is_active': True,
        }
    )
    
    # Set password only if newly created
    if created:
        super_admin_user.set_password('superadmin123')
        super_admin_user.save()
    
    if not super_admin_user.roles.filter(name='SUPER_ADMIN').exists():
        super_admin_user.roles.add(super_admin_role)
    print(f"  ✓ Created: {super_admin_user.username}\n")
    
    # Create Unit Hierarchy (Top to Bottom)
    print("📦 Creating organizational hierarchy...")
    
    # Level 1: Corporate Office (Root)
    corporate = Unit.objects.create(
        code='CO',
        name='Corporate Office',
        unit_type='CO',
        parent=None
    )
    print(f"  ✓ Created: {corporate.name}")
    
    # Level 2: Local Head Offices
    lho_north = Unit.objects.create(
        code='LHO_NORTH',
        name='Local Head Office - North',
        unit_type='LHO',
        parent=corporate
    )
    print(f"  ✓ Created: {lho_north.name}")
    
    lho_south = Unit.objects.create(
        code='LHO_SOUTH',
        name='Local Head Office - South',
        unit_type='LHO',
        parent=corporate
    )
    print(f"  ✓ Created: {lho_south.name}")
    
    # Level 3: Administrative Offices
    ao_delhi = Unit.objects.create(
        code='AO_DELHI',
        name='Administrative Office - Delhi',
        unit_type='AO',
        parent=lho_north
    )
    print(f"  ✓ Created: {ao_delhi.name}")
    
    ao_mumbai = Unit.objects.create(
        code='AO_MUMBAI',
        name='Administrative Office - Mumbai',
        unit_type='AO',
        parent=lho_south
    )
    print(f"  ✓ Created: {ao_mumbai.name}")
    
    # Level 4: Regional Offices
    ro_north_delhi = Unit.objects.create(
        code='RO_NORTH_DELHI',
        name='Regional Office - North Delhi',
        unit_type='RO',
        parent=ao_delhi
    )
    print(f"  ✓ Created: {ro_north_delhi.name}")
    
    ro_south_mumbai = Unit.objects.create(
        code='RO_SOUTH_MUMBAI',
        name='Regional Office - South Mumbai',
        unit_type='RO',
        parent=ao_mumbai
    )
    print(f"  ✓ Created: {ro_south_mumbai.name}")
    
    # Level 5: Branches
    branch_karol_bagh = Unit.objects.create(
        code='BR_KAROL_BAGH',
        name='Branch - Karol Bagh',
        unit_type='BR',
        parent=ro_north_delhi
    )
    print(f"  ✓ Created: {branch_karol_bagh.name}")
    
    branch_rajouri = Unit.objects.create(
        code='BR_RAJOURI',
        name='Branch - Rajouri Garden',
        unit_type='BR',
        parent=ro_north_delhi
    )
    print(f"  ✓ Created: {branch_rajouri.name}")
    
    branch_andheri = Unit.objects.create(
        code='BR_ANDHERI',
        name='Branch - Andheri',
        unit_type='BR',
        parent=ro_south_mumbai
    )
    print(f"  ✓ Created: {branch_andheri.name}")
    
    branch_bandra = Unit.objects.create(
        code='BR_BANDRA',
        name='Branch - Bandra',
        unit_type='BR',
        parent=ro_south_mumbai
    )
    print(f"  ✓ Created: {branch_bandra.name}")
    
    print("✓ Unit hierarchy created\n")
    
    # Create Users with proper hierarchy
    print("👥 Creating users...")
    
    # Admin at Corporate Office
    admin_user = User.objects.create_user(
        username='admin',
        password='admin123',
        email='admin@sbi.com',
        first_name='System',
        last_name='Administrator',
        employee_id='EMP_ADMIN_CO',
        unit=corporate,
        is_staff=True,
        is_superuser=True
    )
    admin_user.roles.add(admin_role)
    print(f"  ✓ Created Admin: {admin_user.username} @ {admin_user.unit.name}")
    
    # Checker at LHO Level
    checker_lho_north = User.objects.create_user(
        username='checker_lho_north',
        password='checker123',
        email='checker.lho.north@sbi.com',
        first_name='Rajesh',
        last_name='Kumar',
        employee_id='EMP_LHO_N',
        unit=lho_north
    )
    checker_lho_north.roles.add(checker_role)
    print(f"  ✓ Created Checker: {checker_lho_north.username} @ {checker_lho_north.unit.name}")
    
    checker_lho_south = User.objects.create_user(
        username='checker_lho_south',
        password='checker123',
        email='checker.lho.south@sbi.com',
        first_name='Priya',
        last_name='Sharma',
        employee_id='EMP_LHO_S',
        unit=lho_south
    )
    checker_lho_south.roles.add(checker_role)
    print(f"  ✓ Created Checker: {checker_lho_south.username} @ {checker_lho_south.unit.name}")
    
    # Checker at AO Level
    checker_ao_delhi = User.objects.create_user(
        username='checker_ao_delhi',
        password='checker123',
        email='checker.ao.delhi@sbi.com',
        first_name='Amit',
        last_name='Singh',
        employee_id='EMP_AO_D',
        unit=ao_delhi
    )
    checker_ao_delhi.roles.add(checker_role)
    print(f"  ✓ Created Checker: {checker_ao_delhi.username} @ {checker_ao_delhi.unit.name}")
    
    checker_ao_mumbai = User.objects.create_user(
        username='checker_ao_mumbai',
        password='checker123',
        email='checker.ao.mumbai@sbi.com',
        first_name='Sunita',
        last_name='Patel',
        employee_id='EMP_AO_M',
        unit=ao_mumbai
    )
    checker_ao_mumbai.roles.add(checker_role)
    print(f"  ✓ Created Checker: {checker_ao_mumbai.username} @ {checker_ao_mumbai.unit.name}")
    
    # Checker at RO Level
    checker_ro_delhi = User.objects.create_user(
        username='checker_ro_delhi',
        password='checker123',
        email='checker.ro.delhi@sbi.com',
        first_name='Vikram',
        last_name='Mehta',
        employee_id='EMP_RO_ND',
        unit=ro_north_delhi
    )
    checker_ro_delhi.roles.add(checker_role)
    print(f"  ✓ Created Checker: {checker_ro_delhi.username} @ {checker_ro_delhi.unit.name}")
    
    checker_ro_mumbai = User.objects.create_user(
        username='checker_ro_mumbai',
        password='checker123',
        email='checker.ro.mumbai@sbi.com',
        first_name='Deepak',
        last_name='Verma',
        employee_id='EMP_RO_SM',
        unit=ro_south_mumbai
    )
    checker_ro_mumbai.roles.add(checker_role)
    print(f"  ✓ Created Checker: {checker_ro_mumbai.username} @ {checker_ro_mumbai.unit.name}")
    
    # Makers at Branch Level
    maker_karol_bagh = User.objects.create_user(
        username='maker_karol_bagh',
        password='maker123',
        email='maker.kb@sbi.com',
        first_name='Rahul',
        last_name='Gupta',
        employee_id='EMP_BR_KB',
        unit=branch_karol_bagh
    )
    maker_karol_bagh.roles.add(maker_role)
    print(f"  ✓ Created Maker: {maker_karol_bagh.username} @ {maker_karol_bagh.unit.name}")
    
    maker_rajouri = User.objects.create_user(
        username='maker_rajouri',
        password='maker123',
        email='maker.rj@sbi.com',
        first_name='Sanjay',
        last_name='Malhotra',
        employee_id='EMP_BR_RJ',
        unit=branch_rajouri
    )
    maker_rajouri.roles.add(maker_role)
    print(f"  ✓ Created Maker: {maker_rajouri.username} @ {maker_rajouri.unit.name}")
    
    maker_andheri = User.objects.create_user(
        username='maker_andheri',
        password='maker123',
        email='maker.andheri@sbi.com',
        first_name='Pooja',
        last_name='Desai',
        employee_id='EMP_BR_AN',
        unit=branch_andheri
    )
    maker_andheri.roles.add(maker_role)
    print(f"  ✓ Created Maker: {maker_andheri.username} @ {maker_andheri.unit.name}")
    
    maker_bandra = User.objects.create_user(
        username='maker_bandra',
        password='maker123',
        email='maker.bandra@sbi.com',
        first_name='Neha',
        last_name='Shah',
        employee_id='EMP_BR_BR',
        unit=branch_bandra
    )
    maker_bandra.roles.add(maker_role)
    print(f"  ✓ Created Maker: {maker_bandra.username} @ {maker_bandra.unit.name}")
    
    print("✓ Users created\n")
    
    # Display hierarchy
    print("=" * 70)
    print("📊 ORGANIZATIONAL HIERARCHY")
    print("=" * 70)
    print(f"""
{corporate.name} (CO)
├── {lho_north.name} (LHO) - Checker: checker_lho_north
│   └── {ao_delhi.name} (AO) - Checker: checker_ao_delhi
│       └── {ro_north_delhi.name} (RO) - Checker: checker_ro_delhi
│           ├── {branch_karol_bagh.name} (BR) - Maker: maker_karol_bagh
│           └── {branch_rajouri.name} (BR) - Maker: maker_rajouri
│
└── {lho_south.name} (LHO) - Checker: checker_lho_south
    └── {ao_mumbai.name} (AO) - Checker: checker_ao_mumbai
        └── {ro_south_mumbai.name} (RO) - Checker: checker_ro_mumbai
            ├── {branch_andheri.name} (BR) - Maker: maker_andheri
            └── {branch_bandra.name} (BR) - Maker: maker_bandra
    """)
    print("=" * 70)
    
    # Display approval routing
    print("\n📋 APPROVAL ROUTING RULES")
    print("=" * 70)
    print("""
HIERARCHY-BASED MAKER-CHECKER:
- Branch Makers → Regional Office Checker (immediate parent)
- Regional Office Checker can approve Branch requests

EXAMPLE FLOWS:
1. maker_karol_bagh (Branch) creates request
   → Routes to checker_ro_delhi (Regional Office - parent unit)
   
2. maker_andheri (Branch) creates request
   → Routes to checker_ro_mumbai (Regional Office - parent unit)
   
3. If no checker at parent level:
   → Routes to next ancestor level (AO, LHO, CO)
    """)
    print("=" * 70)
    
    # Display credentials
    print("\n🔐 LOGIN CREDENTIALS")
    print("=" * 70)
    print("""
ADMIN:
  Username: admin
  Password: admin123
  Unit: Corporate Office

👑 SUPER ADMIN (Can manage all users and roles):
  Username: superadmin
  Password: superadmin123
  Unit: N/A (global scope)
  Access: User Management Panel

CHECKERS (by level):
  LHO Level:
    - checker_lho_north / checker123 @ Local Head Office - North
    - checker_lho_south / checker123 @ Local Head Office - South
    
  AO Level:
    - checker_ao_delhi / checker123 @ Administrative Office - Delhi
    - checker_ao_mumbai / checker123 @ Administrative Office - Mumbai
    
  RO Level:
    - checker_ro_delhi / checker123 @ Regional Office - North Delhi
    - checker_ro_mumbai / checker123 @ Regional Office - South Mumbai

MAKERS (at Branches):
  - maker_karol_bagh / maker123 @ Branch - Karol Bagh
  - maker_rajouri / maker123 @ Branch - Rajouri Garden
  - maker_andheri / maker123 @ Branch - Andheri
  - maker_bandra / maker123 @ Branch - Bandra
    """)
    print("=" * 70)
    
    print("\n✅ HIERARCHY SETUP COMPLETE!")
    print("🚀 You can now start the servers and test the workflow.\n")

if __name__ == '__main__':
    create_hierarchy_data()
