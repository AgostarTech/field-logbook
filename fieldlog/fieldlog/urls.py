from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from users.views import login_view  # Your custom login view

urlpatterns = [
    path('admin/', admin.site.urls),

    # Home, login, signup, dashboard, etc.
    path('', include(('users.urls', 'users'), namespace='users')),

    # Namespaced URLs for other apps
    path('logbook/', include(('logbook.urls', 'logbook'), namespace='logbook')),
    path('supervisors/', include(('supervisors.urls', 'supervisors'), namespace='supervisors')),
    path('notifications/', include(('notifications.urls', 'notifications'), namespace='notifications')),

    # Static pages
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('contact/', TemplateView.as_view(template_name='contact.html'), name='contact'),
    path('learn-more/', TemplateView.as_view(template_name='learn_more.html'), name='learn_more'),

    # Login route (custom login view)
    path('login/', login_view, name='login'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
