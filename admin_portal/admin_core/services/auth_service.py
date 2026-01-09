"""
Authentication Service.

Handles user authentication, token generation, and auth-related operations.
"""
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from admin_core.models import User, AuditLog


class AuthService:
    """
    Service class for handling authentication operations.
    
    Methods:
    - authenticate_user: Authenticate user with username/password
    - generate_token: Generate or retrieve authentication token
    - logout_user: Invalidate user token
    """
    
    @staticmethod
    def authenticate_user(username, password, ip_address=None):
        """
        Authenticate user with username and password.
        
        Args:
            username: User's username
            password: User's password
            ip_address: Optional IP address for audit logging
        
        Returns:
            User object if authentication succeeds
        
        Raises:
            AuthenticationFailed: If credentials are invalid
        """
        user = authenticate(username=username, password=password)
        
        if not user:
            raise AuthenticationFailed('Invalid username or password.')
        
        if not user.is_active:
            raise AuthenticationFailed('This user account is inactive.')
        
        # Log the login action
        AuditLog.log_action(
            user=user,
            action=f'User logged in',
            action_type='LOGIN',
            metadata={'username': username},
            ip_address=ip_address
        )
        
        # Update last login
        update_last_login(None, user)
        
        return user
    
    @staticmethod
    def generate_token(user):
        """
        Generate or retrieve authentication token for user.
        
        Args:
            user: User object
        
        Returns:
            Token object
        """
        token, created = Token.objects.get_or_create(user=user)
        return token
    
    @staticmethod
    def logout_user(user, ip_address=None):
        """
        Logout user by deleting their token.
        
        Args:
            user: User object to logout
            ip_address: Optional IP address for audit logging
        
        Returns:
            True if logout was successful
        """
        # Log the logout action
        AuditLog.log_action(
            user=user,
            action='User logged out',
            action_type='LOGOUT',
            ip_address=ip_address
        )
        
        # Delete the token
        Token.objects.filter(user=user).delete()
        return True
    
    @staticmethod
    def change_password(user, old_password, new_password):
        """
        Change user password with validation.
        
        Args:
            user: User object
            old_password: Current password
            new_password: New password to set
        
        Returns:
            User object
        
        Raises:
            ValidationError: If old password is incorrect
        """
        if not user.check_password(old_password):
            raise ValidationError({'old_password': 'Incorrect password.'})
        
        user.set_password(new_password)
        user.save()
        
        # Log the password change
        AuditLog.log_action(
            user=user,
            action='User changed password',
            action_type='UPDATE',
            metadata={'target': 'password'}
        )
        
        return user
