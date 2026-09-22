"""
Testes da integração Google Calendar.
A API real NÃO é chamada — tudo é mockado via unittest.mock.
"""

import os
from datetime import date, time, datetime
from unittest.mock import MagicMock, patch, PropertyMock
from zoneinfo import ZoneInfo

from django.test import TestCase, RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage

from chamados.services.google_calendar import (
    GoogleCalendarService,
    GoogleCalendarError,
    TZ_NAME,
    TZ,
)
from chamados.models import AgendamentoMultimidia

# ─── helpers ─────────────────────────────────────────────────────────────────

LOCAL_VALIDO  = 'Auditório da Prefeitura'
LOCAL_VALIDO2 = 'Sede da Secretaria de Saúde'
DATA          = date(2026, 8, 10)
INICIO        = time(9, 0)
FIM           = time(12, 0)


def _ev(local: str, inicio: time, fim: time, d: date = DATA) -> dict:
    """Monta um item de evento no formato retornado pela API do Google."""
    tz = ZoneInfo(TZ_NAME)
    return {
        'id': 'fake_event_id',
        'summary': f'[{local}] Teste',
        'location': local,
        'start': {'dateTime': datetime.combine(d, inicio, tzinfo=tz).isoformat()},
        'end':   {'dateTime': datetime.combine(d, fim,    tzinfo=tz).isoformat()},
    }


def _svc_with_events(events: list) -> GoogleCalendarService:
    """Cria um GoogleCalendarService com o método list() mockado."""
    svc = GoogleCalendarService()
    mock_service = MagicMock()
    mock_service.events.return_value.list.return_value.execute.return_value = {
        'items': events
    }
    svc._service = mock_service
    return svc


# ─── 1. Disponibilidade — horário completamente livre ────────────────────────

class TestDisponibilidade(TestCase):

    @patch.dict(os.environ, {
        'GOOGLE_SERVICE_ACCOUNT_FILE': '/fake/sa.json',
        'GOOGLE_CALENDAR_ID': 'fake@group.calendar.google.com',
    })
    def test_horario_livre(self):
        """Nenhum evento → disponível."""
        svc = _svc_with_events([])
        ok, msg = svc.check_availability(LOCAL_VALIDO, DATA, INICIO, FIM)
        self.assertTrue(ok)
        self.assertEqual(msg, '')

    @patch.dict(os.environ, {
        'GOOGLE_SERVICE_ACCOUNT_FILE': '/fake/sa.json',
        'GOOGLE_CALENDAR_ID': 'fake@group.calendar.google.com',
    })
    def test_conflito_exato(self):
        """Evento exatamente no mesmo horário → conflito."""
        svc = _svc_with_events([_ev(LOCAL_VALIDO, INICIO, FIM)])
        ok, msg = svc.check_availability(LOCAL_VALIDO, DATA, INICIO, FIM)
        self.assertFalse(ok)
        self.assertIn(LOCAL_VALIDO, msg)

    @patch.dict(os.environ, {
        'GOOGLE_SERVICE_ACCOUNT_FILE': '/fake/sa.json',
        'GOOGLE_CALENDAR_ID': 'fake@group.calendar.google.com',
    })
    def test_conflito_parcial_inicio(self):
        """Evento 09-12, pedido 10-11 (dentro) → conflito."""
        svc = _svc_with_events([_ev(LOCAL_VALIDO, time(9, 0), time(12, 0))])
        ok, _ = svc.check_availability(LOCAL_VALIDO, DATA, time(10, 0), time(11, 0))
        self.assertFalse(ok)

    @patch.dict(os.environ, {
        'GOOGLE_SERVICE_ACCOUNT_FILE': '/fake/sa.json',
        'GOOGLE_CALENDAR_ID': 'fake@group.calendar.google.com',
    })
    def test_conflito_envolve_evento(self):
        """Pedido 08-13 envolve evento 09-12 → conflito."""
        svc = _svc_with_events([_ev(LOCAL_VALIDO, time(9, 0), time(12, 0))])
        ok, _ = svc.check_availability(LOCAL_VALIDO, DATA, time(8, 0), time(13, 0))
        self.assertFalse(ok)

    @patch.dict(os.environ, {
        'GOOGLE_SERVICE_ACCOUNT_FILE': '/fake/sa.json',
        'GOOGLE_CALENDAR_ID': 'fake@group.calendar.google.com',
    })
    def test_livre_antes_do_evento(self):
        """Evento 09-12, pedido 07-09 (adjacente, sem overlap) → disponível."""
        svc = _svc_with_events([_ev(LOCAL_VALIDO, time(9, 0), time(12, 0))])
        ok, _ = svc.check_availability(LOCAL_VALIDO, DATA, time(7, 0), time(9, 0))
        self.assertTrue(ok)

    @patch.dict(os.environ, {
        'GOOGLE_SERVICE_ACCOUNT_FILE': '/fake/sa.json',
        'GOOGLE_CALENDAR_ID': 'fake@group.calendar.google.com',
    })
    def test_livre_depois_do_evento(self):
        """Evento 09-12, pedido 12-13 (adjacente, sem overlap) → disponível."""
        svc = _svc_with_events([_ev(LOCAL_VALIDO, time(9, 0), time(12, 0))])
        ok, _ = svc.check_availability(LOCAL_VALIDO, DATA, time(12, 0), time(13, 0))
        self.assertTrue(ok)

    @patch.dict(os.environ, {
        'GOOGLE_SERVICE_ACCOUNT_FILE': '/fake/sa.json',
        'GOOGLE_CALENDAR_ID': 'fake@group.calendar.google.com',
    })
    def test_outro_local_mesmo_horario(self):
        """Evento no mesmo horário mas LOCAL DIFERENTE → disponível."""
        svc = _svc_with_events([_ev(LOCAL_VALIDO2, time(9, 0), time(12, 0))])
        ok, _ = svc.check_availability(LOCAL_VALIDO, DATA, INICIO, FIM)
        self.assertTrue(ok)


# ─── 2. Locais oficiais ───────────────────────────────────────────────────────

class TestLocaisOficiais(TestCase):

    def test_nove_locais_no_model(self):
        """AgendamentoMultimidia.LOCAIS_CHOICES deve ter exatamente 9 locais."""
        self.assertEqual(len(AgendamentoMultimidia.LOCAIS_CHOICES), 9)

    def test_locais_esperados(self):
        valores = [v for v, _ in AgendamentoMultimidia.LOCAIS_CHOICES]
        esperados = [
            'Auditório da Prefeitura',
            'Sede da Secretaria de Saúde',
            'Centro Integrado',
            'Faetec',
            'Sicoob',
            'Ciep',
            'Maristas',
            'Cipec',
            'Sala dos Conselhos',
        ]
        for local in esperados:
            self.assertIn(local, valores, f'Local ausente: {local}')

    def test_sem_outros(self):
        valores = [v for v, _ in AgendamentoMultimidia.LOCAIS_CHOICES]
        self.assertNotIn('Outros', valores)
        self.assertNotIn('Outro', valores)


# ─── 3. Timezone ─────────────────────────────────────────────────────────────

class TestTimezone(TestCase):

    def test_timezone_sao_paulo(self):
        self.assertEqual(TZ_NAME, 'America/Sao_Paulo')

    def test_rfc3339_tem_offset(self):
        """Data/hora convertida para RFC 3339 deve conter offset de timezone."""
        resultado = GoogleCalendarService._to_rfc3339(DATA, INICIO)
        # Deve conter '-03:00' ou '-02:00' (horário de verão) — nunca 'Z' (UTC)
        self.assertIn('-0', resultado.replace('+', '-'))
        self.assertNotIn('Z', resultado)


# ─── 4. Erro da API ──────────────────────────────────────────────────────────

class TestErroAPI(TestCase):

    @patch.dict(os.environ, {
        'GOOGLE_SERVICE_ACCOUNT_FILE': '/fake/sa.json',
        'GOOGLE_CALENDAR_ID': 'fake@group.calendar.google.com',
    })
    def test_erro_generico_levanta_excecao(self):
        """Erro inesperado da API deve levantar GoogleCalendarError."""
        svc = GoogleCalendarService()
        mock_service = MagicMock()
        mock_service.events.return_value.list.return_value.execute.side_effect = \
            Exception('Falha de rede')
        svc._service = mock_service

        with self.assertRaises(GoogleCalendarError):
            svc.check_availability(LOCAL_VALIDO, DATA, INICIO, FIM)

    def test_sem_env_vars_levanta_excecao(self):
        """Sem variáveis de ambiente, deve levantar GoogleCalendarError."""
        svc = GoogleCalendarService()
        with self.assertRaises(GoogleCalendarError):
            svc._calendar_id()


# ─── 5. Criação de evento ─────────────────────────────────────────────────────

class TestCriacaoEvento(TestCase):

    @patch.dict(os.environ, {
        'GOOGLE_SERVICE_ACCOUNT_FILE': '/fake/sa.json',
        'GOOGLE_CALENDAR_ID': 'fake@group.calendar.google.com',
    })
    def test_create_event_retorna_id(self):
        """create_event deve retornar o ID do evento criado."""
        svc = GoogleCalendarService()
        mock_service = MagicMock()
        mock_service.events.return_value.insert.return_value.execute.return_value = {
            'id': 'novo_event_id_123'
        }
        svc._service = mock_service

        event_id = svc.create_event(
            local='Auditório da Prefeitura',
            data=DATA,
            horario_inicio=INICIO,
            horario_fim=FIM,
            titulo='Teste de evento',
        )
        self.assertEqual(event_id, 'novo_event_id_123')

    @patch.dict(os.environ, {
        'GOOGLE_SERVICE_ACCOUNT_FILE': '/fake/sa.json',
        'GOOGLE_CALENDAR_ID': 'fake@group.calendar.google.com',
    })
    def test_create_event_usa_local_no_titulo(self):
        """O evento criado deve incluir o local no título."""
        svc = GoogleCalendarService()
        mock_service = MagicMock()
        mock_service.events.return_value.insert.return_value.execute.return_value = {'id': 'x'}
        svc._service = mock_service

        svc.create_event('Faetec', DATA, INICIO, FIM, 'Reunião')

        call_args = mock_service.events.return_value.insert.call_args
        body = call_args.kwargs.get('body') or call_args.args[0] if call_args.args else call_args[1].get('body', {})
        # Aceitar ambas as formas de chamada
        if not body:
            body = call_args[1].get('body', {})
        summary = body.get('summary', '')
        self.assertIn('Faetec', summary)


# ─── 6. Permissões (integração com view) ──────────────────────────────────────

class TestPermissoes(TestCase):

    def setUp(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.usuario_comum = User.objects.create_user(
            username='comum_test',
            password='senha123',
            email='comum@test.com',
            tipo='comum',
        )
        self.usuario_ti = User.objects.create_user(
            username='ti_test',
            password='senha123',
            email='ti@test.com',
            tipo='ti',
        )

    def test_usuario_comum_nao_ve_agendamentos_de_outros(self):
        """Usuário comum acessa /agendamento/ mas só vê seus próprios agendamentos — não os de terceiros."""
        from chamados.models import AgendamentoMultimidia
        from datetime import date, time

        # Cria agendamento do usuário TI
        ag_ti = AgendamentoMultimidia.objects.create(
            solicitante=self.usuario_ti,
            setor='TI', local='Faetec', sala='',
            data=date(2026, 12, 1), horario_inicio=time(9, 0), horario_fim=time(10, 0),
            equipamentos=[], status='Pendente',
        )
        # Cria agendamento do usuário comum
        ag_comum = AgendamentoMultimidia.objects.create(
            solicitante=self.usuario_comum,
            setor='RH', local='Sicoob', sala='',
            data=date(2026, 12, 2), horario_inicio=time(9, 0), horario_fim=time(10, 0),
            equipamentos=[], status='Pendente',
        )

        self.client.login(username='comum_test', password='senha123')
        response = self.client.get('/agendamento/')
        self.assertEqual(response.status_code, 200)

        # O contexto deve conter apenas o agendamento do próprio usuário comum
        pendentes = list(response.context['agendamentos_pendentes'])
        ids = [a.id for a in pendentes]
        self.assertIn(ag_comum.id, ids, 'Agendamento próprio deve aparecer')
        self.assertNotIn(ag_ti.id, ids, 'Agendamento de outro usuário NÃO deve aparecer')

    def test_usuario_ti_acessa_admin(self):
        """Usuário TI pode acessar /agendamento/ normalmente."""
        self.client.login(username='ti_test', password='senha123')
        response = self.client.get('/agendamento/')
        self.assertEqual(response.status_code, 200)
