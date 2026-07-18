import os
import re

import httpx
from twilio.rest import Client


RESEND_API_KEY = os.getenv("RESEND_API_KEY")
FROM_EMAIL = os.getenv("RESEND_FROM") or os.getenv("SENDGRID_FROM")

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
TWILIO_PHONE = os.getenv("TWILIO_PHONE")


def is_email(contact: str) -> bool:
    return "@" in contact


def is_phone(contact: str) -> bool:
    return re.fullmatch(r"\+?\d{9,15}", contact) is not None


def send_booking_notification(
    contact,
    name,
    party_size,
    date,
    time,
    booking_uuid=None,
    cancelled=False,
    notes="",
):
    if is_email(contact):
        send_booking_email(contact, name, party_size, date, time, booking_uuid, cancelled, notes)
    elif is_phone(contact):
        send_booking_sms(contact, name, party_size, date, time, booking_uuid, cancelled, notes)
    else:
        print("Contacto no válido:", contact)


def send_booking_email(
    to_email,
    name,
    party_size,
    date,
    time,
    booking_uuid=None,
    cancelled=False,
    notes="",
):
    uuid_text = f"<p><b>ID de reserva:</b> {booking_uuid}</p>" if booking_uuid else ""
    notes_text = f"<p><b>Observaciones:</b> {notes}</p>" if notes else ""

    if cancelled:
        subject = "Reserva cancelada"
        html_content = f"""
        <h2>Hola {name}</h2>
        <p>Tu reserva para <b>{party_size} personas</b> del {date} a las {time} ha sido cancelada.</p>
        {notes_text}
        {uuid_text}
        """
    else:
        subject = "Reserva confirmada"
        html_content = f"""
        <h2>Hola {name}</h2>
        <p>Tu reserva esta confirmada:</p>
        <ul>
            <li><b>Comensales:</b> {party_size}</li>
            <li><b>Fecha:</b> {date}</li>
            <li><b>Hora:</b> {time}</li>
        </ul>
        {notes_text}
        {uuid_text}
        """

    if not RESEND_API_KEY or not FROM_EMAIL:
        print("Falta configuracion de Resend, no se envia email de reserva")
        return

    response = httpx.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
        json={
            "from": FROM_EMAIL,
            "to": [to_email],
            "subject": subject,
            "html": html_content,
        },
        timeout=30,
    )
    if response.is_error:
        print("Error de Resend:", response.status_code, response.text)
        response.raise_for_status()


def send_booking_sms(
    phone,
    name,
    party_size,
    date,
    time,
    booking_uuid=None,
    cancelled=False,
    notes="",
):
    uuid_text = f" ID de reserva: {booking_uuid}" if booking_uuid else ""
    notes_text = f" Observaciones: {notes}." if notes else ""

    if cancelled:
        body = (
            f"Hola {name}. Tu reserva para {party_size} personas el {date} a las {time} "
            f"ha sido cancelada.{notes_text}{uuid_text}"
        )
    else:
        body = (
            f"Hola {name}. Reserva confirmada para {party_size} personas el {date} a las {time}."
            f"{notes_text}{uuid_text}"
        )

    client = Client(TWILIO_SID, TWILIO_TOKEN)
    client.messages.create(
        body=body,
        from_=TWILIO_PHONE,
        to=phone,
    )
