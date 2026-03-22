from __future__ import annotations

import hmac
from datetime import datetime, timedelta

from app.backend.booking.models import BookingRequest
from app.backend.booking.notifications import send_booking_notification
from app.backend.booking.repository import (
    delete_booking,
    find_duplicate_booking,
    get_booking_by_uuid,
    save_booking,
    update_booking,
)
from app.backend.booking.scheduling import (
    WORKING_HOURS,
    get_available_slots,
    get_nearby_free_slots,
    is_closed_day,
    is_slot_available,
    parse_date,
    parse_party_size,
    parse_time_flexible,
)
from app.backend.core.security import validate_contact, validate_text_field


REQUIRED_FIELDS = ["name", "date", "time", "party_size", "contact"]


FIELD_LABELS = {
    "name": "tu nombre",
    "date": "el día de la reserva (día/mes/año)",
    "time": "la hora aproximada (por ejemplo 14:00)",
    "party_size": "el número de comensales",
    "contact": "un teléfono o email de contacto",
}


def validate_optional_notes(notes: str | None) -> str:
    if not notes:
        return ""
    return validate_text_field(notes, "Observaciones", max_length=120)


def add_notification_task(
    background_tasks,
    contact,
    name,
    party_size,
    date,
    time,
    booking_uuid,
    cancelled=False,
    notes="",
):
    if background_tasks is None:
        return

    background_tasks.add_task(
        send_booking_notification,
        contact,
        name,
        party_size,
        str(date),
        time,
        booking_uuid,
        cancelled,
        notes,
    )


def handle_booking(decision, background_tasks):
    booking_data = dict(decision.get("booking", {}))
    missing_fields = [field for field in REQUIRED_FIELDS if booking_data.get(field) in [None, ""]]

    if missing_fields:
        friendly_fields = [FIELD_LABELS[field] for field in missing_fields]

        if len(friendly_fields) == 1:
            message = f"Para reservar necesito que me indiques {friendly_fields[0]}."
        else:
            message = (
                "Para reservar necesito que me indiques "
                + ", ".join(friendly_fields[:-1])
                + " y "
                + friendly_fields[-1]
                + "."
            )
        return {"bot_message": message}

    try:
        booking_data["date"] = parse_date(booking_data["date"])
    except Exception:
        return {"bot_message": "No he entendido la fecha. Escribela en formato dia/mes/año."}

    if is_closed_day(booking_data["date"]):
        return {
            "bot_message": "Ese día estamos cerrados o ya ha pasado. Elige otra fecha."
        }

    try:
        party_size = parse_party_size(booking_data["party_size"])
    except ValueError as exc:
        return {"bot_message": str(exc)}

    try:
        requested_minutes = parse_time_flexible(booking_data["time"])
    except ValueError:
        return {"bot_message": "No he entendido bien la hora. Prueba con algo como 14:00 o 21:30."}

    requested_time = f"{requested_minutes // 60:02d}:{requested_minutes % 60:02d}"
    available_slots = get_available_slots(booking_data["date"], party_size)

    if requested_time not in WORKING_HOURS or requested_time not in available_slots:
        options = get_nearby_free_slots(booking_data["date"], requested_minutes, party_size)
        if not options:
            return {
                "bot_message": "No tengo disponibilidad para ese número de personas en esa fecha."
            }
        return {
            "bot_message": (
                "A esa hora no tenemos mesa disponible, pero puedo ofrecerte estas alternativas: "
                + " · ".join(options)
            )
        }

    try:
        booking_data["name"] = validate_text_field(booking_data["name"], "Nombre")
        booking_data["contact"] = validate_contact(booking_data["contact"])
        booking_data["notes"] = validate_optional_notes(booking_data.get("notes"))
    except ValueError as exc:
        return {"bot_message": str(exc)}

    if find_duplicate_booking(booking_data["contact"], booking_data["date"], requested_time):
        return {
            "bot_message": "Ya existe una reserva con ese contacto para esa fecha y hora."
        }

    booking = BookingRequest(
        name=booking_data["name"],
        date=booking_data["date"],
        time=requested_time,
        party_size=party_size,
        contact=booking_data["contact"],
        notes=booking_data.get("notes", ""),
    )

    try:
        booking_uuid = save_booking(booking)
    except Exception:
        return {"bot_message": "No he podido guardar la reserva. Intentalo de nuevo."}

    add_notification_task(
        background_tasks,
        booking.contact,
        booking.name,
        booking.party_size,
        booking.date,
        booking.time,
        booking_uuid,
        notes=booking.notes,
    )

    notes_line = f"\nObservaciones: {booking.notes}" if booking.notes else ""

    return {
        "bot_message": (
            "Reserva confirmada\n\n"
            f"Cliente: {booking.name}\n"
            f"Comensales: {booking.party_size}\n"
            f"Fecha: {booking.date}\n"
            f"Hora: {booking.time}"
            f"{notes_line}\n"
            f"Confirmacion enviada a: {booking.contact}\n"
            f"ID de reserva: {booking_uuid}\n\n"
            "Si quieres modificarla o cancelarla, puedes usar ese ID."
        ),
        "booking_uuid": booking_uuid,
    }


def handle_availability(decision: dict):
    booking_data = decision.get("booking", {})
    date_str = decision.get("availability_date") or booking_data.get("date")
    party_size_raw = booking_data.get("party_size") or 2
    requested_time = booking_data.get("time")

    if not date_str:
        return {"bot_message": "Dime para que día quieres comprobar disponibilidad."}

    try:
        date = parse_date(date_str)
    except Exception:
        return {"bot_message": "No he entendido la fecha. Escribela en formato día/mes/año."}

    if is_closed_day(date):
        return {"bot_message": "Ese dia estamos cerrados o la fecha ya ha pasado."}

    try:
        party_size = parse_party_size(party_size_raw)
    except ValueError as exc:
        return {"bot_message": str(exc)}

    if requested_time:
        try:
            requested_minutes = parse_time_flexible(requested_time)
        except ValueError:
            return {"bot_message": "No he entendido la hora. Prueba con algo como 14:00."}

        normalized_time = f"{requested_minutes // 60:02d}:{requested_minutes % 60:02d}"
        if is_slot_available(date, normalized_time, party_size):
            return {
                "bot_message": (
                    f"Si, tengo disponibilidad el {date} a las {normalized_time} para "
                    f"{party_size} personas."
                )
            }

        options = get_nearby_free_slots(date, requested_minutes, party_size)
        if not options:
            return {
                "bot_message": (
                    f"No tengo hueco el {date} para {party_size} personas en ese turno."
                )
            }

        return {
            "bot_message": (
                f"No tengo mesa exacta a las {normalized_time} para {party_size} personas. "
                f"Te puedo ofrecer: {' · '.join(options)}"
            )
        }

    available_slots = get_available_slots(date, party_size)
    if not available_slots:
        return {
            "bot_message": f"No quedan mesas libres el {date} para {party_size} personas."
        }

    return {
        "bot_message": (
            f"Disponibilidad el {date} para {party_size} personas:\n"
            + " · ".join(available_slots)
        )
    }


def handle_availability_overview(days_ahead: int = 7, party_size: int = 2):
    today = datetime.today().date()
    result_lines = []

    for offset in range(days_ahead):
        date = today + timedelta(days=offset)
        date_str = date.strftime("%Y-%m-%d")

        if is_closed_day(date_str):
            continue

        free_slots = get_available_slots(date_str, party_size)
        if free_slots:
            preview = ", ".join(free_slots[:5])
            if len(free_slots) > 5:
                preview += ", ..."
            result_lines.append(f"{date.strftime('%d/%m/%Y')} -> {preview}")

    if not result_lines:
        return {"bot_message": "No veo disponibilidad en los proximos dias."}

    return {
        "bot_message": (
            f"Estos son los proximos dias con disponibilidad para {party_size} personas:\n\n"
            + "\n".join(result_lines)
            + "\n\nSi quieres, te ayudo a cerrar la reserva."
        )
    }


def handle_modify_booking(decision, background_tasks):
    booking_data = decision.get("booking", {})
    booking_uuid = booking_data.get("booking_uuid")
    new_date = booking_data.get("date")
    new_time = booking_data.get("time")
    new_party_size = booking_data.get("party_size")
    new_notes = booking_data.get("notes")
    contact = booking_data.get("contact")

    try:
        contact = validate_contact(contact)
    except ValueError as exc:
        return {"bot_message": str(exc)}

    if not booking_uuid:
        return {"bot_message": "Necesito tu ID de reserva para modificarla."}

    if not contact:
        return {"bot_message": "Necesito el contacto asociado a la reserva para modificarla."}

    if not any([new_date, new_time, new_party_size, new_notes]):
        return {
            "bot_message": "Indica al menos una nueva fecha, una nueva hora, un nuevo numero de comensales o unas observaciones."
        }

    booking = get_booking_by_uuid(booking_uuid)
    if not booking or not hmac.compare_digest(contact, booking["contact"]):
        return {
            "bot_message": f"No he encontrado ninguna reserva con ID {booking_uuid} y ese contacto."
        }

    try:
        resolved_date = parse_date(new_date) if new_date else booking["date"]
    except ValueError:
        return {"bot_message": "No he entendido la nueva fecha. Escribela como día/mes/año."}

    if new_time:
        try:
            minutes = parse_time_flexible(new_time)
            resolved_time = f"{minutes // 60:02d}:{minutes % 60:02d}"
        except ValueError:
            return {"bot_message": "No he entendido la nueva hora. Usa algo como 14:30."}
    else:
        resolved_time = booking["time"]

    try:
        resolved_party_size = (
            parse_party_size(new_party_size)
            if new_party_size not in [None, ""]
            else int(booking["party_size"])
        )
    except ValueError as exc:
        return {"bot_message": str(exc)}

    try:
        resolved_notes = (
            validate_optional_notes(new_notes)
            if new_notes not in [None, ""]
            else booking.get("notes", "")
        )
    except ValueError as exc:
        return {"bot_message": str(exc)}

    if is_closed_day(resolved_date):
        return {"bot_message": "Ese día estamos cerrados o ya ha pasado. Elige otro."}

    if resolved_time not in WORKING_HOURS:
        target_minutes = parse_time_flexible(resolved_time)
        options = get_nearby_free_slots(
            resolved_date,
            target_minutes,
            resolved_party_size,
            exclude_booking_uuid=booking_uuid,
        )
        if options:
            return {
                "bot_message": "No trabajo esa hora exacta. Te propongo: " + " · ".join(options)
            }
        return {"bot_message": "La nueva hora esta fuera del horario del restaurante."}

    if not is_slot_available(resolved_date, resolved_time, resolved_party_size, booking_uuid):
        target_minutes = parse_time_flexible(resolved_time)
        options = get_nearby_free_slots(
            resolved_date,
            target_minutes,
            resolved_party_size,
            exclude_booking_uuid=booking_uuid,
        )
        if options:
            return {
                "bot_message": "No tengo disponibilidad exacta para ese cambio. Te propongo: "
                + " · ".join(options)
            }
        return {"bot_message": "No tengo disponibilidad para ese cambio en esa fecha."}

    if find_duplicate_booking(contact, resolved_date, resolved_time, booking_uuid):
        return {
            "bot_message": "Con ese contacto ya existe otra reserva para esa fecha y hora."
        }

    try:
        update_booking(
            booking_uuid,
            resolved_date,
            resolved_time,
            resolved_party_size,
            resolved_notes,
        )
    except Exception as exc:
        return {"bot_message": "Error modificando la reserva: " + str(exc)}

    add_notification_task(
        background_tasks,
        booking["contact"],
        booking["name"],
        resolved_party_size,
        resolved_date,
        resolved_time,
        booking_uuid,
        notes=resolved_notes,
    )

    notes_line = f" Observaciones: {resolved_notes}." if resolved_notes else ""
    return {
        "bot_message": (
            "Perfecto, tu reserva ha sido modificada: "
            f"{resolved_party_size} personas el {resolved_date} a las {resolved_time}."
            f"{notes_line} ID de reserva: {booking_uuid}"
        )
    }


def handle_cancel_booking(decision, background_tasks):
    booking_data = decision.get("booking", {})
    booking_uuid = booking_data.get("booking_uuid")
    contact = booking_data.get("contact")

    try:
        contact = validate_contact(contact)
    except ValueError as exc:
        return {"bot_message": str(exc)}

    if not booking_uuid:
        return {"bot_message": "Necesito tu ID de reserva para cancelarla."}

    if not contact:
        return {"bot_message": "Necesito el contacto de la reserva para cancelarla."}

    booking = get_booking_by_uuid(booking_uuid)
    if not booking or not hmac.compare_digest(contact, booking["contact"]):
        return {"bot_message": "No he encontrado ninguna reserva con esos datos."}

    try:
        delete_booking(booking_uuid)
    except Exception as exc:
        return {"bot_message": "Error cancelando la reserva: " + str(exc)}

    add_notification_task(
        background_tasks,
        booking["contact"],
        booking["name"],
        booking["party_size"],
        booking["date"],
        booking["time"],
        booking_uuid,
        cancelled=True,
        notes=booking.get("notes", ""),
    )

    return {
        "bot_message": (
            f"Tu reserva para {booking['party_size']} personas el {booking['date']} "
            f"a las {booking['time']} ha sido cancelada correctamente. "
            f"ID de reserva: {booking_uuid}"
        )
    }
