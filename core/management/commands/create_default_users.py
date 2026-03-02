from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Profile

class Command(BaseCommand):
    help = 'Creates default users on deployment'

    def handle(self, *args, **kwargs):
        # Admin User: Jesica
        if not User.objects.filter(username='Jesica').exists():
            admin_user = User.objects.create_superuser('Jesica', '', 'SilvioJesicaNicolCiro@*90')
            Profile.objects.filter(user=admin_user).update(role='admin')
            self.stdout.write(self.style.SUCCESS('Se creó la administradora Jesica'))

        # Receptionist User: ElChoique
        if not User.objects.filter(username='ElChoique').exists():
            receptionist = User.objects.create_user('ElChoique', '', 'Elchoique055')
            Profile.objects.filter(user=receptionist).update(role='recepcionista')
            self.stdout.write(self.style.SUCCESS('Se creó la recepcionista ElChoique'))
