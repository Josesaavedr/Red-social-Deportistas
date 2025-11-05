from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UsuarioViewSet, PerfilDeportistaViewSet

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'perfiles', PerfilDeportistaViewSet, basename='perfil')

urlpatterns = [
    path('', include(router.urls)),
]

