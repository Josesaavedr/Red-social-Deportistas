from django.contrib import admin
from .models import Publicacion, Like, Comentario


@admin.register(Publicacion)
class PublicacionAdmin(admin.ModelAdmin):
    list_display = ['id', 'autor', 'contenido_preview', 'fecha_creacion', 'likes_count', 'comentarios_count']
    list_filter = ['fecha_creacion', 'autor']
    search_fields = ['contenido', 'autor__username']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion', 'likes_count', 'comentarios_count']
    date_hierarchy = 'fecha_creacion'
    
    def contenido_preview(self, obj):
        return obj.contenido[:50] + '...' if len(obj.contenido) > 50 else obj.contenido
    contenido_preview.short_description = 'Contenido'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'publicacion', 'fecha_creacion']
    list_filter = ['fecha_creacion']
    search_fields = ['usuario__username', 'publicacion__id']


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'publicacion', 'contenido_preview', 'fecha_creacion']
    list_filter = ['fecha_creacion']
    search_fields = ['contenido', 'usuario__username']
    
    def contenido_preview(self, obj):
        return obj.contenido[:50] + '...' if len(obj.contenido) > 50 else obj.contenido
    contenido_preview.short_description = 'Contenido'

