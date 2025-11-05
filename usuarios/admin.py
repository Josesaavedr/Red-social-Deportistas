from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario, PerfilDeportista


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'es_verificado', 'fecha_registro']
    list_filter = ['es_verificado', 'fecha_registro']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    date_hierarchy = 'fecha_registro'


@admin.register(PerfilDeportista)
class PerfilDeportistaAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'deporte_principal', 'nivel', 'ubicacion']
    list_filter = ['deporte_principal', 'nivel']
    search_fields = ['usuario__username', 'usuario__email', 'ubicacion']
    readonly_fields = ['fecha_actualizacion']

