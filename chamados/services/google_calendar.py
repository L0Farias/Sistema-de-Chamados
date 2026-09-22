"""
Serviço de integração com Google Calendar.

Autenticação via Service Account (recomendado para aplicações servidor).
Todas as credenciais são lidas de variáveis de ambiente — nenhuma chave
é hardcoded aqui.

Variáveis de ambiente necessárias (ver .env.example):
    GOOGLE_SERVICE_ACCOUNT_FILE  — caminho para o JSON da Service Account
    GOOGLE_CALENDAR_ID           — ID do calendário (ex: abc123@group.calendar.google.com)

Uso básico:
    from chamados.services.google_calendar import GoogleCalendarService

    svc = GoogleCalendarService()
    disponivel, mensagem = svc.check_availability(local, data, h_inicio, h_fim)
    if disponivel:
        event_id = svc.create_event(local, data, h_inicio, h_fim, titulo, descricao)
"""

import os
import logging
from datetime import datetime, date, time
from zoneinfo import ZoneInfo

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/calendar']

# Fuso horário do Django (settings.py TIME_ZONE)
TZ_NAME = 'America/Sao_Paulo'
TZ = ZoneInfo(TZ_NAME)


class GoogleCalendarError(Exception):
    """Erro genérico do serviço Google Calendar."""


class GoogleCalendarService:
    """
    Encapsula autenticação, consulta de disponibilidade e criação de eventos
    no Google Calendar via Service Account.
    """

    def __init__(self):
        self._service = None

    # ── Autenticação ──────────────────────────────────────────────────

    def _get_service(self):
        """Retorna o cliente autenticado, criando-o na primeira chamada."""
        if self._service is not None:
            return self._service

        cred_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE', '')
        if not cred_file or not os.path.exists(cred_file):
            raise GoogleCalendarError(
                'GOOGLE_SERVICE_ACCOUNT_FILE não configurado ou arquivo não encontrado. '
                'Verifique o .env.'
            )

        credentials = service_account.Credentials.from_service_account_file(
            cred_file, scopes=SCOPES
        )
        self._service = build('calendar', 'v3', credentials=credentials, cache_discovery=False)
        return self._service

    # ── Helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _to_rfc3339(d: date, t: time) -> str:
        """Combina date + time e converte para RFC 3339 com timezone."""
        dt = datetime.combine(d, t, tzinfo=TZ)
        return dt.isoformat()

    @staticmethod
    def _calendar_id() -> str:
        cal_id = os.getenv('GOOGLE_CALENDAR_ID', '')
        if not cal_id:
            raise GoogleCalendarError(
                'GOOGLE_CALENDAR_ID não configurado. Verifique o .env.'
            )
        return cal_id

    # ── Verificação de disponibilidade ────────────────────────────────

    def check_availability(
        self,
        local: str,
        data: date,
        horario_inicio: time,
        horario_fim: time,
    ) -> tuple[bool, str]:
        """
        Verifica se o local está disponível no intervalo solicitado.

        Retorna:
            (True, '')          → disponível
            (False, mensagem)   → conflito encontrado
        """
        try:
            service = self._get_service()
            cal_id  = self._calendar_id()

            # Busca eventos que se sobrepõem ao intervalo:
            # Um evento B conflita com [inicio, fim) se B.start < fim AND B.end > inicio
            time_min = self._to_rfc3339(data, horario_inicio)
            time_max = self._to_rfc3339(data, horario_fim)

            result = service.events().list(
                calendarId=cal_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime',
                q=local,            # filtra por local no texto do evento
            ).execute()

            events = result.get('items', [])

            # Filtragem precisa: verifica sobreposição real com o local exato
            for ev in events:
                ev_location = ev.get('location', '')
                ev_summary  = ev.get('summary', '')

                # Considera conflito se o local aparece no campo location ou no título
                if local.lower() not in ev_location.lower() and \
                   local.lower() not in ev_summary.lower():
                    continue  # evento não é deste local

                # Extrai horários do evento
                ev_start_str = ev.get('start', {}).get('dateTime', '')
                ev_end_str   = ev.get('end',   {}).get('dateTime', '')

                if not ev_start_str or not ev_end_str:
                    continue

                ev_start = datetime.fromisoformat(ev_start_str)
                ev_end   = datetime.fromisoformat(ev_end_str)
                req_start = datetime.combine(data, horario_inicio, tzinfo=TZ)
                req_end   = datetime.combine(data, horario_fim,    tzinfo=TZ)

                # Lógica de sobreposição: A conflita com B se A.start < B.end AND A.end > B.start
                if req_start < ev_end and req_end > ev_start:
                    logger.info(
                        'Conflito detectado para local=%s em %s %s-%s. Evento: %s',
                        local, data, horario_inicio, horario_fim, ev_summary
                    )
                    return False, (
                        f'⚠️ Horário indisponível.\n'
                        f'O local "{local}" já possui um agendamento nesse período.\n'
                        f'Escolha outro horário.'
                    )

            return True, ''

        except GoogleCalendarError:
            raise
        except HttpError as e:
            logger.error('Erro HTTP Google Calendar (check_availability): %s', e)
            raise GoogleCalendarError(
                f'Erro ao consultar o Google Calendar: {e.status_code} — {e.reason}'
            )
        except Exception as e:
            logger.error('Erro inesperado (check_availability): %s', e)
            raise GoogleCalendarError(f'Erro interno ao verificar disponibilidade: {e}')

    # ── Criação de evento ─────────────────────────────────────────────

    def create_event(
        self,
        local: str,
        data: date,
        horario_inicio: time,
        horario_fim: time,
        titulo: str,
        descricao: str = '',
    ) -> str:
        """
        Cria um evento no Google Calendar.

        Retorna o ID do evento criado (google_event_id).
        Lança GoogleCalendarError em caso de falha.
        """
        try:
            service = self._get_service()
            cal_id  = self._calendar_id()

            event_body = {
                'summary':     f'[{local}] {titulo}',
                'location':    local,
                'description': descricao,
                'start': {
                    'dateTime': self._to_rfc3339(data, horario_inicio),
                    'timeZone': TZ_NAME,
                },
                'end': {
                    'dateTime': self._to_rfc3339(data, horario_fim),
                    'timeZone': TZ_NAME,
                },
                # Notificações padrão do calendário
                'reminders': {'useDefault': True},
            }

            created = service.events().insert(
                calendarId=cal_id,
                body=event_body,
            ).execute()

            event_id = created.get('id', '')
            logger.info(
                'Evento criado no Google Calendar: id=%s local=%s data=%s',
                event_id, local, data
            )
            return event_id

        except GoogleCalendarError:
            raise
        except HttpError as e:
            logger.error('Erro HTTP Google Calendar (create_event): %s', e)
            raise GoogleCalendarError(
                f'Erro ao criar evento no Google Calendar: {e.status_code} — {e.reason}'
            )
        except Exception as e:
            logger.error('Erro inesperado (create_event): %s', e)
            raise GoogleCalendarError(f'Erro interno ao criar evento: {e}')

    # ── Exclusão de evento ────────────────────────────────────────────

    def delete_event(self, event_id: str) -> None:
        """Remove um evento do Google Calendar pelo ID. Não lança se não existir."""
        if not event_id:
            return
        try:
            service = self._get_service()
            cal_id  = self._calendar_id()
            service.events().delete(calendarId=cal_id, eventId=event_id).execute()
            logger.info('Evento removido do Google Calendar: id=%s', event_id)
        except HttpError as e:
            if e.status_code == 404:
                logger.warning('Evento %s não encontrado no Google Calendar (já removido?)', event_id)
            else:
                logger.error('Erro ao remover evento %s: %s', event_id, e)
        except Exception as e:
            logger.error('Erro inesperado (delete_event): %s', e)
