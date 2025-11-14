from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import EventoDeportivo, ParticipanteEvento


def lista_eventos(request):
    """Vista para mostrar la lista de eventos"""
    # Filtrar eventos futuros por defecto
    filtro = request.GET.get('filtro', 'futuros')
    
    eventos = EventoDeportivo.objects.select_related(
        'organizador', 'organizador__perfil'
    ).prefetch_related('participantes__usuario')
    
    if filtro == 'futuros':
        eventos = eventos.filter(fecha_inicio__gte=timezone.now())
    elif filtro == 'pasados':
        eventos = eventos.filter(fecha_fin__lt=timezone.now())
    elif filtro == 'mis_eventos' and request.user.is_authenticated:
        eventos = eventos.filter(organizador=request.user)
    
    # Si el usuario está autenticado, obtener eventos en los que participa
    user_participaciones = []
    if request.user.is_authenticated:
        user_participaciones = ParticipanteEvento.objects.filter(
            usuario=request.user
        ).values_list('evento_id', flat=True)
    
    context = {
        'eventos': eventos,
        'filtro': filtro,
        'user_participaciones': list(user_participaciones),
    }
    return render(request, 'eventos/lista.html', context)


def detalle_evento(request, pk):
    """Vista para ver el detalle de un evento"""
    evento = get_object_or_404(
        EventoDeportivo.objects.select_related(
            'organizador', 'organizador__perfil'
        ).prefetch_related('participantes__usuario'),
        pk=pk
    )
    
    # Verificar si el usuario actual está participando
    user_participa = False
    if request.user.is_authenticated:
        user_participa = ParticipanteEvento.objects.filter(
            usuario=request.user, evento=evento
        ).exists()
    
    context = {
        'evento': evento,
        'user_participa': user_participa,
    }
    return render(request, 'eventos/detalle.html', context)


@login_required
def crear_evento(request):
    """Vista para crear un nuevo evento"""
    if request.method == 'POST':
        titulo = request.POST.get('titulo', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        tipo = request.POST.get('tipo', 'otro')
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        ubicacion = request.POST.get('ubicacion', '').strip()
        capacidad_maxima = request.POST.get('capacidad_maxima')
        imagen = request.FILES.get('imagen')
        es_publico = request.POST.get('es_publico') == 'on'
        
        # Validaciones
        if not all([titulo, descripcion, fecha_inicio, fecha_fin, ubicacion]):
            messages.error(request, 'Todos los campos obligatorios deben ser completados.')
            return render(request, 'eventos/crear.html')
        
        # Crear evento
        evento = EventoDeportivo.objects.create(
            organizador=request.user,
            titulo=titulo,
            descripcion=descripcion,
            tipo=tipo,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            ubicacion=ubicacion,
            capacidad_maxima=int(capacidad_maxima) if capacidad_maxima else None,
            imagen=imagen,
            es_publico=es_publico
        )
        
        messages.success(request, '¡Evento creado exitosamente!')
        return redirect('detalle_evento', pk=evento.pk)
    
    return render(request, 'eventos/crear.html')


@login_required
def participar_evento(request, pk):
    """Vista para participar en un evento"""
    evento = get_object_or_404(EventoDeportivo, pk=pk)
    
    # Verificar capacidad
    if evento.capacidad_maxima and evento.participantes_count >= evento.capacidad_maxima:
        messages.error(request, 'El evento ha alcanzado su capacidad máxima.')
        return redirect('detalle_evento', pk=pk)
    
    # Verificar si ya está participando
    participante, created = ParticipanteEvento.objects.get_or_create(
        usuario=request.user,
        evento=evento
    )
    
    if not created:
        messages.warning(request, 'Ya estás participando en este evento.')
    else:
        # Incrementar contador
        evento.participantes_count += 1
        evento.save()
        messages.success(request, '¡Te has unido al evento exitosamente!')
    
    return redirect('detalle_evento', pk=pk)


@login_required
def dejar_participar_evento(request, pk):
    """Vista para dejar de participar en un evento"""
    evento = get_object_or_404(EventoDeportivo, pk=pk)
    
    try:
        participante = ParticipanteEvento.objects.get(
            usuario=request.user,
            evento=evento
        )
        participante.delete()
        
        # Decrementar contador
        evento.participantes_count = max(0, evento.participantes_count - 1)
        evento.save()
        
        messages.success(request, 'Has dejado de participar en el evento.')
    except ParticipanteEvento.DoesNotExist:
        messages.error(request, 'No estás participando en este evento.')
    
    return redirect('detalle_evento', pk=pk)

