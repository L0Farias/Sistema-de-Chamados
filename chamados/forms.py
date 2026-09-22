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


# ====================== FORMULÁRIO DE AGENDAMENTO DE MULTIMÍDIA ======================
from .models import AgendamentoMultimidia
import datetime

EQUIPAMENTOS_CHOICES = [
    ('Projetor',       'Projetor'),
    ('Notebook',       'Notebook'),
    ('Caixa de Som',   'Caixa de Som'),
    ('Microfone',      'Microfone'),
    ('Outro',          'Outro'),
]

# Locais fixos — sincronizados com AgendamentoMultimidia.LOCAIS_CHOICES
LOCAIS_CHOICES = AgendamentoMultimidia.LOCAIS_CHOICES

class AgendamentoMultimidiaForm(forms.Form):
    setor = forms.CharField(
        label="Setor",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Departamento de RH'})
    )
    local = forms.ChoiceField(
        label="Local *",
        choices=[('', '— Selecione o local —')] + list(LOCAIS_CHOICES),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    sala = forms.CharField(
        label="Sala / Ambiente específico",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Auditório Principal (opcional)'})
    )
    data = forms.DateField(
        label="Data",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    horario_inicio = forms.TimeField(
        label="Horário de Início",
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'})
    )
    horario_fim = forms.TimeField(
        label="Horário de Fim",
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'})
    )
    equipamentos = forms.MultipleChoiceField(
        label="Equipamentos Necessários",
        choices=EQUIPAMENTOS_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=True
    )
    finalidade = forms.CharField(
        label="Finalidade",
        max_length=300,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Apresentação de resultados'})
    )
    observacoes = forms.CharField(
        label="Observações",
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Informações adicionais...'})
    )

    def clean_local(self):
        local = self.cleaned_data.get('local', '').strip()
        if not local:
            raise forms.ValidationError('Selecione um local.')
        valid = [v for v, _ in LOCAIS_CHOICES]
        if local not in valid:
            raise forms.ValidationError('Local inválido. Selecione uma das opções disponíveis.')
        return local

    def clean(self):
        cleaned = super().clean()
        data       = cleaned.get('data')
        h_inicio   = cleaned.get('horario_inicio')
        h_fim      = cleaned.get('horario_fim')
        equip      = cleaned.get('equipamentos')

        if data and data < datetime.date.today():
            self.add_error('data', 'A data não pode ser anterior a hoje.')

        if h_inicio and h_fim:
            if h_fim <= h_inicio:
                self.add_error('horario_fim', 'O horário de fim deve ser posterior ao horário de início.')

        if not equip:
            self.add_error('equipamentos', 'Selecione ao menos um equipamento.')

        return cleaned
