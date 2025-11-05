from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.utils import timezone
from .models import EventoDeportivo, ParticipanteEvento
from .serializers import EventoDeportivoSerializer, ParticipanteEventoSerializer


class EventoDeportivoViewSet(viewsets.ModelViewSet):
    queryset = EventoDeportivo.objects.all().select_related('organizador').prefetch_related('participantes__usuario')
    serializer_class = EventoDeportivoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtrar por organizador
        organizador_id = self.request.query_params.get('organizador', None)
        if organizador_id:
            queryset = queryset.filter(organizador_id=organizador_id)
        
        # Filtrar eventos futuros
        futuros = self.request.query_params.get('futuros', None)
        if futuros == 'true':
            queryset = queryset.filter(fecha_inicio__gte=timezone.now())
        
        # Filtrar eventos pasados
        pasados = self.request.query_params.get('pasados', None)
        if pasados == 'true':
            queryset = queryset.filter(fecha_fin__lt=timezone.now())
        
        return queryset
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def perform_create(self, serializer):
        serializer.save(organizador=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def participar(self, request, pk=None):
        """Unirse a un evento"""
        evento = self.get_object()
        
        # Verificar capacidad
        if evento.capacidad_maxima and evento.participantes_count >= evento.capacidad_maxima:
            return Response(
                {'error': 'El evento ha alcanzado su capacidad máxima.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar si ya está participando
        participante, created = ParticipanteEvento.objects.get_or_create(
            usuario=request.user,
            evento=evento
        )
        
        if not created:
            return Response(
                {'error': 'Ya estás participando en este evento.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Incrementar contador
        evento.participantes_count += 1
        evento.save()
        
        return Response(
            ParticipanteEventoSerializer(participante).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated])
    def dejar_participar(self, request, pk=None):
        """Dejar de participar en un evento"""
        evento = self.get_object()
        
        try:
            participante = ParticipanteEvento.objects.get(
                usuario=request.user,
                evento=evento
            )
            participante.delete()
            
            # Decrementar contador
            evento.participantes_count = max(0, evento.participantes_count - 1)
            evento.save()
            
            return Response({'message': 'Has dejado de participar en el evento.'}, status=status.HTTP_200_OK)
        except ParticipanteEvento.DoesNotExist:
            return Response(
                {'error': 'No estás participando en este evento.'},
                status=status.HTTP_400_BAD_REQUEST
            )

