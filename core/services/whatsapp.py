import logging
import os
from typing import Optional

import requests
from django.utils import timezone

logger = logging.getLogger(__name__)


class WhatsappClient:
    def __init__(self):
        self.token = os.getenv("WHATSAPP_TOKEN")
        self.phone_id = os.getenv("WHATSAPP_PHONE_ID")
        self.enabled = bool(self.token and self.phone_id)

    def send_reminder(self, reminder) -> bool:
        if not self.enabled:
            logger.info("WhatsApp no configurado, se omite envío.")
            return False

        message = self._build_message(reminder)
        url = f"https://graph.facebook.com/v20.0/{self.phone_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "to": reminder.phone_number,
            "type": "text",
            "text": {"body": message},
        }
        headers = {
            "Authorization": f"Bearer {self.token}",
        }
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            reminder.notified_at = timezone.now()
            reminder.save(update_fields=["notified_at"])
            return True
        except Exception as exc:  # pragma: no cover - best effort
            logger.error("Error enviando WhatsApp: %s", exc)
            return False

    @staticmethod
    def _build_message(reminder) -> str:
        return (
            f"Recordatorio: {reminder.title}\n"
            f"Vence: {reminder.due_date} | Monto: ${reminder.amount}\n"
            f"Tipo: {reminder.get_service_type_display()}"
        )
