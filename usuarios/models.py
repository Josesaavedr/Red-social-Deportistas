from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class Usuario(AbstractUser):
    """Modelo de usuario personalizado para deportistas"""
    email = models.EmailField(unique=True)
    telefono = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="El número de teléfono debe estar en formato: '+999999999'. Hasta 15 dígitos permitidos."
        )]
    )
    fecha_nacimiento = models.DateField(null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    es_verificado = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-fecha_registro']
    
    def __str__(self):
        return self.username


class PerfilDeportista(models.Model):
    """Perfil deportivo del usuario"""
    DEPORTES_CHOICES = [
        ('futbol', 'Fútbol'),
        ('baloncesto', 'Baloncesto'),
        ('tenis', 'Tenis'),
        ('natacion', 'Natación'),
        ('ciclismo', 'Ciclismo'),
        ('atletismo', 'Atletismo'),
        ('boxeo', 'Boxeo'),
        ('voleibol', 'Voleibol'),
        ('otro', 'Otro'),
    ]
    
    NIVEL_CHOICES = [
        ('principiante', 'Principiante'),
        ('intermedio', 'Intermedio'),
        ('avanzado', 'Avanzado'),
        ('profesional', 'Profesional'),
    ]
    
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil')
    deporte_principal = models.CharField(max_length=50, choices=DEPORTES_CHOICES, default='otro')
    deportes_secundarios = models.CharField(max_length=200, blank=True, help_text="Separados por comas")
    nivel = models.CharField(max_length=20, choices=NIVEL_CHOICES, default='intermedio')
    biografia = models.TextField(blank=True, max_length=500)
    foto_perfil = models.ImageField(upload_to='perfiles/', blank=True, null=True)
    foto_portada = models.ImageField(upload_to='portadas/', blank=True, null=True)
    ubicacion = models.CharField(max_length=100, blank=True)
    sitio_web = models.URLField(blank=True)
    instagram = models.CharField(max_length=100, blank=True)
    twitter = models.CharField(max_length=100, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Perfil Deportista'
        verbose_name_plural = 'Perfiles Deportistas'
    
    def __str__(self):
        return f"Perfil de {self.usuario.username}"

