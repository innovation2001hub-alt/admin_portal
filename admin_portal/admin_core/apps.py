from django.apps import AppConfig


class AdminCoreConfig(AppConfig):
    name = 'admin_core'
    
    def ready(self):
        """Customize admin site on app ready."""
        from django.contrib import admin
        from django.utils.html import format_html
        from django.db.models.signals import post_migrate
        from django.dispatch import receiver
        
        # Customize admin site
        admin.site.site_header = "Admin Portal"
        admin.site.site_title = "Admin Portal"
        admin.site.index_title = "Welcome to Admin Portal"

        # Register signal to seed roles after migrations
        @receiver(post_migrate)
        def seed_fixed_roles(sender, **kwargs):
            """Ensure fixed roles exist after migrations."""
            if sender.name == 'admin_core':
                from .models import Role
                from .utils import ROLE_ADMIN, ROLE_MAKER, ROLE_CHECKER
                
                Role.objects.get_or_create(name=ROLE_ADMIN, defaults={'description': 'Administrator role with full access'})
                Role.objects.get_or_create(name=ROLE_MAKER, defaults={'description': 'Maker role for creating requests'})
                Role.objects.get_or_create(name=ROLE_CHECKER, defaults={'description': 'Checker role for approving requests'})
        
        # Add custom CSS for dashboard badges
        original_index = admin.site.index
        
        def index_with_dashboard_links(request):
            """Add dashboard quick links to admin index."""
            response = original_index(request)
            if request.user.is_superuser or request.user.is_staff:
                # Add dashboard navigation in the context
                from .utils import get_primary_role_name, ROLE_ADMIN, ROLE_MAKER, ROLE_CHECKER
                role = get_primary_role_name(request.user)
                if role and request.user.is_active:
                    dashboard_urls = {
                        ROLE_ADMIN: '/admin/dashboard/',
                        ROLE_MAKER: '/maker/dashboard/',
                        ROLE_CHECKER: '/checker/dashboard/',
                    }
                    response.context_data['dashboard_url'] = dashboard_urls.get(role)
            return response
        
        admin.site.index = index_with_dashboard_links

