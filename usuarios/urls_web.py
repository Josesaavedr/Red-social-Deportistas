from django.urls import path
from . import views_web

urlpatterns = [
    path('usuarios/registro/', views_web.registro_view, name='registro'),
    path('usuarios/login/', views_web.login_view, name='login'),
    path('usuarios/logout/', views_web.logout_view, name='logout'),
    path('perfil/', views_web.perfil_usuario, name='perfil_usuario'),
    path('perfil/editar/', views_web.editar_perfil, name='editar_perfil'),
    path('perfil/<str:username>/', views_web.perfil_usuario, name='perfil_usuario_detalle'),
]

