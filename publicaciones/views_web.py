from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db import transaction
from .models import Publicacion, Like, Comentario, SesionEntrenamiento
import json


def home(request):
    """Vista principal - página de bienvenida"""
    return render(request, 'publicaciones/feed.html')


def lista_publicaciones(request):
    """Vista para mostrar lista de publicaciones"""
    publicaciones = Publicacion.objects.select_related('autor').prefetch_related('likes', 'comentarios').order_by('-fecha_creacion')
    
    # Procesar publicaciones de entrenamiento para extraer datos del timer
    for publicacion in publicaciones:
        if 'TIMER:' in publicacion.contenido:
            publicacion.tipo = 'entrenamiento'
            # Extraer datos del timer y otros campos
            lines = publicacion.contenido.splitlines()
            publicacion.timer_data = {}
            
            for line in lines:
                if 'TIMER:' in line:
                    timer_str = line.replace('TIMER:', '').strip()
                    time_parts = timer_str.split(':')
                    if len(time_parts) == 3:
                        publicacion.timer_data['horas'] = time_parts[0]
                        publicacion.timer_data['minutos'] = time_parts[1]
                        publicacion.timer_data['segundos'] = time_parts[2]
                elif 'DEPORTE:' in line:
                    publicacion.timer_data['deporte'] = line.replace('DEPORTE:', '').strip()
                elif 'DISTANCIA:' in line:
                    publicacion.timer_data['distancia'] = line.replace('DISTANCIA:', '').strip()
                elif 'CALORIAS:' in line:
                    publicacion.timer_data['calorias'] = line.replace('CALORIAS:', '').strip()
                elif 'FECHA:' in line:
                    publicacion.timer_data['fecha'] = line.replace('FECHA:', '').strip()
                elif 'NOTAS:' in line:
                    publicacion.timer_data['notas'] = line.replace('NOTAS:', '').strip()
        else:
            publicacion.tipo = 'normal'
    
    # Obtener likes del usuario actual
    user_likes = []
    if request.user.is_authenticated:
        user_likes = list(Like.objects.filter(usuario=request.user).values_list('publicacion_id', flat=True))
    
    # Verificar si hay sesión de entrenamiento activa
    sesion_activa = None
    if request.user.is_authenticated:
        sesion_activa = SesionEntrenamiento.objects.filter(
            usuario=request.user,
            estado__in=['activo', 'pausado']
        ).first()
    
    # Deportes populares para el modal
    deportes_populares = SesionEntrenamiento.DEPORTE_CHOICES
    
    context = {
        'publicaciones': publicaciones,
        'user_likes': user_likes,
        'sesion_activa': sesion_activa,
        'deportes_populares': deportes_populares,
    }
    return render(request, 'publicaciones/lista.html', context)


def detalle_publicacion(request, pk):
    """Vista para ver el detalle de una publicación"""
    publicacion = get_object_or_404(
        Publicacion.objects.select_related('autor', 'autor__perfil').prefetch_related(
            'comentarios__usuario',
            'likes__usuario'
        ),
        pk=pk
    )

    # Procesar si es una publicación de entrenamiento
    if 'TIMER:' in publicacion.contenido:
        publicacion.tipo = 'entrenamiento'
        # Extraer datos del timer y otros campos
        lines = publicacion.contenido.splitlines()
        publicacion.timer_data = {}

        for line in lines:
            if 'TIMER:' in line:
                timer_str = line.replace('TIMER:', '').strip()
                time_parts = timer_str.split(':')
                if len(time_parts) == 3:
                    publicacion.timer_data['horas'] = time_parts[0]
                    publicacion.timer_data['minutos'] = time_parts[1]
                    publicacion.timer_data['segundos'] = time_parts[2]
            elif 'DEPORTE:' in line:
                publicacion.timer_data['deporte'] = line.replace('DEPORTE:', '').strip()
            elif 'DISTANCIA:' in line:
                publicacion.timer_data['distancia'] = line.replace('DISTANCIA:', '').strip()
            elif 'CALORIAS:' in line:
                publicacion.timer_data['calorias'] = line.replace('CALORIAS:', '').strip()
            elif 'FECHA:' in line:
                publicacion.timer_data['fecha'] = line.replace('FECHA:', '').strip()
            elif 'NOTAS:' in line:
                publicacion.timer_data['notas'] = line.replace('NOTAS:', '').strip()
    else:
        publicacion.tipo = 'normal'

    # Verificar si el usuario actual le dio like
    user_liked = False
    if request.user.is_authenticated:
        user_liked = Like.objects.filter(usuario=request.user, publicacion=publicacion).exists()

    context = {
        'publicacion': publicacion,
        'user_liked': user_liked,
    }
    return render(request, 'publicaciones/detalle.html', context)


@login_required
def crear_publicacion(request):
    """Vista para crear una nueva publicación"""
    if request.method == 'POST':
        contenido = request.POST.get('contenido', '').strip()
        imagen = request.FILES.get('imagen')
        
        if not contenido:
            messages.error(request, 'El contenido de la publicación no puede estar vacío.')
            return redirect('lista_publicaciones')
        
        publicacion = Publicacion.objects.create(
            autor=request.user,
            contenido=contenido,
            imagen=imagen
        )
        
        messages.success(request, '¡Publicación creada exitosamente!')
        return redirect('detalle_publicacion', pk=publicacion.pk)
    
    return render(request, 'publicaciones/crear.html')


@login_required
@require_POST
def toggle_like(request, pk):
    """Vista para dar o quitar like a una publicación (AJAX)"""
    publicacion = get_object_or_404(Publicacion, pk=pk)
    
    like, created = Like.objects.get_or_create(
        usuario=request.user,
        publicacion=publicacion
    )
    
    if not created:
        # Si ya existe, lo eliminamos (quitar like)
        like.delete()
        publicacion.likes_count = max(0, publicacion.likes_count - 1)
        publicacion.save()
        liked = False
    else:
        # Incrementar contador
        publicacion.likes_count += 1
        publicacion.save()
        liked = True
    
    return JsonResponse({
        'liked': liked,
        'likes_count': publicacion.likes_count
    })


@login_required
@require_POST
def crear_comentario(request, pk):
    """Vista para crear un comentario en una publicación"""
    publicacion = get_object_or_404(Publicacion, pk=pk)
    contenido = request.POST.get('contenido', '').strip()
    
    if not contenido:
        messages.error(request, 'El comentario no puede estar vacío.')
        return redirect('detalle_publicacion', pk=pk)
    
    comentario = Comentario.objects.create(
        usuario=request.user,
        publicacion=publicacion,
        contenido=contenido
    )
    
    # Incrementar contador
    publicacion.comentarios_count += 1
    publicacion.save()
    
    messages.success(request, '¡Comentario agregado!')
    return redirect('detalle_publicacion', pk=pk)


@login_required
def eliminar_publicacion(request, pk):
    """Vista para eliminar una publicación"""
    publicacion = get_object_or_404(Publicacion, pk=pk, autor=request.user)
    
    if request.method == 'POST':
        publicacion.delete()
        messages.success(request, 'Publicación eliminada exitosamente.')
        return redirect('lista_publicaciones')
    
    return render(request, 'publicaciones/confirmar_eliminar.html', {'publicacion': publicacion})

@login_required
@require_POST
def iniciar_entrenamiento(request):
    """Vista para iniciar una sesión de entrenamiento"""
    print(f"Iniciando entrenamiento para usuario: {request.user}")  # Debug
    
    # Verificar que no haya una sesión activa
    sesion_existente = SesionEntrenamiento.objects.filter(
        usuario=request.user,
        estado__in=['activo', 'pausado']
    ).first()
    
    if sesion_existente:
        print(f"Sesión existente encontrada: {sesion_existente}")  # Debug
        return JsonResponse({'success': False, 'error': 'Ya tienes una sesión activa'})
    
    deporte = request.POST.get('deporte')
    print(f"Deporte recibido: {deporte}")  # Debug
    
    if not deporte:
        return JsonResponse({'success': False, 'error': 'Deporte requerido'})
    
    try:
        sesion = SesionEntrenamiento.objects.create(
            usuario=request.user,
            deporte=deporte,
            estado='activo'
        )
        print(f"Sesión creada: {sesion}")  # Debug
        return JsonResponse({'success': True, 'sesion_id': sesion.id})
    except Exception as e:
        print(f"Error creando sesión: {e}")  # Debug
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_POST
def controlar_entrenamiento(request):
    """Vista para controlar entrenamiento (pausar/reanudar/cancelar/finalizar)"""
    try:
        sesion = SesionEntrenamiento.objects.get(
            usuario=request.user,
            estado__in=['activo', 'pausado']
        )
    except SesionEntrenamiento.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'No hay sesión activa'})
    
    accion = request.POST.get('accion')
    
    if accion == 'pausar':
        sesion.estado = 'pausado'
        sesion.save()
        return JsonResponse({'success': True})
    
    elif accion == 'reanudar':
        sesion.estado = 'activo'
        sesion.save()
        return JsonResponse({'success': True})
    
    elif accion == 'cancelar':
        sesion.estado = 'cancelado'
        sesion.save()
        return JsonResponse({'success': True})
    
    elif accion == 'finalizar':
        # Obtener datos adicionales
        distancia = request.POST.get('distancia')
        calorias = request.POST.get('calorias')
        notas = request.POST.get('notas', '')
        
        # Finalizar sesión
        sesion.estado = 'completado'
        sesion.fin = timezone.now()
        if distancia:
            try:
                sesion.distancia = float(distancia)
            except (ValueError, TypeError):
                pass
        if calorias:
            try:
                sesion.calorias = int(calorias)
            except (ValueError, TypeError):
                pass
        sesion.notas = notas
        sesion.save()
        
        # Crear publicación automática con formato especial
        duracion = sesion.duracion_total()
        horas = int(duracion.total_seconds() // 3600)
        minutos = int((duracion.total_seconds() % 3600) // 60)
        segundos = int(duracion.total_seconds() % 60)
        
        # Formato especial para la publicación sin emojis
        contenido = "ENTRENAMIENTO COMPLETADO\n"
        contenido += "=" * 40 + "\n\n"
        
        # Datos del timer para renderizar visualmente
        contenido += f"TIMER:{horas:02d}:{minutos:02d}:{segundos:02d}\n"
        contenido += f"DEPORTE: {sesion.get_deporte_display().upper()}\n"
        
        if sesion.distancia:
            contenido += f"DISTANCIA: {sesion.distancia} km\n"
        if sesion.calorias:
            contenido += f"CALORIAS: {sesion.calorias} kcal\n"
        
        contenido += f"FECHA: {sesion.fin.strftime('%d/%m/%Y a las %H:%M')}\n"
        
        if sesion.notas:
            contenido += f"\nNOTAS:\n{sesion.notas}\n"
        
        contenido += "\n" + "=" * 40
        contenido += f"\n#entrenamiento #{sesion.deporte} #fitness #deporte"
        
        publicacion = Publicacion.objects.create(
            autor=request.user,
            contenido=contenido,
            tipo='entrenamiento'
        )
        
        sesion.publicacion = publicacion
        sesion.save()
        
        return JsonResponse({'success': True, 'publicacion_id': publicacion.id})
    
    return JsonResponse({'success': False, 'error': 'Acción no válida'})

@login_required
def finalizar_entrenamiento(request):
    """Vista para finalizar entrenamiento - redirige al control con acción finalizar"""
    if request.method == 'POST':
        return controlar_entrenamiento(request)
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
def obtener_tiempo_entrenamiento(request):
    """Vista para obtener el tiempo actual del entrenamiento"""
    try:
        sesion = SesionEntrenamiento.objects.get(
            usuario=request.user,
            estado__in=['activo', 'pausado']
        )
        duracion = sesion.duracion_total()
        return JsonResponse({
            'success': True,
            'duracion_segundos': int(duracion.total_seconds()),
            'estado': sesion.estado
        })
    except SesionEntrenamiento.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'No hay sesión activa'})







