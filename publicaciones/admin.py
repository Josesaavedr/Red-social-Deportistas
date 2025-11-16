from django.contrib import admin
from .models import Publicacion, Like, Comentario, SesionEntrenamiento


@admin.register(Publicacion)
class PublicacionAdmin(admin.ModelAdmin):
    list_display = ['id', 'autor', 'tipo', 'contenido_preview', 'fecha_creacion', 'likes_count', 'comentarios_count']
    list_filter = ['fecha_creacion', 'autor', 'tipo']
    search_fields = ['contenido', 'autor__username']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion', 'likes_count', 'comentarios_count']
    date_hierarchy = 'fecha_creacion'
    
    def contenido_preview(self, obj):
        return obj.contenido[:50] + '...' if len(obj.contenido) > 50 else obj.contenido
    contenido_preview.short_description = 'Contenido'


@admin.register(SesionEntrenamiento)
class SesionEntrenamientoAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'deporte', 'estado', 'inicio', 'duracion_display']
    list_filter = ['deporte', 'estado', 'inicio']
    search_fields = ['usuario__username', 'notas']
    readonly_fields = ['inicio', 'duracion_display']
    
    def duracion_display(self, obj):
        if obj.estado == 'completado' and obj.fin:
            duracion = obj.duracion_total()
            horas = int(duracion.total_seconds() // 3600)
            minutos = int((duracion.total_seconds() % 3600) // 60)
            return f"{horas}h {minutos}m"
        return "En progreso"
    duracion_display.short_description = 'Duración'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'publicacion', 'fecha_creacion']
    list_filter = ['fecha_creacion']


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'publicacion', 'contenido_preview', 'fecha_creacion']
    list_filter = ['fecha_creacion']
    
    def contenido_preview(self, obj):
        return obj.contenido[:30] + '...' if len(obj.contenido) > 30 else obj.contenido
    contenido_preview.short_description = 'Contenido'

