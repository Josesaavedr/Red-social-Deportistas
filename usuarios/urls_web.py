from django.urls import path
from django.contrib.auth import views as auth_views
from . import views_web

urlpatterns = [
    path('usuarios/registro/', views_web.registro_view, name='registro'),
    path('usuarios/login/', views_web.login_view, name='login'),
    path('usuarios/logout/', auth_views.LogoutView.as_view(), name='logout'),
]

