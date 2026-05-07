from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, UsuarioComumCreationForm, ChamadoForm
from .models import Chamado, MensagemChat


# ====================== PÁGINA INICIAL ======================
def index(request):
    return redirect('login')


# ====================== LOGIN ======================
def login_view(request):
    if request.user.is_authenticated:
        if request.user.tipo == 'ti':
            return redirect('equipe_ti')
        else:
            return redirect('usuario_comum')

    form = LoginForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Bem-vindo, {user.get_full_name() or user.username}!')
                
                if user.tipo == 'ti':
                    return redirect('equipe_ti')
                else:
                    return redirect('usuario_comum')
            else:
                messages.error(request, 'Usuário ou senha incorretos.')
    
    return render(request, 'chamados/login.html', {'form': form})


# ====================== LOGOUT ======================
def logout_view(request):
    logout(request)
    messages.info(request, 'Você saiu do sistema.')
    return redirect('login')


# ====================== CADASTRO USUÁRIO COMUM ======================
def cadastrar_comum(request):
    if request.user.is_authenticated:
        return redirect('index')

    form = UsuarioComumCreationForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Cadastro realizado com sucesso! Agora faça login.')
            return redirect('login')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')

    return render(request, 'chamados/cadastrar_comum.html', {'form': form})


# ====================== CADASTRO USUÁRIO TI ======================
@login_required
def cadastrar_ti(request):
    if request.user.tipo != 'ti':
        messages.error(request, 'Acesso negado. Apenas a equipe TI pode cadastrar novos usuários TI.')
        return redirect('equipe_ti')

    form = UsuarioComumCreationForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.save(commit=False)
            user.tipo = 'ti'
            user.is_staff = True
            user.save()
            messages.success(request, f'Usuário TI "{user.username}" cadastrado com sucesso!')
            return redirect('equipe_ti')
    
    return render(request, 'chamados/cadastrar_ti.html', {'form': form})


# ====================== ÁREA DO USUÁRIO COMUM ======================
@login_required
def usuario_comum(request):
    if request.user.tipo != 'comum':
        return redirect('equipe_ti')
    
    return render(request, 'chamados/usuario_comum.html', {'user': request.user})


# ====================== ÁREA DA EQUIPE TI ======================
@login_required
def equipe_ti(request):
    if request.user.tipo != 'ti':
        return redirect('usuario_comum')
    
    chamados = Chamado.objects.all().order_by('-data_abertura')
    
    # Contagens por status
    count_triagem = chamados.filter(status__in=['Novo', 'Triagem']).count()
    count_atendimento = chamados.filter(status='Em Atendimento').count()
    count_concluido = chamados.filter(status='Fechado').count()

    return render(request, 'chamados/equipe_ti.html', {
        'user': request.user,
        'chamados': chamados,
        'count_triagem': count_triagem,
        'count_atendimento': count_atendimento,
        'count_concluido': count_concluido,
    })

# ====================== ABRIR NOVO CHAMADO ======================
@login_required
def criar_chamado(request):
    if request.user.tipo != 'comum':
        return redirect('equipe_ti')

    form = ChamadoForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            chamado = form.save(commit=False)
            chamado.nome_usuario = request.user
            chamado.save()
            messages.success(request, f'Chamado #{chamado.id} aberto com sucesso!')
            return redirect('usuario_comum')
    
    return render(request, 'chamados/criar_chamado.html', {
        'form': form,
        'user': request.user
    })


# ====================== DETALHES DO CHAMADO ======================
@login_required
def detalhe_chamado(request, pk):
    chamado = get_object_or_404(Chamado, pk=pk)
    
    # Segurança: Usuário comum só vê seus próprios chamados
    if request.user.tipo == 'comum' and chamado.nome_usuario != request.user:
        messages.error(request, 'Você não tem permissão para visualizar este chamado.')
        return redirect('usuario_comum')

    mensagens = chamado.mensagens.all()

    return render(request, 'chamados/detalhe_chamado.html', {
        'chamado': chamado,
        'mensagens': mensagens,
        'user': request.user,
    })

# ====================== AÇÕES DO TI ======================
@login_required
def triar_chamado(request, pk):
    if request.user.tipo != 'ti':
        messages.error(request, 'Acesso negado.')
        return redirect('login')
    
    chamado = get_object_or_404(Chamado, pk=pk)
    chamado.status = 'Triagem'
    chamado.atendente = request.user
    chamado.save()
    messages.success(request, f'Chamado #{pk} enviado para Triagem.')
    return redirect('equipe_ti')


@login_required
def iniciar_atendimento(request, pk):
    if request.user.tipo != 'ti':
        messages.error(request, 'Acesso negado.')
        return redirect('login')
    
    chamado = get_object_or_404(Chamado, pk=pk)
    chamado.status = 'Em Atendimento'
    chamado.atendente = request.user
    chamado.save()
    messages.success(request, f'Atendimento do chamado #{pk} iniciado.')
    return redirect('equipe_ti')


@login_required
def fechar_chamado(request, pk):
    if request.user.tipo != 'ti':
        messages.error(request, 'Acesso negado.')
        return redirect('login')
    
    chamado = get_object_or_404(Chamado, pk=pk)
    chamado.status = 'Fechado'
    chamado.save()
    messages.success(request, f'Chamado #{pk} fechado com sucesso.')
    return redirect('equipe_ti')


@login_required
def reabrir_chamado(request, pk):
    if request.user.tipo != 'ti':
        messages.error(request, 'Acesso negado.')
        return redirect('login')
    
    chamado = get_object_or_404(Chamado, pk=pk)
    chamado.status = 'Novo'
    chamado.atendente = None
    chamado.save()
    messages.success(request, f'Chamado #{pk} reaberto.')
    return redirect('equipe_ti')


# ====================== ENVIAR MENSAGEM NO CHAT ======================
@login_required
def enviar_mensagem(request, pk):
    chamado = get_object_or_404(Chamado, pk=pk)
    mensagem_texto = request.POST.get('mensagem')

    if mensagem_texto and mensagem_texto.strip():
        MensagemChat.objects.create(
            chamado=chamado,
            autor=request.user,
            mensagem=mensagem_texto.strip()
        )
        messages.success(request, 'Mensagem enviada!')
    
    return redirect('detalhe_chamado', pk=pk)

#=====================AJAX======================
from django.http import JsonResponse
from django.core.paginator import Paginator

@login_required
def load_more_chamados(request):
    status = request.GET.get('status')
    page = int(request.GET.get('page', 1))
    per_page = 10  # Quantidade por carregamento

    chamados = Chamado.objects.filter(status=status).order_by('-data_abertura')
    
    paginator = Paginator(chamados, per_page)
    page_obj = paginator.get_page(page)

    data = {
        'chamados': [
            {
                'id': c.id,
                'nome_usuario': str(c.nome_usuario),
                'local': c.local,
                'categoria': c.categoria,
                'tipo': c.get_tipo_display(),
                'status': c.status,
                'data_abertura': c.data_abertura.strftime("%d/%m/%Y %H:%M"),
            } for c in page_obj
        ],
        'has_next': page_obj.has_next()
    }

    return JsonResponse(data)