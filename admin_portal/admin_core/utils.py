from typing import Optional
from django.urls import reverse


ROLE_ADMIN = "ADMIN"
ROLE_MAKER = "MAKER"
ROLE_CHECKER = "CHECKER"


def get_primary_role_name(user) -> Optional[str]:
    """
    Returns the primary role name for a user.
    Only returns standard roles (ADMIN, MAKER, CHECKER).
    If multiple exist, returns the first by name.
    """
    if not user or not user.is_authenticated:
        return None
    # User model uses M2M `roles` - filter to only standard roles
    allowed_roles = [ROLE_ADMIN, ROLE_MAKER, ROLE_CHECKER]
    role = user.roles.filter(name__in=allowed_roles).order_by("name").first()
    return role.name if role else None


def get_dashboard_url(user) -> str:
    """Return dashboard URL path based on the user's role.

    Defaults to login page if role is missing.
    """
    role = get_primary_role_name(user)
    if role == ROLE_ADMIN:
        return reverse("admin-dashboard")
    if role == ROLE_MAKER:
        return reverse("maker-dashboard")
    if role == ROLE_CHECKER:
        return reverse("checker-dashboard")
    return reverse("login")
