"""
URL Configuration for admin_core application.

Includes all API endpoints for the admin portal.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.auth_views import LoginView, LogoutView, ChangePasswordView, CurrentUserView
from .views.unit_views import UnitViewSet
from .views.user_views import UserViewSet
from .views.approval_views import ApprovalRequestViewSet
from .views.user_management_views import UserManagementViewSet


# Create router and register viewsets
router = DefaultRouter()
router.register(r'units', UnitViewSet, basename='unit')
router.register(r'users', UserViewSet, basename='user')
router.register(r'approvals', ApprovalRequestViewSet, basename='approval')
router.register(r'user-management', UserManagementViewSet, basename='user-management')

# Authentication endpoints
auth_urlpatterns = [
    path('login/', LoginView.as_view({'post': 'create'}), name='auth-login'),
    path('logout/', LogoutView.as_view({'post': 'create'}), name='auth-logout'),
    path('change-password/', ChangePasswordView.as_view({'post': 'create'}), name='auth-change-password'),
    path('current-user/', CurrentUserView.as_view({'get': 'list'}), name='auth-current-user'),
]

# App name for URL reversing
app_name = 'admin_core'

# URL patterns
urlpatterns = [
    path('auth/', include(auth_urlpatterns)),
    path('', include(router.urls)),
]
