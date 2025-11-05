from rest_framework import serializers
from .models import EventoDeportivo, ParticipanteEvento
from usuarios.serializers import UsuarioSerializer


class ParticipanteEventoSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)
    
    class Meta:
        model = ParticipanteEvento
        fields = ['id', 'usuario', 'fecha_registro', 'confirmado']
        read_only_fields = ['id', 'fecha_registro']


class EventoDeportivoSerializer(serializers.ModelSerializer):
    organizador = UsuarioSerializer(read_only=True)
    participantes = ParticipanteEventoSerializer(many=True, read_only=True)
    usuario_participa = serializers.SerializerMethodField()
    
    class Meta:
        model = EventoDeportivo
        fields = [
            'id', 'organizador', 'titulo', 'descripcion', 'tipo',
            'fecha_inicio', 'fecha_fin', 'ubicacion', 'imagen',
            'capacidad_maxima', 'participantes_count', 'es_publico',
            'fecha_creacion', 'fecha_actualizacion', 'participantes',
            'usuario_participa'
        ]
        read_only_fields = [
            'id', 'organizador', 'participantes_count',
            'fecha_creacion', 'fecha_actualizacion'
        ]
    
    def get_usuario_participa(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.participantes.filter(usuario=request.user).exists()
        return False
    
    def validate(self, data):
        """Validar que fecha_fin sea posterior a fecha_inicio"""
        if 'fecha_inicio' in data and 'fecha_fin' in data:
            if data['fecha_fin'] <= data['fecha_inicio']:
                raise serializers.ValidationError({
                    'fecha_fin': 'La fecha de fin debe ser posterior a la fecha de inicio.'
                })
        return data

