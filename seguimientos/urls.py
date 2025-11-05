from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SeguimientoViewSet

router = DefaultRouter()
router.register(r'seguimientos', SeguimientoViewSet, basename='seguimiento')

urlpatterns = [
    path('', include(router.urls)),
]

