from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import TemplateView

from admin_core.decorators import RoleRequiredMixin
from admin_core.utils import get_primary_role_name, get_dashboard_url, ROLE_ADMIN, ROLE_MAKER, ROLE_CHECKER
from admin_core.models.user import User


def login_view(request):
    """Custom login using username or employee_id, then redirect by role.

    POST fields: identifier (username or employee_id), password
    """
    if request.method == "POST":
        identifier = request.POST.get("identifier")
        password = request.POST.get("password")

        if not identifier or not password:
            messages.error(request, "Please provide both identifier and password.")
            return render(request, "login.html")

        # Try direct username login first
        user = authenticate(request, username=identifier, password=password)

        # If that fails, try resolving by employee_id
        if user is None:
            try:
                matched = User.objects.get(employee_id=identifier)
                user = authenticate(request, username=matched.username, password=password)
            except User.DoesNotExist:
                user = None

        if user is None:
            messages.error(request, "Invalid credentials.")
            return render(request, "login.html")

        # Ensure user has a role
        role = get_primary_role_name(user)
        if not role:
            messages.error(request, "Your account has no role assigned. Contact admin.")
            return render(request, "login.html")

        login(request, user)
        return redirect(get_dashboard_url(user))

    # GET: render login page
    return render(request, "login.html")


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")


class AdminDashboardView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    template_name = "admin/dashboard.html"
    allowed_roles = [ROLE_ADMIN]


class MakerDashboardView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    template_name = "maker/dashboard.html"
    allowed_roles = [ROLE_MAKER]


class CheckerDashboardView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    template_name = "checker/dashboard.html"
    allowed_roles = [ROLE_CHECKER]
