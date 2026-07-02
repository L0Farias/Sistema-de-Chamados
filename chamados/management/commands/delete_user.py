from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Deleta um usuário do sistema'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username do usuário a ser deletado')
        parser.add_argument('--id', type=int, help='ID do usuário a ser deletado')
        parser.add_argument('--force', action='store_true', help='Deletar sem confirmação')

    def handle(self, *args, **options):
        User = get_user_model()
        username = options['username']
        user_id = options['id']
        force = options['force']

        # Buscar usuário
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'❌ Usuário com username "{username}" não encontrado.'))
                return
        elif user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'❌ Usuário com ID {user_id} não encontrado.'))
                return
        else:
            self.stdout.write(self.style.ERROR('❌ Você deve informar --username ou --id'))
            return

        # Proteção: Não permitir deletar superusuário facilmente
        if user.is_superuser and not force:
            self.stdout.write(self.style.ERROR('❌ Não é permitido deletar um superusuário sem --force.'))
            return

        self.stdout.write(self.style.WARNING(f'\nVocê está prestes a deletar o usuário:'))
        self.stdout.write(f"   ID: {user.id}")
        self.stdout.write(f"   Username: {user.username}")
        self.stdout.write(f"   Nome: {user.get_full_name() or '-'}")
        self.stdout.write(f"   Email: {user.email or '-'}")
        self.stdout.write(f"   Tipo: {getattr(user, 'tipo', 'N/A').upper()}\n")

        if not force:
            confirm = input("Tem certeza que deseja deletar este usuário? (s/N): ")
            if confirm.lower() != 's':
                self.stdout.write(self.style.SUCCESS('Operação cancelada.'))
                return

        user.delete()
        self.stdout.write(self.style.SUCCESS(f'✅ Usuário "{user.username}" deletado com sucesso!'))