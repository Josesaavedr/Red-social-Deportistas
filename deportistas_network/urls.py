"""
URL configuration for deportistas_network project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # API URLs
    path('api/', include('usuarios.urls')),
    path('api/', include('publicaciones.urls')),
    path('api/', include('eventos.urls')),
    path('api/', include('seguimientos.urls')),
    # Web URLs
    path('', include('usuarios.urls_web')),
    path('', include('publicaciones.urls_web')),
    path('', include('eventos.urls_web')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

