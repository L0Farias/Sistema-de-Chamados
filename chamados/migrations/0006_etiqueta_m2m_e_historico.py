import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models

# Cores padrão para cada etiqueta que existia no CharField antigo
CORES_PADRAO = {
    'Problema':          '#f59e0b',  # amarelo
    'Solicitação':       '#3b82f6',  # azul
    'Computador Locado': '#8b5cf6',  # roxo
    'Impressora Locada': '#6b7280',  # cinza
    'Bug':               '#ef4444',  # vermelho
}


def migrar_etiquetas_para_m2m(apps, schema_editor):
    """
    Migração de dados: lê o campo CharField 'etiqueta' de cada Chamado,
    garante que existe um registro Etiqueta correspondente, e cria a
    relação M2M. Executa antes do RemoveField do CharField.
    """
    Chamado  = apps.get_model('chamados', 'Chamado')
    Etiqueta = apps.get_model('chamados', 'Etiqueta')

    for chamado in Chamado.objects.exclude(etiqueta='').exclude(etiqueta__isnull=True):
        nome = chamado.etiqueta.strip()
        if not nome:
            continue
        cor = CORES_PADRAO.get(nome, '#6366f1')
        etiqueta_obj, _ = Etiqueta.objects.get_or_create(
            nome=nome,
            defaults={'cor': cor, 'ativa': True}
        )
        chamado.etiquetas.add(etiqueta_obj)


def reverter_migrar_etiquetas(apps, schema_editor):
    """Reversão: limpa o M2M (o CharField é restaurado vazio — dados não recuperáveis)."""
    Chamado = apps.get_model('chamados', 'Chamado')
    for chamado in Chamado.objects.all():
        chamado.etiquetas.clear()


class Migration(migrations.Migration):

    dependencies = [
        ('chamados', '0005_alter_chamado_etiqueta'),
    ]

    operations = [
        # 1. Criar o model Etiqueta
        migrations.CreateModel(
            name='Etiqueta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=50, unique=True, verbose_name='Nome')),
                ('cor', models.CharField(
                    default='#6366f1', max_length=7,
                    validators=[django.core.validators.RegexValidator(
                        message='A cor deve estar no formato hexadecimal #RRGGBB.',
                        regex='^#[0-9A-Fa-f]{6}$'
                    )],
                    verbose_name='Cor (hex)'
                )),
                ('ativa', models.BooleanField(default=True, verbose_name='Ativa')),
            ],
            options={
                'verbose_name': 'Etiqueta',
                'verbose_name_plural': 'Etiquetas',
                'ordering': ['nome'],
            },
        ),

        # 2. Criar o campo M2M no Chamado (vazio por enquanto)
        migrations.AddField(
            model_name='chamado',
            name='etiquetas',
            field=models.ManyToManyField(
                blank=True, related_name='chamados',
                to='chamados.etiqueta', verbose_name='Etiquetas'
            ),
        ),

        # 3. Migrar dados: CharField → Etiqueta + M2M
        migrations.RunPython(migrar_etiquetas_para_m2m, reverter_migrar_etiquetas),

        # 4. Remover o CharField antigo
        migrations.RemoveField(
            model_name='chamado',
            name='etiqueta',
        ),

        # 5. Ajustar FKs que ganharam verbose_name
        migrations.AlterField(
            model_name='chamado',
            name='atendente_fechamento',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='chamados_fechados',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Atendente no Fechamento'
            ),
        ),
        migrations.AlterField(
            model_name='chamado',
            name='reaberto_por',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='chamados_reabertos',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Reaberto Por'
            ),
        ),

        # 6. Criar HistoricoEtiqueta
        migrations.CreateModel(
            name='HistoricoEtiqueta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('acao', models.CharField(
                    choices=[('adicionada', 'Adicionada'), ('removida', 'Removida')],
                    max_length=10
                )),
                ('data', models.DateTimeField(default=django.utils.timezone.now)),
                ('chamado', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='historico_etiquetas', to='chamados.chamado'
                )),
                ('etiqueta', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='historico', to='chamados.etiqueta'
                )),
                ('usuario', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name': 'Histórico de Etiqueta',
                'verbose_name_plural': 'Histórico de Etiquetas',
                'ordering': ['data'],
            },
        ),
    ]
