from django.db import models
from django.conf import settings


class EventoDeportivo(models.Model):
    """Modelo para eventos deportivos"""
    TIPO_CHOICES = [
        ('competicion', 'Competición'),
        ('entrenamiento', 'Entrenamiento'),
        ('reunion', 'Reunión'),
        ('torneo', 'Torneo'),
        ('otro', 'Otro'),
    ]
    
    organizador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='eventos_organizados'
    )
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(max_length=1000)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='otro')
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    ubicacion = models.CharField(max_length=200)
    imagen = models.ImageField(upload_to='eventos/', blank=True, null=True)
    capacidad_maxima = models.IntegerField(null=True, blank=True)
    participantes_count = models.IntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    es_publico = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Evento Deportivo'
        verbose_name_plural = 'Eventos Deportivos'
        ordering = ['fecha_inicio']
        indexes = [
            models.Index(fields=['fecha_inicio']),
            models.Index(fields=['organizador']),
        ]
    
    def __str__(self):
        return f"{self.titulo} - {self.fecha_inicio.strftime('%Y-%m-%d')}"


class ParticipanteEvento(models.Model):
    """Modelo para participantes en eventos"""
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='eventos_participacion'
    )
    evento = models.ForeignKey(
        EventoDeportivo,
        on_delete=models.CASCADE,
        related_name='participantes'
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    confirmado = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['usuario', 'evento']
        verbose_name = 'Participante Evento'
        verbose_name_plural = 'Participantes Eventos'
        ordering = ['fecha_registro']
    
    def __str__(self):
        return f"{self.usuario.username} en {self.evento.titulo}"

