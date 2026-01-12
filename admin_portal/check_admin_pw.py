from django.contrib.auth import get_user_model, authenticate
User = get_user_model()
try:
    u = User.objects.get(username="admin")
    print("Found admin user", u.id)
    u.set_password("AdminPortal@123")
    u.save()
    user = authenticate(username="admin", password="AdminPortal@123")
    print("Authenticate result:", user is not None)
except User.DoesNotExist:
    print("Admin user does not exist")
