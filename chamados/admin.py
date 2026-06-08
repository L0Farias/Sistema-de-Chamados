from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Chamado, MensagemChat


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'tipo', 'is_active', 'date_joined']
    list_filter = ['tipo', 'is_active', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['username']

    fieldsets = UserAdmin.fieldsets + (
        ('Perfil do Sistema', {'fields': ('tipo',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Perfil do Sistema', {'fields': ('tipo',)}),
    )


@admin.register(Chamado)
class ChamadoAdmin(admin.ModelAdmin):
    list_display = ['id', 'nome_usuario', 'status', 'tipo', 'etiqueta', 'categoria', 'local', 'data_abertura', 'atendente']
    list_filter = ['status', 'tipo', 'etiqueta']
    search_fields = ['nome_usuario__username', 'categoria', 'local', 'problema']
    ordering = ['-data_abertura']
    readonly_fields = ['data_abertura', 'data_triagem', 'data_atendimento', 'data_fechamento']

    fieldsets = (
        ('Solicitação', {
            'fields': ('nome_usuario', 'local', 'categoria', 'tipo', 'etiqueta', 'problema')
        }),
        ('Status e Atendimento', {
            'fields': ('status', 'atendente')
        }),
        ('Timestamps', {
            'fields': ('data_abertura', 'data_triagem', 'data_atendimento', 'data_fechamento'),
            'classes': ('collapse',),
        }),
    )


@admin.register(MensagemChat)
class MensagemChatAdmin(admin.ModelAdmin):
    list_display = ['id', 'chamado', 'autor', 'data']
    list_filter = ['chamado__status']
    search_fields = ['autor__username', 'mensagem']
    ordering = ['-data']
    readonly_fields = ['data']
