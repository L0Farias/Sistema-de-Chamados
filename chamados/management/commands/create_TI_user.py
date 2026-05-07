from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from chamados.models import Usuario

class Command(BaseCommand):
    help = 'Cria um novo usuário TI ou promove um usuário existente para TI'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Nome de usuário')
        parser.add_argument('--password', type=str, help='Senha')
        parser.add_argument('--nome', type=str, help='Nome completo (opcional)')
        parser.add_argument('--promover', type=str, help='Promover usuário existente para TI (informe o username)')

    def handle(self, *args, **options):
        User = get_user_model()

        # === PROMOVER USUÁRIO EXISTENTE ===
        if options['promover']:
            username = options['promover']
            try:
                user = User.objects.get(username=username)
                if user.tipo == 'ti':
                    self.stdout.write(self.style.WARNING(f'O usuário {username} já é TI.'))
                    return
                
                user.tipo = 'ti'
                user.save()
                self.stdout.write(self.style.SUCCESS(f'✅ Usuário "{username}" promovido para TI com sucesso!'))
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'❌ Usuário "{username}" não encontrado.'))
            return

        # === CRIAR NOVO USUÁRIO TI ===
        username = options['username']
        password = options['password']
        nome = options['nome'] or username

        if not username or not password:
            self.stdout.write(self.style.ERROR('❌ Você deve informar --username e --password'))
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.ERROR(f'❌ Já existe um usuário com o username "{username}".'))
            return

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=nome.split()[0] if ' ' in nome else nome,
            last_name=' '.join(nome.split()[1:]) if ' ' in nome else '',
        )
        
        user.tipo = 'ti'
        user.is_staff = True  # Dá acesso ao admin
        user.save()

        self.stdout.write(self.style.SUCCESS(f'✅ Usuário TI criado com sucesso!'))
        self.stdout.write(f'   Username: {user.username}')
        self.stdout.write(f'   Nome: {user.get_full_name() or user.username}')
        self.stdout.write(f'   Tipo: {user.tipo.upper()}')
        self.stdout.write(f'   Staff: {user.is_staff}')