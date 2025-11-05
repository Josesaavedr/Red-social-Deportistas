from rest_framework import serializers
from .models import Publicacion, Like, Comentario
from usuarios.serializers import UsuarioSerializer


class ComentarioSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)
    
    class Meta:
        model = Comentario
        fields = ['id', 'usuario', 'contenido', 'fecha_creacion', 'fecha_actualizacion']
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']


class PublicacionSerializer(serializers.ModelSerializer):
    autor = UsuarioSerializer(read_only=True)
    comentarios = ComentarioSerializer(many=True, read_only=True)
    usuario_dio_like = serializers.SerializerMethodField()
    
    class Meta:
        model = Publicacion
        fields = [
            'id', 'autor', 'contenido', 'imagen', 'fecha_creacion',
            'fecha_actualizacion', 'likes_count', 'comentarios_count',
            'comentarios', 'usuario_dio_like'
        ]
        read_only_fields = ['id', 'autor', 'fecha_creacion', 'fecha_actualizacion', 'likes_count', 'comentarios_count']
    
    def get_usuario_dio_like(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(usuario=request.user).exists()
        return False


class LikeSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)
    
    class Meta:
        model = Like
        fields = ['id', 'usuario', 'fecha_creacion']
        read_only_fields = ['id', 'fecha_creacion']

