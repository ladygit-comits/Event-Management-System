from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Creates a default superuser if none exist'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                username='faith_admin',
                email='admin@example.com',
                password='F@ith2025$issawrap!'
            )
            self.stdout.write(self.style.SUCCESS('Default superuser created.'))
        else:
            self.stdout.write('Superuser already exists.')
