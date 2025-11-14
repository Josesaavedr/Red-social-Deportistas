from django.db import models
from django.conf import settings
from django.utils import timezone


class Publicacion(models.Model):
    TIPO_CHOICES = [
        ('normal', 'Publicación Normal'),
        ('entrenamiento', 'Sesión de Entrenamiento'),
    ]
    
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='publicaciones'
    )
    contenido = models.TextField(max_length=2000)
    imagen = models.ImageField(upload_to='publicaciones/', blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    likes_count = models.IntegerField(default=0)
    comentarios_count = models.IntegerField(default=0)
    
    # Campo para entrenamientos
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='normal')
    
    class Meta:
        verbose_name = 'Publicación'
        verbose_name_plural = 'Publicaciones'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['-fecha_creacion']),
            models.Index(fields=['autor']),
        ]

    def __str__(self):
        return f"{self.autor.username} - {self.contenido[:50]}..."


class Like(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='likes'
    )
    publicacion = models.ForeignKey(
        Publicacion, 
        on_delete=models.CASCADE, 
        related_name='likes'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('usuario', 'publicacion')
        verbose_name = 'Like'
        verbose_name_plural = 'Likes'

    def __str__(self):
        return f"{self.usuario.username} likes {self.publicacion.id}"


class Comentario(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='comentarios'
    )
    publicacion = models.ForeignKey(
        Publicacion, 
        on_delete=models.CASCADE, 
        related_name='comentarios'
    )
    contenido = models.TextField(max_length=1000)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['fecha_creacion']
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'

    def __str__(self):
        return f"{self.usuario.username} - {self.contenido[:30]}..."


class SesionEntrenamiento(models.Model):
    ESTADO_CHOICES = [
        ('activo', 'En Progreso'),
        ('pausado', 'Pausado'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]
    
    DEPORTE_CHOICES = [
        ('correr', 'Correr'),
        ('ciclismo', 'Ciclismo'),
        ('natacion', 'Natación'),
        ('gimnasio', 'Gimnasio'),
        ('yoga', 'Yoga'),
        ('futbol', 'Fútbol'),
        ('basquet', 'Básquet'),
        ('tenis', 'Tenis'),
        ('boxeo', 'Boxeo'),
        ('crossfit', 'CrossFit'),
    ]
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='sesiones_entrenamiento'
    )
    deporte = models.CharField(max_length=20, choices=DEPORTE_CHOICES)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')
    
    # Tiempos
    inicio = models.DateTimeField(auto_now_add=True)
    fin = models.DateTimeField(null=True, blank=True)
    tiempo_pausado = models.DurationField(default=timezone.timedelta(0))
    
    # Datos adicionales
    distancia = models.FloatField(null=True, blank=True, help_text="Distancia en km")
    calorias = models.IntegerField(null=True, blank=True)
    notas = models.TextField(blank=True, max_length=500)
    
    # Publicación generada
    publicacion = models.OneToOneField(
        Publicacion, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='sesion_entrenamiento'
    )
    
    class Meta:
        verbose_name = 'Sesión de Entrenamiento'
        verbose_name_plural = 'Sesiones de Entrenamiento'
        ordering = ['-inicio']
    
    def duracion_total(self):
        if self.fin:
            return (self.fin - self.inicio) - self.tiempo_pausado
        return (timezone.now() - self.inicio) - self.tiempo_pausado
    
    def __str__(self):
        return f"{self.usuario.username} - {self.get_deporte_display()} ({self.estado})"


