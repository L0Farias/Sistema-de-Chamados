from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


class Command(BaseCommand):
    help = 'Cria um novo usuário TI (com email obrigatório) ou promove um usuário existente para TI'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Nome de usuário')
        parser.add_argument('--email',    type=str, help='E-mail do usuário (obrigatório para criação)')
        parser.add_argument('--password', type=str, help='Senha')
        parser.add_argument('--nome',     type=str, help='Nome completo (opcional)')
        parser.add_argument(
            '--promover',
            type=str,
            help='Promover usuário existente para TI (informe o username)',
        )

    def handle(self, *args, **options):
        User = get_user_model()

        # === PROMOVER USUÁRIO EXISTENTE ===
        if options['promover']:
            username = options['promover']
            try:
                user = User.objects.get(username=username)
                if user.tipo == 'ti':
                    self.stdout.write(self.style.WARNING(f'O usuário "{username}" já é TI.'))
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
        email    = options['email']
        nome     = options['nome'] or username

        # --- Validação de campos obrigatórios ---
        if not username or not password or not email:
            self.stdout.write(self.style.ERROR(
                '❌ Para criar um usuário TI você deve informar --username, --email e --password'
            ))
            return

        # --- Validação de formato do email ---
        try:
            validate_email(email)
        except ValidationError:
            self.stdout.write(self.style.ERROR(
                f'❌ O e-mail "{email}" não é um endereço válido.'
            ))
            return

        # --- Verificar unicidade do username ---
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.ERROR(
                f'❌ Já existe um usuário com o username "{username}".'
            ))
            return

        # --- Verificar unicidade do email ---
        if User.objects.filter(email__iexact=email).exists():
            self.stdout.write(self.style.ERROR(
                f'❌ O e-mail "{email}" já está cadastrado no sistema.'
            ))
            return

        # --- Criar usuário ---
        first_name = nome.split()[0] if ' ' in nome else nome
        last_name  = ' '.join(nome.split()[1:]) if ' ' in nome else ''

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )

        user.tipo     = 'ti'
        user.is_staff = True  # Acesso ao painel admin
        user.save()

        self.stdout.write(self.style.SUCCESS('✅ Usuário TI criado com sucesso!'))
        self.stdout.write(f'   Username : {user.username}')
        self.stdout.write(f'   E-mail   : {user.email}')
        self.stdout.write(f'   Nome     : {user.get_full_name() or user.username}')
        self.stdout.write(f'   Tipo     : {user.tipo.upper()}')
        self.stdout.write(f'   Staff    : {user.is_staff}')
