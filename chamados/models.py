from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.validators import RegexValidator


class Usuario(AbstractUser):
    tipo = models.CharField(
        max_length=10,
        choices=[
            ('comum', 'Usuário Comum'),
            ('ti', 'Equipe TI'),
        ],
        default='comum'
    )
    email = models.EmailField(
        unique=True,
        blank=False,
        null=False,
        verbose_name="E-mail"
    )

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"


class Etiqueta(models.Model):
    _hex_validator = RegexValidator(
        regex=r'^#[0-9A-Fa-f]{6}$',
        message='A cor deve estar no formato hexadecimal #RRGGBB.'
    )

    nome = models.CharField(max_length=50, unique=True, verbose_name="Nome")
    cor  = models.CharField(
        max_length=7,
        validators=[_hex_validator],
        default='#6366f1',
        verbose_name="Cor (hex)"
    )
    ativa = models.BooleanField(default=True, verbose_name="Ativa")

    class Meta:
        ordering = ['nome']
        verbose_name = "Etiqueta"
        verbose_name_plural = "Etiquetas"

    def __str__(self):
        return self.nome


class Chamado(models.Model):
    STATUS_CHOICES = [
        ('Novo', 'Novo'),
        ('Triagem', 'Triagem'),
        ('Em Atendimento', 'Em Atendimento'),
        ('Fechado', 'Fechado'),
    ]

    TIPO_CHOICES = [
        ('problema', 'Problema'),
        ('solicitacao', 'Solicitação'),
    ]

    nome_usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE,
        related_name='chamados_abertos', verbose_name="Solicitante"
    )
    local     = models.CharField(max_length=100, verbose_name="Local")
    categoria = models.CharField(max_length=100, verbose_name="Categoria")
    tipo      = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name="Tipo")
    problema  = models.TextField(verbose_name="Descrição do Problema")

    etiquetas = models.ManyToManyField(
        Etiqueta,
        blank=True,
        related_name='chamados',
        verbose_name="Etiquetas"
    )

    data_abertura = models.DateTimeField(default=timezone.now, verbose_name="Data de Abertura")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='Novo', verbose_name="Status"
    )

    atendente = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='chamados_atendidos', verbose_name="Atendente"
    )
    atendente_fechamento = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='chamados_fechados', verbose_name="Atendente no Fechamento"
    )
    reaberto_por = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='chamados_reabertos', verbose_name="Reaberto Por"
    )

    data_triagem     = models.DateTimeField(null=True, blank=True)
    data_atendimento = models.DateTimeField(null=True, blank=True)
    data_fechamento  = models.DateTimeField(null=True, blank=True)
    data_reabertura  = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-data_abertura']
        verbose_name = "Chamado"
        verbose_name_plural = "Chamados"

    def __str__(self):
        return f"Chamado #{self.id} - {self.nome_usuario}"


class HistoricoEtiqueta(models.Model):
    ACAO_CHOICES = [
        ('adicionada', 'Adicionada'),
        ('removida',   'Removida'),
    ]

    chamado  = models.ForeignKey(Chamado,  on_delete=models.CASCADE, related_name='historico_etiquetas')
    etiqueta = models.ForeignKey(Etiqueta, on_delete=models.CASCADE, related_name='historico')
    acao     = models.CharField(max_length=10, choices=ACAO_CHOICES)
    usuario  = models.ForeignKey(Usuario,  on_delete=models.CASCADE)
    data     = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['data']
        verbose_name = "Histórico de Etiqueta"
        verbose_name_plural = "Histórico de Etiquetas"

    def __str__(self):
        return f"{self.chamado} — {self.etiqueta} {self.acao} por {self.usuario}"


class MensagemChat(models.Model):
    chamado  = models.ForeignKey(Chamado, on_delete=models.CASCADE, related_name='mensagens')
    autor    = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    mensagem = models.TextField()
    data     = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['data']
        verbose_name = "Mensagem"
        verbose_name_plural = "Mensagens do Chat"

    def __str__(self):
        return f"{self.autor} - Chamado #{self.chamado.id}"
