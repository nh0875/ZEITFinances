from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group

class Command(BaseCommand):
    help = 'Creates default users and groups on deployment'

    def handle(self, *args, **kwargs):
        # Create groups if they don't exist
        admin_group, _ = Group.objects.get_or_create(name='administrador')
        recep_group, _ = Group.objects.get_or_create(name='recepcionista')

        # Admin User: Jesica
        if not User.objects.filter(username='Jesica').exists():
            admin_user = User.objects.create_superuser('Jesica', '', 'SilvioJesicaNicolCiro@*90')
            admin_user.groups.add(admin_group)
            self.stdout.write(self.style.SUCCESS('Se creo la administradora Jesica'))

        # Receptionist User: ElChoique
        if not User.objects.filter(username='ElChoique').exists():
            receptionist = User.objects.create_user('ElChoique', '', 'Elchoique055')
            receptionist.groups.add(recep_group)
            self.stdout.write(self.style.SUCCESS('Se creo la recepcionista ElChoique'))
