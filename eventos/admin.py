from django.contrib import admin
from .models import EventoDeportivo, ParticipanteEvento


@admin.register(EventoDeportivo)
class EventoDeportivoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'organizador', 'tipo', 'fecha_inicio', 'ubicacion', 'participantes_count']
    list_filter = ['tipo', 'fecha_inicio', 'es_publico']
    search_fields = ['titulo', 'descripcion', 'organizador__username', 'ubicacion']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion', 'participantes_count']
    date_hierarchy = 'fecha_inicio'


@admin.register(ParticipanteEvento)
class ParticipanteEventoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'evento', 'fecha_registro', 'confirmado']
    list_filter = ['fecha_registro', 'confirmado']
    search_fields = ['usuario__username', 'evento__titulo']

