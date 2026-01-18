"""
Main URL configuration for myproject project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.views.generic import TemplateView
from django.views.static import serve
from pathlib import Path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('tlog.urls')),
    # Перенаправление favicon.ico на статический файл
    re_path(r'^favicon\.ico$', RedirectView.as_view(url='/static/favicon.svg', permanent=True)),
    # QTH карта - прямой доступ к файлу без /static/ в URL
    re_path(r'^qth-loc\.html$', serve, {'path': 'qth-loc.html', 'document_root': Path(__file__).resolve().parent.parent / 'tlog' / 'static'}),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)