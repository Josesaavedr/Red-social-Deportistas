from rest_framework import serializers
from .models import Seguimiento
from usuarios.serializers import UsuarioSerializer


class SeguimientoSerializer(serializers.ModelSerializer):
    seguidor = UsuarioSerializer(read_only=True)
    seguido = UsuarioSerializer(read_only=True)
    
    class Meta:
        model = Seguimiento
        fields = ['id', 'seguidor', 'seguido', 'fecha_creacion']
        read_only_fields = ['id', 'fecha_creacion']

