import re
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from twilio.rest import Client
import os

# --- CONFIG ---
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("SENDGRID_FROM")

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
TWILIO_PHONE = os.getenv("TWILIO_PHONE")


def is_email(contact: str) -> bool:
    return "@" in contact


def is_phone(contact: str) -> bool:
    return re.fullmatch(r"\+?\d{9,15}", contact) is not None


def send_booking_notification(contact, name, service, date, time, booking_uuid=None, cancelled=False):
    """
    Envía notificación por email o SMS.
    Si cancelled=True, el mensaje indica que se canceló la reserva.
    """
    if is_email(contact):
        send_booking_email(contact, name, service, date, time, booking_uuid, cancelled)
    elif is_phone(contact):
        send_booking_sms(contact, name, service, date, time, booking_uuid, cancelled)
    else:
        print("Contacto no válido:", contact)



def send_booking_email(to_email, name, service, date, time, booking_uuid=None, cancelled=False):
    uuid_text = f"<p><b>ID de reserva:</b> {booking_uuid}</p>" if booking_uuid else ""
    
    if cancelled:
        subject = "Reserva cancelada ❌"
        html_content = f"""
        <h2>Hola {name}!</h2>
        <p>Tu cita para <b>{service}</b> programada para {date} a las {time} ha sido <b>cancelada</b>.</p>
        {uuid_text}
        """
    else:
        subject = "Reserva confirmada ✂️"
        html_content = f"""
        <h2>Hola {name}!</h2>
        <p>Tu cita para <b>{service}</b> está confirmada:</p>
        <ul>
            <li><b>Fecha:</b> {date}</li>
            <li><b>Hora:</b> {time}</li>
        </ul>
        <p>📍Te esperamos en <b>Calle Lorem Ipsum</b>!</p>
        {uuid_text}
        """

    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        html_content=html_content
    )
    sg = SendGridAPIClient(SENDGRID_API_KEY)
    sg.send(message)



def send_booking_sms(phone, name, service, date, time, booking_uuid=None, cancelled=False):
    uuid_text = f" ID de reserva: {booking_uuid}" if booking_uuid else ""
    
    if cancelled:
        body = f"Hola {name}! Tu reserva para {service} el {date} a las {time} ha sido CANCELADA.{uuid_text} ❌"
    else:
        body = f"Hola {name}! Tu reserva para {service} es el {date} a las {time}.{uuid_text} ✂️"

    client = Client(TWILIO_SID, TWILIO_TOKEN)
    client.messages.create(
        body=body,
        from_=TWILIO_PHONE,
        to=phone
    )