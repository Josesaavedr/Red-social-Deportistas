from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import Usuario, PerfilDeportista
from .serializers import UsuarioSerializer, RegistroSerializer, PerfilDeportistaSerializer


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action == 'create' or self.action == 'registro':
            return [AllowAny()]
        return super().get_permissions()
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def registro(self, request):
        """Endpoint para registro de nuevos usuarios"""
        serializer = RegistroSerializer(data=request.data)
        if serializer.is_valid():
            usuario = serializer.save()
            token, created = Token.objects.get_or_create(user=usuario)
            return Response({
                'usuario': UsuarioSerializer(usuario).data,
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def perfil(self, request):
        """Obtener el perfil del usuario autenticado"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def actualizar_perfil(self, request):
        """Actualizar el perfil del usuario autenticado"""
        usuario = request.user
        serializer = self.get_serializer(usuario, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PerfilDeportistaViewSet(viewsets.ModelViewSet):
    queryset = PerfilDeportista.objects.all()
    serializer_class = PerfilDeportistaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return PerfilDeportista.objects.filter(usuario=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

