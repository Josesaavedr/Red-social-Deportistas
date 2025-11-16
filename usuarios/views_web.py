from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistroForm
from .models import Usuario, PerfilDeportista


def registro_view(request):
    """Vista para registro de usuarios"""
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            messages.success(request, f'¡Bienvenido {usuario.username}! Tu cuenta ha sido creada exitosamente.')
            return redirect('home')
    else:
        form = RegistroForm()
    return render(request, 'usuarios/registro.html', {'form': form})


def login_view(request):
    """Vista para inicio de sesión"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            usuario = authenticate(username=username, password=password)
            if usuario is not None:
                login(request, usuario)
                messages.success(request, f'¡Bienvenido de nuevo, {username}!')
                return redirect('home')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = AuthenticationForm()
    return render(request, 'usuarios/login.html', {'form': form})


def logout_view(request):
    """Vista para cerrar sesión"""
    logout(request)
    messages.success(request, '¡Has cerrado sesión exitosamente!')
    return redirect('home')


def perfil_usuario(request, username=None):
    """Vista para ver el perfil de un usuario"""
    if username:
        usuario = get_object_or_404(Usuario, username=username)
    else:
        # Si no se especifica username, mostrar el perfil del usuario actual
        if not request.user.is_authenticated:
            return redirect('login')
        usuario = request.user

    # Obtener o crear perfil deportista
    perfil, created = PerfilDeportista.objects.get_or_create(usuario=usuario)

    # Obtener estadísticas
    publicaciones = usuario.publicaciones.all()[:10]
    eventos_organizados = usuario.eventos_organizados.all()[:5]

    context = {
        'usuario': usuario,
        'perfil': perfil,
        'publicaciones': publicaciones,
        'eventos_organizados': eventos_organizados,
        'es_propio': request.user == usuario,
    }
    return render(request, 'usuarios/perfil.html', context)


@login_required
def editar_perfil(request):
    """Vista para editar el perfil del usuario"""
    perfil, created = PerfilDeportista.objects.get_or_create(usuario=request.user)

    if request.method == 'POST':
        # Actualizar datos del usuario
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()

        # Actualizar perfil deportista
        perfil.deporte_principal = request.POST.get('deporte_principal', 'otro')
        perfil.nivel = request.POST.get('nivel', 'intermedio')
        perfil.biografia = request.POST.get('biografia', '')
        perfil.ubicacion = request.POST.get('ubicacion', '')
        perfil.sitio_web = request.POST.get('sitio_web', '')
        perfil.instagram = request.POST.get('instagram', '')
        perfil.twitter = request.POST.get('twitter', '')

        if 'foto_perfil' in request.FILES:
            perfil.foto_perfil = request.FILES['foto_perfil']

        if 'foto_portada' in request.FILES:
            perfil.foto_portada = request.FILES['foto_portada']

        perfil.save()

        messages.success(request, '¡Perfil actualizado exitosamente!')
        return redirect('perfil_usuario')

    context = {
        'perfil': perfil,
    }
    return render(request, 'usuarios/editar_perfil.html', context)

