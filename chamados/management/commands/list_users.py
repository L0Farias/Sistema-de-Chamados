from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Lista todos os usuários do sistema com email'

    def handle(self, *args, **options):
        User = get_user_model()
        users = User.objects.all().order_by('username')

        if not users.exists():
            self.stdout.write(self.style.WARNING('Nenhum usuário cadastrado no sistema.'))
            return

        self.stdout.write(self.style.SUCCESS(f'\n=== USUÁRIOS CADASTRADOS ({users.count()}) ===\n'))
        self.stdout.write(f"{'ID':<3} {'Username':<18} {'Nome':<25} {'Email':<35} {'Tipo':<8} {'Status'}")
        self.stdout.write("-" * 100)

        for user in users:
            full_name = user.get_full_name() or '-'
            email = user.email or '-'
            tipo = getattr(user, 'tipo', 'N/A').upper()
            status = "✅ Ativo" if user.is_active else "❌ Inativo"
            
            self.stdout.write(
                f"{user.id:<3} "
                f"{user.username:<18} "
                f"{full_name:<25} "
                f"{email:<35} "
                f"{tipo:<8} "
                f"{status}"
            )
        
        self.stdout.write(self.style.SUCCESS('\nFim da lista.\n'))