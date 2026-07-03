import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from .forms import LoginForm, UsuarioComumCreationForm, ChamadoForm, AgendamentoMultimidiaForm
from .models import Chamado, MensagemChat, Etiqueta, HistoricoEtiqueta, AgendamentoMultimidia


# ──────────────────────────────────────────
#  AUTENTICAÇÃO
# ──────────────────────────────────────────

def index(request):
    return redirect('login')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('equipe_ti' if request.user.tipo == 'ti' else 'usuario_comum')

    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password'],
        )
        if user:
            login(request, user)
            messages.success(request, f'Bem-vindo, {user.get_full_name() or user.username}!')
            return redirect('equipe_ti' if user.tipo == 'ti' else 'usuario_comum')
        messages.error(request, 'Usuário ou senha incorretos.')

    return render(request, 'chamados/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Você saiu do sistema.')
    return redirect('login')


# ──────────────────────────────────────────
#  CADASTROS
# ──────────────────────────────────────────

def cadastrar_comum(request):
    if request.user.is_authenticated:
        return redirect('index')
    form = UsuarioComumCreationForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Cadastro realizado! Faça login.')
            return redirect('login')
        messages.error(request, 'Corrija os erros abaixo.')
    return render(request, 'chamados/cadastrar_comum.html', {'form': form})


@login_required
def cadastrar_ti(request):
    if request.user.tipo != 'ti':
        messages.error(request, 'Acesso negado.')
        return redirect('equipe_ti')
    form = UsuarioComumCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.tipo = 'ti'
        user.is_staff = True
        user.save()
        messages.success(request, f'Usuário TI "{user.username}" cadastrado!')
        return redirect('equipe_ti')
    return render(request, 'chamados/cadastrar_ti.html', {'form': form})


# ──────────────────────────────────────────
#  ÁREA DO USUÁRIO COMUM
# ──────────────────────────────────────────

@login_required
def usuario_comum(request):
    if request.user.tipo != 'comum':
        return redirect('equipe_ti')
    meus_chamados = (
        Chamado.objects
        .filter(nome_usuario=request.user)
        .prefetch_related('etiquetas')
        .order_by('-data_abertura')
    )
    return render(request, 'chamados/usuario_comum.html', {
        'user': request.user,
        'meus_chamados': meus_chamados,
    })


# ──────────────────────────────────────────
#  KANBAN
# ──────────────────────────────────────────

@login_required
def equipe_ti(request):
    if request.user.tipo != 'ti':
        return redirect('usuario_comum')
    chamados = (
        Chamado.objects
        .select_related('nome_usuario', 'atendente')
        .prefetch_related('etiquetas')
        .order_by('-data_abertura')
    )
    return render(request, 'chamados/equipe_ti.html', {
        'user': request.user,
        'chamados': chamados,
        'count_triagem':    chamados.filter(status__in=['Novo', 'Triagem']).count(),
        'count_atendimento': chamados.filter(status='Em Atendimento').count(),
        'count_concluido':  chamados.filter(status='Fechado').count(),
    })


# ──────────────────────────────────────────
#  CHAMADOS
# ──────────────────────────────────────────

@login_required
def criar_chamado(request):
    if request.user.tipo != 'comum':
        return redirect('equipe_ti')
    form = ChamadoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        chamado = form.save(commit=False)
        chamado.nome_usuario = request.user
        chamado.save()
        messages.success(request, f'Chamado #{chamado.id} aberto com sucesso!')
        return redirect('usuario_comum')
    return render(request, 'chamados/criar_chamado.html', {'form': form, 'user': request.user})


@login_required
def detalhe_chamado(request, pk):
    chamado = get_object_or_404(Chamado, pk=pk)
    if request.user.tipo == 'comum' and chamado.nome_usuario != request.user:
        messages.error(request, 'Sem permissão.')
        return redirect('usuario_comum')
    return render(request, 'chamados/detalhe_chamado.html', {
        'chamado': chamado,
        'mensagens': chamado.mensagens.all(),
        'user': request.user,
    })


# ──────────────────────────────────────────
#  AÇÕES DO TI (transições de status)
# ──────────────────────────────────────────

@login_required
@require_POST
def triar_chamado(request, pk):
    if request.user.tipo != 'ti':
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    chamado = get_object_or_404(Chamado, pk=pk)
    chamado.status = 'Triagem'
    chamado.atendente = request.user
    chamado.data_triagem = timezone.now()
    chamado.save()
    messages.success(request, f'Chamado #{pk} em Triagem.')
    return redirect('equipe_ti')


@login_required
@require_POST
def iniciar_atendimento(request, pk):
    if request.user.tipo != 'ti':
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    chamado = get_object_or_404(Chamado, pk=pk)
    chamado.status = 'Em Atendimento'
    chamado.atendente = request.user
    chamado.data_atendimento = timezone.now()
    chamado.save()
    messages.success(request, f'Chamado #{pk} em atendimento.')
    return redirect('equipe_ti')


@login_required
@require_POST
def fechar_chamado(request, pk):
    if request.user.tipo != 'ti':
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    chamado = get_object_or_404(Chamado, pk=pk)
    chamado.status = 'Fechado'
    chamado.data_fechamento = timezone.now()
    chamado.atendente_fechamento = request.user
    chamado.save()
    messages.success(request, f'Chamado #{pk} fechado.')
    return redirect('equipe_ti')


@login_required
@require_POST
def reabrir_chamado(request, pk):
    if request.user.tipo != 'ti':
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    chamado = get_object_or_404(Chamado, pk=pk)
    chamado.status = 'Novo'
    chamado.atendente = None
    chamado.data_triagem = None
    chamado.data_atendimento = None
    chamado.data_fechamento = None
    chamado.data_reabertura = timezone.now()
    chamado.reaberto_por = request.user
    chamado.save()
    messages.success(request, f'Chamado #{pk} reaberto.')
    return redirect('equipe_ti')


# ──────────────────────────────────────────
#  CHAT
# ──────────────────────────────────────────

@login_required
def enviar_mensagem(request, pk):
    chamado = get_object_or_404(Chamado, pk=pk)
    texto = request.POST.get('mensagem', '').strip()
    if texto:
        MensagemChat.objects.create(chamado=chamado, autor=request.user, mensagem=texto)
        messages.success(request, 'Mensagem enviada!')
    return redirect('detalhe_chamado', pk=pk)


# ──────────────────────────────────────────
#  AJAX — DETALHE DO CHAMADO
# ──────────────────────────────────────────

@login_required
def detalhe_chamado_ajax(request, pk):
    chamado = get_object_or_404(
        Chamado.objects.select_related(
            'nome_usuario', 'atendente', 'atendente_fechamento', 'reaberto_por'
        ).prefetch_related('etiquetas', 'historico_etiquetas__etiqueta', 'historico_etiquetas__usuario'),
        pk=pk
    )
    if request.user.tipo == 'comum' and chamado.nome_usuario != request.user:
        return JsonResponse({'error': 'Acesso negado'}, status=403)

    etiquetas = [
        {'id': e.id, 'nome': e.nome, 'cor': e.cor}
        for e in chamado.etiquetas.filter(ativa=True)
    ]

    historico = []
    for h in chamado.historico_etiquetas.select_related('etiqueta', 'usuario').order_by('data'):
        historico.append({
            'tipo':     'etiqueta',
            'acao':     h.acao,
            'etiqueta': h.etiqueta.nome,
            'cor':      h.etiqueta.cor,
            'usuario':  h.usuario.get_full_name() or h.usuario.username,
            'data':     h.data.strftime('%d/%m/%Y %H:%M'),
        })

    return JsonResponse({
        'id':                  chamado.id,
        'problema':            chamado.problema,
        'nome_usuario':        chamado.nome_usuario.get_full_name() or chamado.nome_usuario.username,
        'local':               chamado.local,
        'categoria':           chamado.categoria,
        'tipo':                chamado.get_tipo_display(),
        'status':              chamado.status,
        'data_abertura':       chamado.data_abertura.strftime('%d/%m/%Y %H:%M'),
        'atendente':           chamado.atendente.get_full_name() or chamado.atendente.username if chamado.atendente else None,
        'data_fechamento':     chamado.data_fechamento.strftime('%d/%m/%Y %H:%M') if chamado.data_fechamento else None,
        'atendente_fechamento': chamado.atendente_fechamento.get_full_name() or chamado.atendente_fechamento.username if chamado.atendente_fechamento else None,
        'data_reabertura':     chamado.data_reabertura.strftime('%d/%m/%Y %H:%M') if chamado.data_reabertura else None,
        'reaberto_por':        chamado.reaberto_por.get_full_name() or chamado.reaberto_por.username if chamado.reaberto_por else None,
        'etiquetas':           etiquetas,
        'historico_etiquetas': historico,
    })


# ──────────────────────────────────────────
#  AJAX — ETIQUETAS
# ──────────────────────────────────────────

@login_required
def etiquetas_chamado(request, pk):
    """GET: retorna todas as etiquetas ativas + ids já associadas ao chamado."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Não autenticado'}, status=403)
    chamado = get_object_or_404(Chamado, pk=pk)
    todas = list(Etiqueta.objects.filter(ativa=True).values('id', 'nome', 'cor'))
    selecionadas = list(chamado.etiquetas.values_list('id', flat=True))
    return JsonResponse({'todas': todas, 'selecionadas': selecionadas})


@login_required
@require_POST
def salvar_etiquetas_chamado(request, pk):
    """POST: salva o conjunto de etiquetas do chamado e registra histórico agrupado."""
    if request.user.tipo != 'ti':
        return JsonResponse({'error': 'Acesso negado'}, status=403)

    chamado = get_object_or_404(Chamado, pk=pk)

    try:
        body = json.loads(request.body)
        novos_ids = set(int(i) for i in body.get('etiqueta_ids', []))
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Dados inválidos'}, status=400)

    atuais_ids = set(chamado.etiquetas.values_list('id', flat=True))
    adicionadas_ids = novos_ids - atuais_ids
    removidas_ids   = atuais_ids - novos_ids

    # Buscar objetos de uma vez
    etiquetas_add = list(Etiqueta.objects.filter(pk__in=adicionadas_ids, ativa=True))
    etiquetas_rem = list(Etiqueta.objects.filter(pk__in=removidas_ids))

    # Aplicar mudanças no M2M
    for et in etiquetas_add:
        chamado.etiquetas.add(et)
    for et in etiquetas_rem:
        chamado.etiquetas.remove(et)

    usuario = request.user

    # Histórico agrupado — adicionadas
    if etiquetas_add:
        if len(etiquetas_add) == 1:
            HistoricoEtiqueta.objects.create(
                chamado=chamado, etiqueta=etiquetas_add[0],
                acao='adicionada', usuario=usuario
            )
        else:
            for et in etiquetas_add:
                HistoricoEtiqueta.objects.create(
                    chamado=chamado, etiqueta=et,
                    acao='adicionada', usuario=usuario
                )

    # Histórico agrupado — removidas
    if etiquetas_rem:
        if not novos_ids and atuais_ids:
            # Limpeza total — registra para cada etiqueta removida
            for et in etiquetas_rem:
                HistoricoEtiqueta.objects.create(
                    chamado=chamado, etiqueta=et,
                    acao='removida', usuario=usuario
                )
        else:
            for et in etiquetas_rem:
                HistoricoEtiqueta.objects.create(
                    chamado=chamado, etiqueta=et,
                    acao='removida', usuario=usuario
                )

    etiquetas_atuais = [
        {'id': e.id, 'nome': e.nome, 'cor': e.cor}
        for e in chamado.etiquetas.filter(ativa=True)
    ]

    # Histórico completo para atualizar timeline no front
    historico_raw = list(
        chamado.historico_etiquetas
        .select_related('etiqueta', 'usuario')
        .order_by('data')
        .values('acao', 'etiqueta__nome', 'etiqueta__cor',
                'usuario__first_name', 'usuario__last_name', 'usuario__username', 'data')
    )
    historico = []
    for h in historico_raw:
        nome_usuario = (
            f"{h['usuario__first_name']} {h['usuario__last_name']}".strip()
            or h['usuario__username']
        )
        historico.append({
            'tipo':     'etiqueta',
            'acao':     h['acao'],
            'etiqueta': h['etiqueta__nome'],
            'cor':      h['etiqueta__cor'],
            'usuario':  nome_usuario,
            'data':     h['data'].strftime('%d/%m/%Y %H:%M'),
        })

    return JsonResponse({
        'success':            True,
        'etiquetas':          etiquetas_atuais,
        'historico_etiquetas': historico,
    })


# ──────────────────────────────────────────
#  AJAX — PAGINAÇÃO KANBAN
# ──────────────────────────────────────────

@login_required
def load_more_chamados(request):
    status   = request.GET.get('status')
    page     = int(request.GET.get('page', 1))
    per_page = 10
    chamados = Chamado.objects.filter(status=status).order_by('-data_abertura')
    paginator = Paginator(chamados, per_page)
    page_obj  = paginator.get_page(page)
    data = {
        'chamados': [
            {
                'id':           c.id,
                'nome_usuario': str(c.nome_usuario),
                'local':        c.local,
                'categoria':    c.categoria,
                'tipo':         c.get_tipo_display(),
                'status':       c.status,
                'data_abertura': c.data_abertura.strftime('%d/%m/%Y %H:%M'),
            } for c in page_obj
        ],
        'has_next': page_obj.has_next(),
    }
    return JsonResponse(data)


# ──────────────────────────────────────────
#  AJAX — POLLING DO KANBAN
# ──────────────────────────────────────────

@login_required
def kanban_polling(request):
    """
    Retorna chamados alterados desde `since` (ISO timestamp ou ID).
    O frontend envia ?since=<timestamp_iso> e recebe somente mudanças.
    """
    if request.user.tipo != 'ti':
        return JsonResponse({'error': 'Acesso negado'}, status=403)

    since_str = request.GET.get('since', '')
    qs = (
        Chamado.objects
        .select_related('nome_usuario', 'atendente')
        .prefetch_related('etiquetas')
        .order_by('-data_abertura')
    )

    if since_str:
        from datetime import datetime
        try:
            # Aceita ISO 8601 enviado pelo JS (Date.toISOString)
            since_dt = datetime.fromisoformat(since_str.replace('Z', '+00:00'))
            qs = qs.filter(data_abertura__gt=since_dt) | qs.filter(data_atendimento__gt=since_dt) | qs.filter(data_fechamento__gt=since_dt) | qs.filter(data_reabertura__gt=since_dt) | qs.filter(data_triagem__gt=since_dt)
            qs = qs.distinct()
        except (ValueError, AttributeError):
            pass

    chamados_data = []
    for c in qs:
        chamados_data.append({
            'id':            c.id,
            'status':        c.status,
            'nome_usuario':  c.nome_usuario.get_full_name() or c.nome_usuario.username,
            'local':         c.local,
            'categoria':     c.categoria,
            'problema':      c.problema,
            'data_abertura': c.data_abertura.strftime('%d/%m/%Y %H:%M'),
            'etiquetas':     [{'nome': e.nome, 'cor': e.cor} for e in c.etiquetas.all()],
        })

    # Contadores sempre atualizados
    todos = Chamado.objects
    contadores = {
        'triagem':     todos.filter(status__in=['Novo', 'Triagem']).count(),
        'atendimento': todos.filter(status='Em Atendimento').count(),
        'concluido':   todos.filter(status='Fechado').count(),
    }

    from django.utils.timezone import now
    return JsonResponse({
        'chamados':   chamados_data,
        'contadores': contadores,
        'timestamp':  now().isoformat(),
    })


# ──────────────────────────────────────────
#  RELATÓRIOS
# ──────────────────────────────────────────

@login_required
def relatorios(request):
    if request.user.tipo != 'ti':
        messages.error(request, 'Acesso negado.')
        return redirect('usuario_comum')
    from .models import Usuario as Usr
    atendentes     = Usr.objects.filter(tipo='ti').order_by('username')
    etiquetas_list = Etiqueta.objects.filter(ativa=True).order_by('nome')
    status_choices = [c[0] for c in Chamado.STATUS_CHOICES]
    return render(request, 'chamados/relatorios.html', {
        'user':            request.user,
        'atendentes':      atendentes,
        'etiquetas_list':  etiquetas_list,
        'status_choices':  status_choices,
    })


@login_required
def relatorios_ajax(request):
    if request.user.tipo != 'ti':
        return JsonResponse({'error': 'Acesso negado'}, status=403)

    qs = Chamado.objects.select_related('nome_usuario', 'atendente').prefetch_related('etiquetas')

    etiqueta_id = request.GET.get('etiqueta', '').strip()
    status      = request.GET.get('status', '').strip()
    atendente   = request.GET.get('atendente', '').strip()
    data_ini    = request.GET.get('data_ini', '').strip()
    data_fim    = request.GET.get('data_fim', '').strip()
    busca       = request.GET.get('busca', '').strip()

    if etiqueta_id:
        qs = qs.filter(etiquetas__id=etiqueta_id)
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

    qs = qs.distinct()
    page      = int(request.GET.get('page', 1))
    paginator = Paginator(qs.order_by('-data_abertura'), 20)
    page_obj  = paginator.get_page(page)

    rows = []
    for c in page_obj:
        etiquetas_nomes = ', '.join(c.etiquetas.values_list('nome', flat=True))
        rows.append({
            'id':              c.id,
            'solicitante':     c.nome_usuario.get_full_name() or c.nome_usuario.username,
            'local':           c.local,
            'categoria':       c.categoria,
            'etiqueta':        etiquetas_nomes or '—',
            'status':          c.status,
            'data_abertura':   c.data_abertura.strftime('%d/%m/%Y %H:%M'),
            'data_fechamento': c.data_fechamento.strftime('%d/%m/%Y %H:%M') if c.data_fechamento else '—',
            'atendente':       c.atendente.username if c.atendente else '—',
        })

    return JsonResponse({
        'chamados':  rows,
        'total':     paginator.count,
        'num_pages': paginator.num_pages,
        'page':      page_obj.number,
        'has_next':  page_obj.has_next(),
        'has_prev':  page_obj.has_previous(),
    })


@login_required
def relatorios_dashboard(request):
    if request.user.tipo != 'ti':
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    from django.db.models import Count

    por_etiqueta = {}
    for e in Etiqueta.objects.annotate(total=Count('chamados')):
        por_etiqueta[e.nome] = e.total

    por_status = dict(
        Chamado.objects.values_list('status').annotate(total=Count('id'))
    )
    por_atendente = {
        r['atendente__username']: r['total']
        for r in Chamado.objects
        .filter(atendente__isnull=False)
        .values('atendente__username')
        .annotate(total=Count('id'))
        .order_by('-total')
    }
    return JsonResponse({
        'por_etiqueta':  por_etiqueta,
        'por_status':    por_status,
        'por_atendente': por_atendente,
    })


@login_required
def relatorios_exportar(request):
    if request.user.tipo != 'ti':
        return JsonResponse({'error': 'Acesso negado'}, status=403)

    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    from django.http import HttpResponse
    from datetime import date

    qs = Chamado.objects.select_related('nome_usuario', 'atendente').prefetch_related('etiquetas')

    etiqueta_id = request.GET.get('etiqueta', '').strip()
    status      = request.GET.get('status', '').strip()
    atendente   = request.GET.get('atendente', '').strip()
    data_ini    = request.GET.get('data_ini', '').strip()
    data_fim    = request.GET.get('data_fim', '').strip()
    busca       = request.GET.get('busca', '').strip()

    if etiqueta_id:
        qs = qs.filter(etiquetas__id=etiqueta_id)
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
        qs = qs.filter(Q(id__icontains=busca) | Q(nome_usuario__username__icontains=busca) | Q(problema__icontains=busca))

    qs = qs.distinct()
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Chamados'
    cabecalho   = ['ID','Solicitante','Local','Categoria','Etiquetas','Descrição','Status','Data Abertura','Data Fechamento','Atendente']
    header_fill = PatternFill('solid', fgColor='1E40AF')
    header_font = Font(bold=True, color='FFFFFF')
    for col, titulo in enumerate(cabecalho, 1):
        cell = ws.cell(row=1, column=col, value=titulo)
        cell.fill      = header_fill
        cell.font      = header_font
        cell.alignment = Alignment(horizontal='center')
    for row_idx, c in enumerate(qs.order_by('-data_abertura'), 2):
        etiquetas_str = ', '.join(c.etiquetas.values_list('nome', flat=True))
        ws.cell(row=row_idx, column=1,  value=c.id)
        ws.cell(row=row_idx, column=2,  value=c.nome_usuario.get_full_name() or c.nome_usuario.username)
        ws.cell(row=row_idx, column=3,  value=c.local)
        ws.cell(row=row_idx, column=4,  value=c.categoria)
        ws.cell(row=row_idx, column=5,  value=etiquetas_str)
        ws.cell(row=row_idx, column=6,  value=c.problema)
        ws.cell(row=row_idx, column=7,  value=c.status)
        ws.cell(row=row_idx, column=8,  value=c.data_abertura.strftime('%d/%m/%Y %H:%M'))
        ws.cell(row=row_idx, column=9,  value=c.data_fechamento.strftime('%d/%m/%Y %H:%M') if c.data_fechamento else '')
        ws.cell(row=row_idx, column=10, value=c.atendente.username if c.atendente else '')
    for col in ws.columns:
        ws.column_dimensions[col[0].column_letter].width = min(
            max(len(str(cell.value or '')) for cell in col) + 4, 50
        )
    filename = f'relatorio_chamados_{date.today().strftime("%Y_%m_%d")}.xlsx'
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    wb.save(response)
    return response


# ──────────────────────────────────────────
#  DASHBOARD
# ──────────────────────────────────────────

@login_required
def dashboard(request):
    """Página de Dashboard — KPIs e gráficos gerenciais."""
    if request.user.tipo != 'ti':
        messages.error(request, 'Acesso negado.')
        return redirect('usuario_comum')

    total_abertos     = Chamado.objects.exclude(status='Fechado').count()
    total_triagem     = Chamado.objects.filter(status__in=['Novo', 'Triagem']).count()
    total_atendimento = Chamado.objects.filter(status='Em Atendimento').count()
    total_fechados    = Chamado.objects.filter(status='Fechado').count()

    return render(request, 'chamados/dashboard.html', {
        'user':              request.user,
        'total_abertos':     total_abertos,
        'total_triagem':     total_triagem,
        'total_atendimento': total_atendimento,
        'total_fechados':    total_fechados,
    })


# ──────────────────────────────────────────
#  AGENDAMENTO DE MULTIMÍDIA
# ──────────────────────────────────────────

@login_required
def agendamento_multimidia(request):
    """Página de agendamento de equipamentos multimídia."""
    form = AgendamentoMultimidiaForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        cd = form.cleaned_data
        AgendamentoMultimidia.objects.create(
            solicitante    = request.user,
            setor          = cd['setor'],
            local          = cd['local'],
            sala           = cd.get('sala', ''),
            data           = cd['data'],
            horario_inicio = cd['horario_inicio'],
            horario_fim    = cd['horario_fim'],
            equipamentos   = cd['equipamentos'],
            finalidade     = cd.get('finalidade', ''),
            observacoes    = cd.get('observacoes', ''),
            status         = 'Pendente',
        )
        messages.success(request, 'Agendamento enviado com sucesso! Aguarde aprovação.')
        return redirect('agendamento_multimidia')

    # Listagem: TI vê todos; comum vê só os seus
    if request.user.tipo == 'ti':
        base_qs = AgendamentoMultimidia.objects.select_related('solicitante').order_by('-data', 'horario_inicio')
    else:
        base_qs = AgendamentoMultimidia.objects.filter(solicitante=request.user).order_by('-data', 'horario_inicio')

    agendamentos_pendentes  = base_qs.exclude(status='Concluído')
    agendamentos_concluidos = base_qs.filter(status='Concluído')

    return render(request, 'chamados/agendamento_multimidia.html', {
        'user':                   request.user,
        'form':                   form,
        'agendamentos_pendentes':  agendamentos_pendentes,
        'agendamentos_concluidos': agendamentos_concluidos,
    })


# ──────────────────────────────────────────
#  CONFIGURAÇÕES (placeholder)
# ──────────────────────────────────────────

@login_required
def configuracoes(request):
    """Placeholder — expansão futura."""
    if request.user.tipo != 'ti':
        messages.error(request, 'Acesso negado.')
        return redirect('usuario_comum')
    return render(request, 'chamados/configuracoes.html', {'user': request.user})


# ──────────────────────────────────────────
#  AGENDAMENTO — ÁREA DO USUÁRIO COMUM
# ──────────────────────────────────────────

@login_required
def meus_agendamentos(request):
    """Página de agendamentos do usuário comum — visualiza apenas os seus."""
    agendamentos = (
        AgendamentoMultimidia.objects
        .filter(solicitante=request.user)
        .order_by('-data', 'horario_inicio')
    )
    return render(request, 'chamados/meus_agendamentos.html', {
        'user': request.user,
        'agendamentos': agendamentos,
    })


@login_required
def novo_agendamento(request):
    """Formulário exclusivo para o usuário comum criar um agendamento."""
    form = AgendamentoMultimidiaForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        cd = form.cleaned_data
        AgendamentoMultimidia.objects.create(
            solicitante    = request.user,
            setor          = cd['setor'],
            local          = cd['local'],
            sala           = cd.get('sala', ''),
            data           = cd['data'],
            horario_inicio = cd['horario_inicio'],
            horario_fim    = cd['horario_fim'],
            equipamentos   = list(cd['equipamentos']),
            finalidade     = cd.get('finalidade', ''),
            observacoes    = cd.get('observacoes', ''),
            status         = 'Pendente',
        )
        messages.success(request, 'Agendamento solicitado com sucesso! Aguarde aprovação da equipe TI.')
        return redirect('meus_agendamentos')

    return render(request, 'chamados/novo_agendamento.html', {
        'user': request.user,
        'form': form,
    })


# ──────────────────────────────────────────
#  AGENDAMENTO — AÇÕES DA EQUIPE TI
# ──────────────────────────────────────────

@login_required
@require_POST
def aprovar_agendamento(request, pk):
    if request.user.tipo != 'ti':
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    ag = get_object_or_404(AgendamentoMultimidia, pk=pk)
    ag.status = 'Aprovado'
    ag.save()
    messages.success(request, f'Agendamento #{pk} aprovado.')
    return redirect('agendamento_multimidia')


@login_required
@require_POST
def cancelar_agendamento(request, pk):
    if request.user.tipo != 'ti':
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    ag = get_object_or_404(AgendamentoMultimidia, pk=pk)
    ag.status = 'Cancelado'
    ag.save()
    messages.success(request, f'Agendamento #{pk} cancelado.')
    return redirect('agendamento_multimidia')


@login_required
@require_POST
def concluir_agendamento(request, pk):
    if request.user.tipo != 'ti':
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    ag = get_object_or_404(AgendamentoMultimidia, pk=pk)
    ag.status = 'Concluído'
    ag.save()
    messages.success(request, f'Agendamento #{pk} concluído.')
    return redirect('agendamento_multimidia')
