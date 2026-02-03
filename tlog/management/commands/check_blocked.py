from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tlog.models import RadioProfile


class Command(BaseCommand):
    help = 'Проверяет статус блокировки пользователей'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Проверить конкретного пользователя по позывному'
        )
        parser.add_argument(
            '--unblock',
            type=str,
            help='Разблокировать пользователя по позывному'
        )
        parser.add_argument(
            '--list-blocked',
            action='store_true',
            help='Показать всех заблокированных пользователей'
        )

    def handle(self, *args, **options):
        username = options.get('username')
        unblock_username = options.get('unblock')
        list_blocked = options.get('list_blocked')

        if username:
            # Проверяем конкретного пользователя
            try:
                user = User.objects.get(username=username.upper())
                profile = user.radio_profile
                
                self.stdout.write(
                    self.style.SUCCESS(f'Пользователь: {user.username}')
                )
                self.stdout.write(f'Email: {user.email}')
                self.stdout.write(f'Заблокирован: {profile.is_blocked}')
                if profile.is_blocked:
                    self.stdout.write(f'Причина: {profile.blocked_reason}')
                    if profile.blocked_at:
                        self.stdout.write(f'Дата блокировки: {profile.blocked_at}')
                
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Пользователь {username} не найден')
                )
            except RadioProfile.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Профиль пользователя {username} не найден')
                )

        elif list_blocked:
            # Показываем всех заблокированных
            blocked_profiles = RadioProfile.objects.filter(is_blocked=True)
            
            if blocked_profiles.exists():
                self.stdout.write(
                    self.style.WARNING(f'Заблокированные пользователи ({blocked_profiles.count()}):')
                )
                for profile in blocked_profiles:
                    self.stdout.write(
                        f'  - {profile.user.username}: {profile.blocked_reason or "Причина не указана"}'
                    )
            else:
                self.stdout.write(
                    self.style.SUCCESS('Заблокированных пользователей не найдено')
                )

        elif unblock_username:
            # Разблокируем пользователя
            try:
                user = User.objects.get(username=unblock_username.upper())
                profile = user.radio_profile
                
                if profile.is_blocked:
                    profile.unblock()
                    self.stdout.write(
                        self.style.SUCCESS(f'Пользователь {user.username} разблокирован')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Пользователь {user.username} не был заблокирован')
                    )
                    
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Пользователь {unblock_username} не найден')
                )
            except RadioProfile.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Профиль пользователя {unblock_username} не найден')
                )

        else:
            self.stdout.write(self.style.ERROR('Укажите один из параметров: --username, --list-blocked или --unblock'))