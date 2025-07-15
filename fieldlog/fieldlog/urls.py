from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),  # Home, login, signup, dashboard
    path('logbook/', include('logbook.urls')),
    path('supervisors/', include('supervisors.urls')),
    path('notifications/', include('notifications.urls')),

    # Static Pages
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('contact/', TemplateView.as_view(template_name='contact.html'), name='contact'),
    path('learn-more/', TemplateView.as_view(template_name='learn_more.html'), name='learn_more'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
