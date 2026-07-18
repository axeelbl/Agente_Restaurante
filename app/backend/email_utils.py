import base64
import os

import httpx

from .config import LEADS_FILE, RESEND_API_KEY, RESEND_FROM, RESEND_TO
from .csv_utils import get_last_modified

LAST_SENT = 0
RESEND_EMAILS_URL = "https://api.resend.com/emails"


def _parse_recipients(recipients):
    if not recipients:
        return []
    return [email.strip() for email in recipients.split(",") if email.strip()]


def send_csv_email():
    global LAST_SENT

    if not os.path.exists(LEADS_FILE):
        return

    mtime = get_last_modified()
    if mtime <= LAST_SENT:
        print("No hay leads nuevos, no se envia email")
        return

    if not RESEND_API_KEY or not RESEND_FROM or not RESEND_TO:
        print("Falta configuracion de Resend, no se envia email")
        return

    try:
        with open(LEADS_FILE, "rb") as file_handle:
            encoded_file = base64.b64encode(file_handle.read()).decode()

        payload = {
            "from": RESEND_FROM,
            "to": _parse_recipients(RESEND_TO),
            "subject": "AxelBot - Leads nuevos",
            "text": "Hay nuevos leads desde el ultimo envio.",
            "attachments": [{"filename": "leads.csv", "content": encoded_file}],
        }
        response = httpx.post(
            RESEND_EMAILS_URL,
            headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
            json=payload,
            timeout=30,
        )
        if response.is_error:
            print("Error de Resend:", response.status_code, response.text)
            response.raise_for_status()
        print("CSV enviado, status:", response.status_code)
        LAST_SENT = mtime
    except Exception as exc:
        print("Error enviando CSV:", exc)
