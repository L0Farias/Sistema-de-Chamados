from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/',  views.login_view,  name='login'),
    path('logout/', views.logout_view, name='logout'),

    # ── USUÁRIO COMUM ──────────────────────────────
    path('meus-chamados/',  views.usuario_comum,  name='usuario_comum'),
    path('chamado/novo/',   views.criar_chamado,  name='criar_chamado'),

    # ── EQUIPE TI ──────────────────────────────────
    path('equipe-ti/', views.equipe_ti, name='equipe_ti'),

    # ── CADASTROS ──────────────────────────────────
    path('cadastrar-comum/', views.cadastrar_comum, name='cadastrar_comum'),
    path('cadastrar-ti/',    views.cadastrar_ti,    name='cadastrar_ti'),

    # ── CHAMADOS ───────────────────────────────────
    path('chamado/<int:pk>/', views.detalhe_chamado, name='detalhe_chamado'),

    # ── AÇÕES DE STATUS ────────────────────────────
    path('chamado/<int:pk>/triar/',   views.triar_chamado,       name='triar_chamado'),
    path('chamado/<int:pk>/iniciar/', views.iniciar_atendimento, name='iniciar_atendimento'),
    path('chamado/<int:pk>/fechar/',  views.fechar_chamado,      name='fechar_chamado'),
    path('chamado/<int:pk>/reabrir/', views.reabrir_chamado,     name='reabrir_chamado'),

    # ── CHAT ───────────────────────────────────────
    path('chamado/<int:pk>/mensagem/', views.enviar_mensagem, name='enviar_mensagem'),

    # ── AJAX GERAL ─────────────────────────────────
    path('chamado/<int:pk>/ajax/',          views.detalhe_chamado_ajax, name='detalhe_chamado_ajax'),
    path('load-more-chamados/',             views.load_more_chamados,   name='load_more_chamados'),
    path('api/kanban/polling/',             views.kanban_polling,       name='kanban_polling'),

    # ── AJAX ETIQUETAS ─────────────────────────────
    path('chamado/<int:pk>/etiquetas/',        views.etiquetas_chamado,       name='etiquetas_chamado'),
    path('chamado/<int:pk>/etiquetas/salvar/', views.salvar_etiquetas_chamado, name='salvar_etiquetas_chamado'),

    # ── RELATÓRIOS ─────────────────────────────────
    path('relatorios/',           views.relatorios,           name='relatorios'),
    path('relatorios/ajax/',      views.relatorios_ajax,      name='relatorios_ajax'),
    path('relatorios/dashboard/', views.relatorios_dashboard, name='relatorios_dashboard'),
    path('relatorios/exportar/',  views.relatorios_exportar,  name='relatorios_exportar'),
]

# ── NOVOS MÓDULOS (adicionados na reestruturação modular) ─────────
urlpatterns += [
    path('dashboard/',     views.dashboard,              name='dashboard'),
    path('agendamento/',   views.agendamento_multimidia, name='agendamento_multimidia'),
    path('configuracoes/', views.configuracoes,          name='configuracoes'),

    # ── AGENDAMENTO — ÁREA DO USUÁRIO COMUM ──────────────────────
    path('meus-agendamentos/',  views.meus_agendamentos, name='meus_agendamentos'),
    path('agendamento/novo/',   views.novo_agendamento,  name='novo_agendamento'),

    # ── CONFIGURAÇÕES USUÁRIO COMUM ───────────────────────────────
    path('minha-conta/',        views.configuracoes_usuario, name='configuracoes_usuario'),

    # ── AGENDAMENTO — AÇÕES DA EQUIPE TI ─────────────────────────
    path('agendamento/<int:pk>/aprovar/',   views.aprovar_agendamento,  name='aprovar_agendamento'),
    path('agendamento/<int:pk>/cancelar/',  views.cancelar_agendamento, name='cancelar_agendamento'),
    path('agendamento/<int:pk>/concluir/',  views.concluir_agendamento, name='concluir_agendamento'),
]
