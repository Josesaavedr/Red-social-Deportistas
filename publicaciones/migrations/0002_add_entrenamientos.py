# Generated migration file
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone

class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('publicaciones', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='publicacion',
            name='tipo',
            field=models.CharField(choices=[('normal', 'Publicación Normal'), ('entrenamiento', 'Sesión de Entrenamiento')], default='normal', max_length=20),
        ),
        migrations.CreateModel(
            name='SesionEntrenamiento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deporte', models.CharField(choices=[('correr', '🏃 Correr'), ('ciclismo', '🚴 Ciclismo'), ('natacion', '🏊 Natación'), ('gimnasio', '💪 Gimnasio'), ('yoga', '🧘 Yoga'), ('futbol', '⚽ Fútbol'), ('basquet', '🏀 Básquet'), ('tenis', '🎾 Tenis'), ('boxeo', '🥊 Boxeo'), ('crossfit', '🏋️ CrossFit')], max_length=20)),
                ('estado', models.CharField(choices=[('activo', 'En Progreso'), ('pausado', 'Pausado'), ('completado', 'Completado'), ('cancelado', 'Cancelado')], default='activo', max_length=20)),
                ('inicio', models.DateTimeField(auto_now_add=True)),
                ('fin', models.DateTimeField(blank=True, null=True)),
                ('tiempo_pausado', models.DurationField(default=django.utils.timezone.timedelta(0))),
                ('distancia', models.FloatField(blank=True, help_text='Distancia en km', null=True)),
                ('calorias', models.IntegerField(blank=True, null=True)),
                ('notas', models.TextField(blank=True, max_length=500)),
                ('publicacion', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sesion_entrenamiento', to='publicaciones.publicacion')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
