from datetime import timedelta

from django.utils import timezone

from core.models import ServiceReminder

from .whatsapp import WhatsappClient


def send_due_soon_reminders(reminders=None) -> int:
    today = timezone.localdate()
    window_end = today + timedelta(days=3)

    queryset = reminders if reminders is not None else ServiceReminder.objects.all()
    due_soon = queryset.filter(
        active=True,
        due_date__range=(today, window_end),
        notified_at__isnull=True,
    ).order_by("due_date")

    client = WhatsappClient()
    sent_count = 0
    for reminder in due_soon:
        if client.send_reminder(reminder):
            sent_count += 1

    return sent_count
