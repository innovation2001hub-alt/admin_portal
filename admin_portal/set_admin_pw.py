from django.contrib.auth import get_user_model
User = get_user_model()
try:
    u = User.objects.get(username="admin")
    u.set_password("AdminPortal@123")
    u.save()
    print("Admin password set to AdminPortal@123")
except User.DoesNotExist:
    print("Admin user does not exist")
