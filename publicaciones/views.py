from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.db.models import Count, Q
from .models import Publicacion, Like, Comentario
from .serializers import PublicacionSerializer, LikeSerializer, ComentarioSerializer


class PublicacionViewSet(viewsets.ModelViewSet):
    queryset = Publicacion.objects.all().select_related('autor').prefetch_related('comentarios__usuario', 'likes')
    serializer_class = PublicacionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtrar por usuario si se especifica
        usuario_id = self.request.query_params.get('usuario', None)
        if usuario_id:
            queryset = queryset.filter(autor_id=usuario_id)
        return queryset
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def perform_create(self, serializer):
        serializer.save(autor=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        """Dar o quitar like a una publicación"""
        publicacion = self.get_object()
        like, created = Like.objects.get_or_create(
            usuario=request.user,
            publicacion=publicacion
        )
        
        if not created:
            # Si ya existe, lo eliminamos (quitar like)
            like.delete()
            publicacion.likes_count = max(0, publicacion.likes_count - 1)
            publicacion.save()
            return Response({'liked': False}, status=status.HTTP_200_OK)
        
        # Incrementar contador
        publicacion.likes_count += 1
        publicacion.save()
        return Response({'liked': True}, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def comentar(self, request, pk=None):
        """Agregar un comentario a una publicación"""
        publicacion = self.get_object()
        serializer = ComentarioSerializer(data=request.data)
        
        if serializer.is_valid():
            comentario = serializer.save(usuario=request.user, publicacion=publicacion)
            publicacion.comentarios_count += 1
            publicacion.save()
            return Response(ComentarioSerializer(comentario).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ComentarioViewSet(viewsets.ModelViewSet):
    queryset = Comentario.objects.all().select_related('usuario', 'publicacion')
    serializer_class = ComentarioSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

