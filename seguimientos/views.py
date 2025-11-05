from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Seguimiento
from .serializers import SeguimientoSerializer
from usuarios.models import Usuario
from usuarios.serializers import UsuarioSerializer


class SeguimientoViewSet(viewsets.ModelViewSet):
    queryset = Seguimiento.objects.all().select_related('seguidor', 'seguido')
    serializer_class = SeguimientoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtrar por usuario autenticado
        usuario = self.request.user
        tipo = self.request.query_params.get('tipo', None)
        
        if tipo == 'seguidores':
            # Personas que siguen al usuario autenticado
            queryset = queryset.filter(seguido=usuario)
        elif tipo == 'siguiendo':
            # Personas que el usuario autenticado sigue
            queryset = queryset.filter(seguidor=usuario)
        else:
            # Por defecto, mostrar todos los seguimientos del usuario
            queryset = queryset.filter(Q(seguidor=usuario) | Q(seguido=usuario))
        
        return queryset
    
    def perform_create(self, serializer):
        seguido_id = self.request.data.get('seguido')
        if seguido_id == self.request.user.id:
            raise serializers.ValidationError({'error': 'No puedes seguirte a ti mismo.'})
        
        serializer.save(seguidor=self.request.user)
    
    @action(detail=False, methods=['get'])
    def seguidores(self, request):
        """Obtener lista de seguidores del usuario autenticado"""
        seguimientos = Seguimiento.objects.filter(seguido=request.user).select_related('seguidor')
        seguidores = [s.seguidor for s in seguimientos]
        serializer = UsuarioSerializer(seguidores, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def siguiendo(self, request):
        """Obtener lista de usuarios que sigue el usuario autenticado"""
        seguimientos = Seguimiento.objects.filter(seguidor=request.user).select_related('seguido')
        siguiendo = [s.seguido for s in seguimientos]
        serializer = UsuarioSerializer(siguiendo, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def seguir(self, request):
        """Seguir a un usuario"""
        seguido_id = request.data.get('usuario_id')
        
        if not seguido_id:
            return Response(
                {'error': 'Se requiere usuario_id.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            seguido = Usuario.objects.get(id=seguido_id)
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Usuario no encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if seguido == request.user:
            return Response(
                {'error': 'No puedes seguirte a ti mismo.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        seguimiento, created = Seguimiento.objects.get_or_create(
            seguidor=request.user,
            seguido=seguido
        )
        
        if not created:
            return Response(
                {'error': 'Ya estás siguiendo a este usuario.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(seguimiento)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['delete'])
    def dejar_seguir(self, request):
        """Dejar de seguir a un usuario"""
        seguido_id = request.data.get('usuario_id')
        
        if not seguido_id:
            return Response(
                {'error': 'Se requiere usuario_id.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            seguimiento = Seguimiento.objects.get(
                seguidor=request.user,
                seguido_id=seguido_id
            )
            seguimiento.delete()
            return Response({'message': 'Has dejado de seguir a este usuario.'}, status=status.HTTP_200_OK)
        except Seguimiento.DoesNotExist:
            return Response(
                {'error': 'No estás siguiendo a este usuario.'},
                status=status.HTTP_400_BAD_REQUEST
            )

