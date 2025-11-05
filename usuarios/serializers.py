from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import Usuario, PerfilDeportista


class PerfilDeportistaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfilDeportista
        fields = [
            'deporte_principal', 'deportes_secundarios', 'nivel',
            'biografia', 'foto_perfil', 'foto_portada', 'ubicacion',
            'sitio_web', 'instagram', 'twitter'
        ]
        read_only_fields = ['fecha_actualizacion']


class UsuarioSerializer(serializers.ModelSerializer):
    perfil = PerfilDeportistaSerializer(read_only=True)
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'telefono', 'fecha_nacimiento', 'es_verificado',
            'fecha_registro', 'perfil', 'password'
        ]
        read_only_fields = ['id', 'es_verificado', 'fecha_registro']
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        usuario = Usuario.objects.create(**validated_data)
        if password:
            usuario.set_password(password)
            usuario.save()
        return usuario


class RegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        usuario = Usuario.objects.create(**validated_data)
        usuario.set_password(password)
        usuario.save()
        # Crear perfil por defecto
        PerfilDeportista.objects.create(usuario=usuario)
        return usuario

