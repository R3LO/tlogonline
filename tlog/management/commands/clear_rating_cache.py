from django.core.management.base import BaseCommand
from django.core.cache import cache


class Command(BaseCommand):
    help = 'Очищает кэш рейтингов и наград'

    def handle(self, *args, **options):
        # Получаем все ключи кэша, связанные с рейтингом
        # В Redis это можно сделать через KEYS pattern, но для Memcached нужно знать точные ключи
        # Поэтому просто очищаем весь кэш для простоты

        cache.clear()

        self.stdout.write(
            self.style.SUCCESS('Кэш рейтингов и наград успешно очищен')
        )
