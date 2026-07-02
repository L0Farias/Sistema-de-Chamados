from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Chamado

# ====================== FORMULÁRIO DE LOGIN ======================
class LoginForm(forms.Form):
    username = forms.CharField(
        label="Nome de Usuário",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite seu usuário'
        })
    )
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite sua senha'
        })
    )


# ====================== FORMULÁRIO DE CADASTRO ======================
class UsuarioComumCreationForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True

        self.fields['first_name'].label = "Primeiro Nome"
        self.fields['last_name'].label = "Último Nome"
        self.fields['email'].label = "E-mail"
        self.fields['username'].label = "Nome de Usuário"

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Este email já está cadastrado no sistema.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if Usuario.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Este nome de usuário já está em uso.")
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.tipo = 'comum'
        if commit:
            user.save()
        return user


# ====================== FORMULÁRIO DE CHAMADO ======================
class ChamadoForm(forms.ModelForm):
    class Meta:
        model = Chamado
        fields = ['local', 'categoria', 'tipo', 'problema']
        widgets = {
            'problema': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Descreva o problema ou solicitação...'}),
            'local': forms.TextInput(attrs={'placeholder': 'Ex: Sala 12, Setor Financeiro'}),
            'categoria': forms.TextInput(attrs={'placeholder': 'Ex: Impressora, Rede, Software...'}),
        }
        labels = {
            'local': 'Local',
            'categoria': 'Categoria',
            'tipo': 'Tipo de Chamado',
            'problema': 'Descrição do Problema / Solicitação',
        }