"""
Migration de dados: garante que as 7 etiquetas fixas do sistema existam,
sem duplicar registros caso já existam.
"""
from django.db import migrations

ETIQUETAS_FIXAS = [
    ('Problema',         '#f97316'),  # laranja
    ('Rede',             '#3b82f6'),  # azul
    ('Solicitação',      '#22c55e'),  # verde
    ('Impressora Locada','#8b5cf6'),  # roxo
    ('Computador',       '#6b7280'),  # cinza
    ('Computador Locado','#92400e'),  # marrom
    ('Telefone',         '#06b6d4'),  # ciano
]


def criar_etiquetas(apps, schema_editor):
    Etiqueta = apps.get_model('chamados', 'Etiqueta')
    for nome, cor in ETIQUETAS_FIXAS:
        Etiqueta.objects.get_or_create(nome=nome, defaults={'cor': cor, 'ativa': True})


def remover_etiquetas(apps, schema_editor):
    # Reversão: não remove (poderia ter sido associada a chamados)
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('chamados', '0006_etiqueta_m2m_e_historico'),
    ]
    operations = [
        migrations.RunPython(criar_etiquetas, remover_etiquetas),
    ]
