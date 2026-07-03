from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Chamado, MensagemChat, Etiqueta, HistoricoEtiqueta, AgendamentoMultimidia


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display  = ['username', 'email', 'first_name', 'last_name', 'tipo', 'is_active', 'date_joined']
    list_filter   = ['tipo', 'is_active', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering      = ['username']
    fieldsets     = UserAdmin.fieldsets + (
        ('Perfil do Sistema', {'fields': ('tipo',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Perfil do Sistema', {'fields': ('tipo',)}),
    )


@admin.register(Etiqueta)
class EtiquetaAdmin(admin.ModelAdmin):
    list_display  = ['nome', 'cor', 'ativa']
    list_filter   = ['ativa']
    search_fields = ['nome']
    ordering      = ['nome']


@admin.register(Chamado)
class ChamadoAdmin(admin.ModelAdmin):
    list_display  = ['id', 'nome_usuario', 'status', 'tipo', 'categoria', 'local', 'data_abertura', 'atendente']
    list_filter   = ['status', 'tipo']
    search_fields = ['nome_usuario__username', 'categoria', 'local', 'problema']
    ordering      = ['-data_abertura']
    readonly_fields = ['data_abertura', 'data_triagem', 'data_atendimento', 'data_fechamento', 'data_reabertura']
    filter_horizontal = ['etiquetas']

    fieldsets = (
        ('Solicitação', {
            'fields': ('nome_usuario', 'local', 'categoria', 'tipo', 'problema', 'etiquetas')
        }),
        ('Status e Atendimento', {
            'fields': ('status', 'atendente', 'atendente_fechamento', 'reaberto_por')
        }),
        ('Timestamps', {
            'fields': ('data_abertura', 'data_triagem', 'data_atendimento', 'data_fechamento', 'data_reabertura'),
            'classes': ('collapse',),
        }),
    )


@admin.register(HistoricoEtiqueta)
class HistoricoEtiquetaAdmin(admin.ModelAdmin):
    list_display  = ['chamado', 'etiqueta', 'acao', 'usuario', 'data']
    list_filter   = ['acao', 'etiqueta']
    search_fields = ['chamado__id', 'usuario__username', 'etiqueta__nome']
    ordering      = ['-data']
    readonly_fields = ['chamado', 'etiqueta', 'acao', 'usuario', 'data']


@admin.register(MensagemChat)
class MensagemChatAdmin(admin.ModelAdmin):
    list_display  = ['id', 'chamado', 'autor', 'data']
    list_filter   = ['chamado__status']
    search_fields = ['autor__username', 'mensagem']
    ordering      = ['-data']
    readonly_fields = ['data']


@admin.register(AgendamentoMultimidia)
class AgendamentoMultimidiaAdmin(admin.ModelAdmin):
    list_display   = ['id', 'solicitante', 'local', 'data', 'horario_inicio', 'horario_fim', 'status', 'created_at']
    list_filter    = ['status', 'data']
    search_fields  = ['solicitante__username', 'local', 'sala', 'setor']
    ordering       = ['-data', 'horario_inicio']
    readonly_fields = ['created_at']
