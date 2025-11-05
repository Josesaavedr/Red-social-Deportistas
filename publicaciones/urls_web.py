from django.urls import path
from django.views.generic import TemplateView
from . import views as publicaciones_views

urlpatterns = [
    path('', TemplateView.as_view(template_name='publicaciones/feed.html'), name='home'),
]

