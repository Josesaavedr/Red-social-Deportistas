from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventoDeportivoViewSet

router = DefaultRouter()
router.register(r'eventos', EventoDeportivoViewSet, basename='evento')

urlpatterns = [
    path('', include(router.urls)),
]

