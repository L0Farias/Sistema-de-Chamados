from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # ==================== USUÁRIO COMUM ====================
    path('meus-chamados/', views.usuario_comum, name='usuario_comum'),
    path('chamado/novo/', views.criar_chamado, name='criar_chamado'),
    
    # ==================== EQUIPE TI ====================
    path('equipe-ti/', views.equipe_ti, name='equipe_ti'),
    
    # ==================== CADASTROS ====================
    path('cadastrar-comum/', views.cadastrar_comum, name='cadastrar_comum'),
    path('cadastrar-ti/', views.cadastrar_ti, name='cadastrar_ti'),
    
    # ==================== CHAMADOS ====================
    path('chamado/<int:pk>/', views.detalhe_chamado, name='detalhe_chamado'),
    
    # ==================== AÇÕES DO TI ====================
    path('chamado/<int:pk>/triar/', views.triar_chamado, name='triar_chamado'),
    path('chamado/<int:pk>/iniciar/', views.iniciar_atendimento, name='iniciar_atendimento'),
    path('chamado/<int:pk>/fechar/', views.fechar_chamado, name='fechar_chamado'),
    path('chamado/<int:pk>/reabrir/', views.reabrir_chamado, name='reabrir_chamado'),
    
    # ==================== CHAT ====================
    path('chamado/<int:pk>/mensagem/', views.enviar_mensagem, name='enviar_mensagem'),



    #===================== AJAX =====================
    path('load-more-chamados/', views.load_more_chamados, name='load_more_chamados'),
]


