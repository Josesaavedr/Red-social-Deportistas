from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, PerfilDeportista


class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True, label='Nombre')
    last_name = forms.CharField(max_length=30, required=True, label='Apellido')
    
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
    
    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.email = self.cleaned_data['email']
        usuario.first_name = self.cleaned_data['first_name']
        usuario.last_name = self.cleaned_data['last_name']
        if commit:
            usuario.save()
            # Crear perfil por defecto
            PerfilDeportista.objects.create(usuario=usuario)
        return usuario

