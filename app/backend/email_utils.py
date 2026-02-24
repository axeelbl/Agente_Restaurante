# Envío de CSV por email (SendGrid)

import base64
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
from .config import SENDGRID_API_KEY, SENDGRID_FROM, SENDGRID_TO, LEADS_FILE
from .csv_utils import get_last_modified
import os

LAST_SENT = 0

def send_csv_email():
    global LAST_SENT

    if not os.path.exists(LEADS_FILE):
        return

    mtime = get_last_modified()
    if mtime <= LAST_SENT:
        print("No hay leads nuevos, no se envía email")
        return

    try:
        with open(LEADS_FILE, "rb") as f:
            encoded_file = base64.b64encode(f.read()).decode()

        attachment = Attachment(
            file_content=FileContent(encoded_file),
            file_type=FileType("text/csv"),
            file_name=FileName("leads.csv"),
            disposition=Disposition("attachment")
        )

        message = Mail(
            from_email=SENDGRID_FROM,
            to_emails=SENDGRID_TO,
            subject="AxelBot – Leads (nuevos)",
            plain_text_content="Hay nuevos leads desde el último envío."
        )
        message.attachment = attachment

        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print("CSV enviado, status:", response.status_code)

        LAST_SENT = mtime
    except Exception as e:
        print("Error enviando CSV:", e)
