"""
URL configuration for myproject project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from tlog.views.main import custom_404_view

handler404 = custom_404_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('favicon.svg', RedirectView.as_view(url='/static/favicon.svg', permanent=True)),
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.svg', permanent=True)),
    path('', include('tlog.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)