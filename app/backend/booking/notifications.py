import os
import re
from html import escape

import httpx
from twilio.rest import Client


RESEND_API_KEY = os.getenv("RESEND_API_KEY")
FROM_EMAIL = os.getenv("RESEND_FROM")
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
    if not RESEND_API_KEY or not FROM_EMAIL:
        return

    safe_name = escape(str(name))
    safe_date = escape(str(date))
    safe_time = escape(str(time))
    safe_uuid = escape(str(booking_uuid)) if booking_uuid else ""
    safe_notes = escape(str(notes)) if notes else ""
    uuid_text = f"<p><b>ID de reserva:</b> {safe_uuid}</p>" if safe_uuid else ""
    notes_text = f"<p><b>Observaciones:</b> {safe_notes}</p>" if safe_notes else ""

    if cancelled:
        subject = "Reserva cancelada"
        html_content = f"""
        <h2>Hola {safe_name}</h2>
        <p>Tu reserva para <b>{party_size} personas</b> del {safe_date} a las {safe_time} ha sido cancelada.</p>
        {notes_text}
        {uuid_text}
        """
    else:
        subject = "Reserva confirmada"
        html_content = f"""
        <h2>Hola {safe_name}</h2>
        <p>Tu reserva está confirmada:</p>
        <ul>
            <li><b>Comensales:</b> {party_size}</li>
            <li><b>Fecha:</b> {safe_date}</li>
            <li><b>Hora:</b> {safe_time}</li>
        </ul>
        {notes_text}
        {uuid_text}
        """

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
    if not TWILIO_SID or not TWILIO_TOKEN or not TWILIO_PHONE:
        return

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
    client.messages.create(body=body, from_=TWILIO_PHONE, to=phone)
