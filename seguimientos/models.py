from django.db import models
from django.conf import settings


class Seguimiento(models.Model):
    """Modelo para seguir a otros usuarios"""
    seguidor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='siguiendo'
    )
    seguido = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='seguidores'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['seguidor', 'seguido']
        verbose_name = 'Seguimiento'
        verbose_name_plural = 'Seguimientos'
        indexes = [
            models.Index(fields=['seguidor']),
            models.Index(fields=['seguido']),
        ]
    
    def __str__(self):
        return f"{self.seguidor.username} sigue a {self.seguido.username}"
    
    def clean(self):
        """Validar que un usuario no se siga a sí mismo"""
        from django.core.exceptions import ValidationError
        if self.seguidor == self.seguido:
            raise ValidationError('Un usuario no puede seguirse a sí mismo.')
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

