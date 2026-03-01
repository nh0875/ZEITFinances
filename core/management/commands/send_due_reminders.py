from django.core.management.base import BaseCommand

from core.services.reminders import send_due_soon_reminders


class Command(BaseCommand):
    help = "Envía recordatorios por WhatsApp para alertas que vencen dentro de 3 días"

    def handle(self, *args, **options):
        sent_count = send_due_soon_reminders()
        self.stdout.write(self.style.SUCCESS(f"Recordatorios enviados: {sent_count}"))
