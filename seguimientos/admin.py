from django.contrib import admin
from .models import Seguimiento


@admin.register(Seguimiento)
class SeguimientoAdmin(admin.ModelAdmin):
    list_display = ['seguidor', 'seguido', 'fecha_creacion']
    list_filter = ['fecha_creacion']
    search_fields = ['seguidor__username', 'seguido__username']
    date_hierarchy = 'fecha_creacion'

