from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
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

    meus_chamados = Chamado.objects.filter(
        nome_usuario=request.user
    ).order_by('-data_abertura')

    return render(request, 'chamados/usuario_comum.html', {
        'user': request.user,
        'meus_chamados': meus_chamados,
    })


# ====================== ÁREA DA EQUIPE TI ======================
@login_required
def equipe_ti(request):
    if request.user.tipo != 'ti':
        return redirect('usuario_comum')

    chamados = Chamado.objects.select_related(
        'nome_usuario', 'atendente'
    ).all().order_by('-data_abertura')
    
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
@require_POST
def triar_chamado(request, pk):
    if request.user.tipo != 'ti':
        messages.error(request, 'Acesso negado.')
        return redirect('login')

    chamado = get_object_or_404(Chamado, pk=pk)
    chamado.status = 'Triagem'
    chamado.atendente = request.user
    chamado.data_triagem = timezone.now()
    chamado.save()
    messages.success(request, f'Chamado #{pk} enviado para Triagem.')
    return redirect('equipe_ti')


@login_required
@require_POST
def iniciar_atendimento(request, pk):
    if request.user.tipo != 'ti':
        messages.error(request, 'Acesso negado.')
        return redirect('login')

    chamado = get_object_or_404(Chamado, pk=pk)
    chamado.status = 'Em Atendimento'
    chamado.atendente = request.user
    chamado.data_atendimento = timezone.now()
    chamado.save()
    messages.success(request, f'Atendimento do chamado #{pk} iniciado.')
    return redirect('equipe_ti')


@login_required
@require_POST
def fechar_chamado(request, pk):
    if request.user.tipo != 'ti':
        messages.error(request, 'Acesso negado.')
        return redirect('login')

    chamado = get_object_or_404(Chamado, pk=pk)
    chamado.status = 'Fechado'
    chamado.data_fechamento = timezone.now()
    chamado.save()
    messages.success(request, f'Chamado #{pk} fechado com sucesso.')
    return redirect('equipe_ti')


@login_required
@require_POST
def reabrir_chamado(request, pk):
    if request.user.tipo != 'ti':
        messages.error(request, 'Acesso negado.')
        return redirect('login')

    chamado = get_object_or_404(Chamado, pk=pk)
    chamado.status = 'Novo'
    chamado.atendente = None
    chamado.data_triagem = None
    chamado.data_atendimento = None
    chamado.data_fechamento = None
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

#=====================Relatorios======================
@login_required
def relatorios(request):
    if request.user.tipo != 'ti':
        messages.error(request, 'Acesso negado.')
        return redirect('usuario_comum')

    from .models import Usuario as Usr
    atendentes = Usr.objects.filter(tipo='ti').order_by('username')
    etiqueta_choices = [c[0] for c in Chamado.ETIQUETA_CHOICES]
    status_choices   = [c[0] for c in Chamado.STATUS_CHOICES]

    return render(request, 'chamados/relatorios.html', {
        'user': request.user,
        'atendentes': atendentes,
        'etiqueta_choices': etiqueta_choices,
        'status_choices': status_choices,
    })


@login_required
def relatorios_ajax(request):
    """Endpoint AJAX para listagem filtrada de chamados."""
    if request.user.tipo != 'ti':
        return JsonResponse({'error': 'Acesso negado'}, status=403)

    qs = Chamado.objects.select_related('nome_usuario', 'atendente').all()

    # Filtros
    etiqueta   = request.GET.get('etiqueta', '').strip()
    status     = request.GET.get('status', '').strip()
    atendente  = request.GET.get('atendente', '').strip()
    data_ini   = request.GET.get('data_ini', '').strip()
    data_fim   = request.GET.get('data_fim', '').strip()
    busca      = request.GET.get('busca', '').strip()

    if etiqueta:
        qs = qs.filter(etiqueta=etiqueta)
    if status:
        qs = qs.filter(status=status)
    if atendente:
        qs = qs.filter(atendente__username=atendente)
    if data_ini:
        qs = qs.filter(data_abertura__date__gte=data_ini)
    if data_fim:
        qs = qs.filter(data_abertura__date__lte=data_fim)
    if busca:
        from django.db.models import Q
        qs = qs.filter(
            Q(id__icontains=busca) |
            Q(nome_usuario__username__icontains=busca) |
            Q(nome_usuario__first_name__icontains=busca) |
            Q(nome_usuario__last_name__icontains=busca) |
            Q(problema__icontains=busca)
        )

    page     = int(request.GET.get('page', 1))
    per_page = 20
    paginator = Paginator(qs.order_by('-data_abertura'), per_page)
    page_obj  = paginator.get_page(page)

    rows = []
    for c in page_obj:
        rows.append({
            'id':             c.id,
            'solicitante':    c.nome_usuario.get_full_name() or c.nome_usuario.username,
            'local':          c.local,
            'categoria':      c.categoria,
            'etiqueta':       c.etiqueta,
            'status':         c.status,
            'data_abertura':  c.data_abertura.strftime('%d/%m/%Y %H:%M'),
            'data_fechamento': c.data_fechamento.strftime('%d/%m/%Y %H:%M') if c.data_fechamento else '—',
            'atendente':      c.atendente.username if c.atendente else '—',
        })

    return JsonResponse({
        'chamados':   rows,
        'total':      paginator.count,
        'num_pages':  paginator.num_pages,
        'page':       page_obj.number,
        'has_next':   page_obj.has_next(),
        'has_prev':   page_obj.has_previous(),
    })


@login_required
def relatorios_dashboard(request):
    """Dados para os gráficos Chart.js."""
    if request.user.tipo != 'ti':
        return JsonResponse({'error': 'Acesso negado'}, status=403)

    from django.db.models import Count
    from .models import Usuario as Usr

    por_etiqueta = dict(
        Chamado.objects.values_list('etiqueta').annotate(total=Count('id'))
    )
    por_status = dict(
        Chamado.objects.values_list('status').annotate(total=Count('id'))
    )
    por_atendente_qs = (
        Chamado.objects
        .filter(atendente__isnull=False)
        .values('atendente__username')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    por_atendente = {r['atendente__username']: r['total'] for r in por_atendente_qs}

    return JsonResponse({
        'por_etiqueta': por_etiqueta,
        'por_status':   por_status,
        'por_atendente': por_atendente,
    })


@login_required
def relatorios_exportar(request):
    """Exporta chamados filtrados para Excel usando openpyxl."""
    if request.user.tipo != 'ti':
        return JsonResponse({'error': 'Acesso negado'}, status=403)

    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    from django.http import HttpResponse
    from datetime import date

    qs = Chamado.objects.select_related('nome_usuario', 'atendente').all()

    etiqueta  = request.GET.get('etiqueta', '').strip()
    status    = request.GET.get('status', '').strip()
    atendente = request.GET.get('atendente', '').strip()
    data_ini  = request.GET.get('data_ini', '').strip()
    data_fim  = request.GET.get('data_fim', '').strip()
    busca     = request.GET.get('busca', '').strip()

    if etiqueta:
        qs = qs.filter(etiqueta=etiqueta)
    if status:
        qs = qs.filter(status=status)
    if atendente:
        qs = qs.filter(atendente__username=atendente)
    if data_ini:
        qs = qs.filter(data_abertura__date__gte=data_ini)
    if data_fim:
        qs = qs.filter(data_abertura__date__lte=data_fim)
    if busca:
        from django.db.models import Q
        qs = qs.filter(
            Q(id__icontains=busca) |
            Q(nome_usuario__username__icontains=busca) |
            Q(problema__icontains=busca)
        )

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Chamados'

    cabecalho = ['ID', 'Solicitante', 'Local', 'Categoria', 'Etiqueta',
                 'Descrição', 'Status', 'Data Abertura', 'Data Fechamento', 'Atendente']

    header_fill = PatternFill('solid', fgColor='1E40AF')
    header_font = Font(bold=True, color='FFFFFF')

    for col, titulo in enumerate(cabecalho, start=1):
        cell = ws.cell(row=1, column=col, value=titulo)
        cell.fill   = header_fill
        cell.font   = header_font
        cell.alignment = Alignment(horizontal='center')

    for row_idx, c in enumerate(qs.order_by('-data_abertura'), start=2):
        ws.cell(row=row_idx, column=1,  value=c.id)
        ws.cell(row=row_idx, column=2,  value=c.nome_usuario.get_full_name() or c.nome_usuario.username)
        ws.cell(row=row_idx, column=3,  value=c.local)
        ws.cell(row=row_idx, column=4,  value=c.categoria)
        ws.cell(row=row_idx, column=5,  value=c.etiqueta)
        ws.cell(row=row_idx, column=6,  value=c.problema)
        ws.cell(row=row_idx, column=7,  value=c.status)
        ws.cell(row=row_idx, column=8,  value=c.data_abertura.strftime('%d/%m/%Y %H:%M'))
        ws.cell(row=row_idx, column=9,  value=c.data_fechamento.strftime('%d/%m/%Y %H:%M') if c.data_fechamento else '')
        ws.cell(row=row_idx, column=10, value=c.atendente.username if c.atendente else '')

    # Auto ajuste de colunas
    for col in ws.columns:
        max_len = max((len(str(cell.value or '')) for cell in col), default=0)
        ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 50)

    filename = f'relatorio_chamados_{date.today().strftime("%Y_%m_%d")}.xlsx'
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    wb.save(response)
    return response

@login_required
def detalhe_chamado_ajax(request, pk):
    chamado = get_object_or_404(Chamado, pk=pk)
    
    # Segurança
    if request.user.tipo == 'comum' and chamado.nome_usuario != request.user:
        return JsonResponse({'error': 'Acesso negado'}, status=403)

    data = {
        'id': chamado.id,
        'problema': chamado.problema,
        'nome_usuario': str(chamado.nome_usuario),
        'local': chamado.local,
        'categoria': chamado.categoria,
        'tipo': chamado.get_tipo_display(),
        'etiqueta': chamado.etiqueta,
        'status': chamado.status,
        'data_abertura': chamado.data_abertura.strftime("%d/%m/%Y %H:%M"),
        'atendente': str(chamado.atendente) if chamado.atendente else 'Não atribuído',
    }
    
    return JsonResponse(data)