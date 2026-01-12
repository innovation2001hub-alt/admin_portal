import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_portal.settings')
import django
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
try:
    u = User.objects.get(username='admin')
    u.set_password('AdminPortal@123')
    u.save()
    print('Admin password updated to AdminPortal@123')
except User.DoesNotExist:
    print('Admin user does not exist')
