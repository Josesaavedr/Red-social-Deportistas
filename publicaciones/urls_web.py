from django.urls import path
from . import views_web

urlpatterns = [
    path('', views_web.lista_publicaciones, name='home'),  # La página de inicio es la lista de publicaciones
    path('publicaciones/', views_web.lista_publicaciones, name='lista_publicaciones'), # Se mantiene por si se usa en otro lugar
    path('publicaciones/<int:pk>/', views_web.detalle_publicacion, name='detalle_publicacion'),
    path('publicaciones/crear/', views_web.crear_publicacion, name='crear_publicacion'),
    path('publicaciones/<int:pk>/like/', views_web.toggle_like, name='toggle_like'),
    path('publicaciones/<int:pk>/comentar/', views_web.crear_comentario, name='crear_comentario'),
    path('publicaciones/<int:pk>/eliminar/', views_web.eliminar_publicacion, name='eliminar_publicacion'),
    path('entrenamientos/iniciar/', views_web.iniciar_entrenamiento, name='iniciar_entrenamiento'),
    path('entrenamientos/controlar/', views_web.controlar_entrenamiento, name='controlar_entrenamiento'),
    path('entrenamientos/tiempo/', views_web.obtener_tiempo_entrenamiento, name='tiempo_entrenamiento'),
]
