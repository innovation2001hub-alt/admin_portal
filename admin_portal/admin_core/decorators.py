from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied

from .utils import get_dashboard_url


def role_required(role_name: str):
    """Decorator to restrict access to users having the given role name."""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return redirect("login")

            has_role = user.roles.filter(name=role_name).exists()
            if not has_role:
                # Friendly redirect to allowed dashboard rather than 403
                messages.warning(request, "You don't have access to that page.")
                return redirect(get_dashboard_url(user))
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator


class RoleRequiredMixin:
    """CBV mixin to enforce role-based access control.

    Set `allowed_roles = ["ADMIN"]` in your view.
    """
    allowed_roles = None

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return redirect("login")

        roles = set(self.allowed_roles or [])
        is_allowed = user.roles.filter(name__in=list(roles)).exists()
        if not is_allowed:
            messages.warning(request, "You don't have access to that page.")
            return redirect(get_dashboard_url(user))
        return super().dispatch(request, *args, **kwargs)
