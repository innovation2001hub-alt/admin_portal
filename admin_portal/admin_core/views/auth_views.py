"""
Authentication Views.

Implements authentication endpoints:
- Login
- Logout
- Change Password
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.viewsets import ViewSet
from rest_framework.authentication import TokenAuthentication

from admin_core.serializers import UserSerializer
from admin_core.services.auth_service import AuthService


class LoginView(ViewSet):
    """
    API endpoint for user login.
    
    POST /api/auth/login/
    - username: str
    - password: str
    
    Returns:
    - token: Authentication token
    - user: User details
    """
    permission_classes = [AllowAny]
    # Disable authentication on login to avoid CSRF checks from SessionAuthentication
    authentication_classes = []
    
    def create(self, request):
        """Handle login request."""
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response(
                {'error': 'Username and password are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get client IP
            ip_address = self._get_client_ip(request)
            
            # Authenticate user
            user = AuthService.authenticate_user(username, password, ip_address)
            
            # Generate token
            token = AuthService.generate_token(user)
            
            # Serialize user
            serializer = UserSerializer(user)
            
            return Response({
                'token': token.key,
                'user': serializer.data,
                'message': 'Login successful.'
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )
    
    @staticmethod
    def _get_client_ip(request):
        """Extract client IP from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class LogoutView(ViewSet):
    """
    API endpoint for user logout.
    
    POST /api/auth/logout/
    
    Returns:
    - message: Success message
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    def create(self, request):
        """Handle logout request."""
        try:
            ip_address = self._get_client_ip(request)
            AuthService.logout_user(request.user, ip_address)
            
            return Response(
                {'message': 'Logout successful.'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @staticmethod
    def _get_client_ip(request):
        """Extract client IP from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class ChangePasswordView(ViewSet):
    """
    API endpoint for changing user password.
    
    POST /api/auth/change-password/
    - old_password: str
    - new_password: str
    - new_password_confirm: str
    
    Returns:
    - message: Success message
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    def create(self, request):
        """Handle change password request."""
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        new_password_confirm = request.data.get('new_password_confirm')
        
        # Validation
        if not all([old_password, new_password, new_password_confirm]):
            return Response(
                {'error': 'All password fields are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if new_password != new_password_confirm:
            return Response(
                {'error': 'New passwords do not match.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            AuthService.change_password(request.user, old_password, new_password)
            
            return Response(
                {'message': 'Password changed successfully.'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class CurrentUserView(ViewSet):
    """
    API endpoint for getting current authenticated user.
    
    GET /api/auth/current-user/
    
    Returns:
    - Current user details
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    def list(self, request):
        """Get current user details."""
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
