from django.shortcuts import redirect
from django.urls import resolve

from .utils import get_primary_role_name, get_dashboard_url, ROLE_ADMIN, ROLE_MAKER, ROLE_CHECKER


class RoleBasedDashboardRedirectMiddleware:
    """
    If an authenticated user tries to access a dashboard URL that doesn't
    match their role, redirect them to their allowed dashboard.
    """

    DASHBOARD_NAME_BY_ROLE = {
        ROLE_ADMIN: "admin-dashboard",
        ROLE_MAKER: "maker-dashboard",
        ROLE_CHECKER: "checker-dashboard",
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only enforce for authenticated users and dashboard routes
        if request.user.is_authenticated:
            try:
                match = resolve(request.path_info)
                name = match.url_name
            except Exception:
                name = None

            if name in {"admin-dashboard", "maker-dashboard", "checker-dashboard"}:
                role = get_primary_role_name(request.user)
                allowed = self.DASHBOARD_NAME_BY_ROLE.get(role)
                if allowed and name != allowed:
                    return redirect(get_dashboard_url(request.user))
        return self.get_response(request)
