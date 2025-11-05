from django.db import models
from django.conf import settings


class Publicacion(models.Model):
    """Modelo para publicaciones de los deportistas"""
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
    
    class Meta:
        verbose_name = 'Publicación'
        verbose_name_plural = 'Publicaciones'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['-fecha_creacion']),
            models.Index(fields=['autor']),
        ]
    
    def __str__(self):
        return f"Publicación de {self.autor.username} - {self.fecha_creacion.strftime('%Y-%m-%d')}"


class Like(models.Model):
    """Modelo para likes en publicaciones"""
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
        unique_together = ['usuario', 'publicacion']
        verbose_name = 'Like'
        verbose_name_plural = 'Likes'
    
    def __str__(self):
        return f"{self.usuario.username} le dio like a la publicación {self.publicacion.id}"


class Comentario(models.Model):
    """Modelo para comentarios en publicaciones"""
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
    contenido = models.TextField(max_length=500)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'
        ordering = ['fecha_creacion']
    
    def __str__(self):
        return f"Comentario de {self.usuario.username} en publicación {self.publicacion.id}"

