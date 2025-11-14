from django.urls import path
from . import views_web

urlpatterns = [
    path('eventos/', views_web.lista_eventos, name='lista_eventos'),
    path('eventos/<int:pk>/', views_web.detalle_evento, name='detalle_evento'),
    path('eventos/crear/', views_web.crear_evento, name='crear_evento'),
    path('eventos/<int:pk>/participar/', views_web.participar_evento, name='participar_evento'),
    path('eventos/<int:pk>/dejar-participar/', views_web.dejar_participar_evento, name='dejar_participar_evento'),
]

