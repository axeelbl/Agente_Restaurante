from datetime import datetime, timedelta
from app.backend.booking.models import BookingRequest
from app.backend.booking.repository import save_booking, get_booked_hours, update_booking, get_booking_by_uuid, delete_booking
from app.backend.booking.scheduling import is_closed_day, parse_date, parse_time_flexible, get_nearby_free_slots, WORKING_HOURS
from app.backend.booking.notifications import send_booking_notification

import hmac
from app.backend.core.security import validate_text_field, validate_contact

VALID_SERVICES = ["Corte", "Barba", "Corte + Barba"]


def handle_booking(decision, background_tasks):
    booking_data = decision.get("booking", {})

    REQUIRED_FIELDS = ["name", "service", "date", "time", "contact"]
    missing_fields = [f for f in REQUIRED_FIELDS if not booking_data.get(f)]

    FIELD_LABELS = {
        "name": "tu nombre",
        "service": "el servicio que quieres (Corte, Barba o Corte + Barba)",
        "date": "el día de la cita (dia/mes/año)",
        "time": "la hora (24:00)",
        "contact": "un teléfono o email de contacto"
    }

    if missing_fields:
        friendly_fields = [FIELD_LABELS[f] for f in missing_fields]

        if len(friendly_fields) == 1:
            msg = f"Para hacer la reserva necesito que me digas {friendly_fields[0]}."
        else:
            msg = (
                "Para hacer la reserva necesito que me digas "
                + ", ".join(friendly_fields[:-1])
                + " y "
                + friendly_fields[-1]
                + "."
            )

        return {"bot_message": msg}

    try:
        booking_data["date"] = parse_date(booking_data["date"])
    except Exception:
        return {"bot_message": "No he entendido la fecha. Escríbela en formato día/mes/año."}

    if is_closed_day(booking_data["date"]):
        return {
            "bot_message": "Lo siento, ese día estamos cerrados o ya pasó. Por favor elige otro día."
        }

    try:
        requested_minutes = parse_time_flexible(booking_data["time"])
    except ValueError:
        return {
            "bot_message": "No he entendido bien la hora. ¿Puedes decirme otra?"
        }

    # Si la hora coincide exactamente con un slot
    requested_time_str = f"{requested_minutes // 60:02d}:{requested_minutes % 60:02d}"

    if requested_time_str in WORKING_HOURS:
        booking_data["time"] = requested_time_str
    else:
        options = get_nearby_free_slots(booking_data["date"],requested_minutes)
        if not options:
            return {
                "bot_message": "Lo siento, ese día ya no quedan horas disponibles."
            }
        return {
            "bot_message": (
                f"A esa hora no tenemos un bloque exacto. "
                f"¿Te viene bien alguna de estas opciones? "
                f"{' · '.join(options)}"
            )
        }

    if booking_data["time"] not in WORKING_HOURS:
        return {
            "bot_message": f"La hora {booking_data['time']} no está disponible. Intenta otra hora."
        }

    
    try:
        booking_data["name"] = validate_text_field(booking_data["name"], "Nombre")
        booking_data["service"] = validate_text_field(booking_data["service"], "Servicio")
        booking_data["contact"] = validate_contact(booking_data["contact"])
    except ValueError as e:
        return {"bot_message": str(e)}

    if booking_data["service"] not in VALID_SERVICES:
        return {"bot_message": "Servicio no válido."}
    
    booking = BookingRequest(**booking_data)

    try:
        booking_uuid = save_booking(booking)
    except Exception:
        return {"bot_message": "Esa hora ya está reservada, prueba con otra."}

    background_tasks.add_task(
        send_booking_notification,
        booking.contact,
        booking.name,
        booking.service,
        str(booking.date),
        booking.time,
        booking_uuid
    )

    return {
        "bot_message": (
            f"✅ **Reserva confirmada** ✂️\n\n"
            f"👤 Cliente: {booking.name}\n"
            f"✂️ Servicio: {booking.service}\n"
            f"📅 Fecha: {booking.date}\n"
            f"⏰ Hora: {booking.time}\n\n"
            f"📩 Confirmación enviada a:\n{booking.contact}\n"
            f"{f'🆔 ID de reserva: {booking_uuid}' if booking_uuid else ''}\n\n"
            "📍Te esperamos en Calle Lorem Ipsum!"
        ),
        "booking_uuid": booking_uuid 
    }



def handle_availability(date_str: str | None):

    if not date_str:
        return {
            "bot_message": "¿Para qué día quieres ver la disponibilidad?"
        }

    try:
        date = parse_date(date_str)
    except Exception:
        return {
            "bot_message": "No he entendido la fecha. Escríbela en formato día/mes/año."
        }

    if is_closed_day(date):
        return {
            "bot_message": "Ese día estamos cerrados o ya pasó."
        }

    booked = get_booked_hours(str(date))
    free = [h for h in WORKING_HOURS if h not in booked]

    if not free:
        return {
            "bot_message": "Ese día está completo."
        }

    return {
        "bot_message": f"Horarios disponibles el {date}:\n" + " · ".join(free)
    }




def handle_availability_overview(days_ahead: int = 7):
    today = datetime.today().date()

    result_lines = []

    for i in range(days_ahead):
        date = today + timedelta(days=i)

        if is_closed_day(str(date)):
            continue

        booked = get_booked_hours(str(date))
        free = [h for h in WORKING_HOURS if h not in booked]

        if free:
            result_lines.append(
                f"{date.strftime('%d/%m/%Y')} → {', '.join(free)}"
            )

    if not result_lines:
        return {"bot_message": "No hay disponibilidad en los próximos días."}

    return {
        "bot_message":
            "Estos son los próximos días con disponibilidad:\n\n"
            + "\n".join(result_lines)
            + "\n\n¿Quieres reservar alguno?"
    }



def handle_modify_booking(decision, background_tasks):
    booking_data = decision.get("booking", {})
    booking_uuid = booking_data.get("booking_uuid")
    new_date = booking_data.get("date")
    new_time = booking_data.get("time")
    contact = booking_data.get("contact")

    try:
        contact = validate_contact(contact)
    except ValueError as e:
        return {"bot_message": str(e)}

    if not booking_uuid:
        return {"bot_message": "Necesito tu ID de reserva para modificarla."}

    if not contact:
        return {"bot_message": "Necesito tu contacto de la reserva para modificarla."}

    if not new_date and not new_time:
        return {"bot_message": "Indica al menos un nuevo día o una nueva hora para la cita."}
    
    

    # Obtener la reserva existente
    booking = get_booking_by_uuid(booking_uuid)
    if not booking or not hmac.compare_digest(contact, booking[6]):
        return {"bot_message": f"No encontré ninguna reserva con ID {booking_uuid} y con contacto {contact}."}
    
    
    # Si no envían alguno de los datos, mantenemos el existente
    if not new_date:
        new_date = booking[4]  # columna date
    else:
        # Parseamos la fecha "humana" a YYYY-MM-DD
        try:
            new_date = parse_date(new_date)
        except ValueError:
            return {"bot_message": "No entendí la fecha nueva. Escribe día/mes/año."}

    if not new_time:
        new_time = booking[5]  # columna time
    else:
        # Parseamos hora flexible a formato HH:MM
        try:
            minutes = parse_time_flexible(new_time)
            new_time = f"{minutes // 60:02d}:{minutes % 60:02d}"
        except ValueError:
            return {"bot_message": "No entendí la hora nueva. Intenta con algo como 16:30 o cuatro y media."}
    
    # Validaciones
    if is_closed_day(new_date):
        return {"bot_message": "Ese día estamos cerrados o ya pasó, elige otro día."}
    
    if new_time not in WORKING_HOURS:
        return {"bot_message": "Esa hora no está dentro del horario disponible."}

    booked = get_booked_hours(str(new_date))
    if new_time in booked:
        return {"bot_message": f"La hora {new_time} no está disponible ese día."}

    # Actualizar reserva
    try:
        update_booking(booking_uuid, new_date, new_time)
    except Exception as e:
        return {"bot_message": "Error modificando la reserva: " + str(e)}

    # Notificar al usuario por email
    background_tasks.add_task(
        send_booking_notification,
        booking[6],  # contact
        booking[2],  # name
        booking[3],  # service
        str(new_date),
        new_time,
        booking_uuid
    )

    return {
        "bot_message": (
            f"Perfecto, tu cita ha sido modificada: "
            f"{booking[3]} el {new_date} a las {new_time}. "
            f"ID de reserva: {booking_uuid}"
        )
    }


def handle_cancel_booking(decision, background_tasks):
    booking_data = decision.get("booking", {})
    booking_uuid = booking_data.get("booking_uuid")
    contact = booking_data.get("contact")

    try:
        contact = validate_contact(contact)
    except ValueError as e:
        return {"bot_message": str(e)}
    
    if not booking_uuid:
        return {"bot_message": "Necesito tu ID de reserva para cancelar la cita."}
    
    if not contact:
        return {"bot_message": "Necesito tu contacto de la reserva para modificarla."}

    # Obtener la reserva
    booking = get_booking_by_uuid(booking_uuid)
    if not booking or not hmac.compare_digest(contact, booking[6]):
        return {"bot_message": f"No encontré ninguna reserva esos datos"}

    # Borrar reserva
    try:
        delete_booking(booking_uuid)
    except Exception as e:
        return {"bot_message": "Error cancelando la reserva: " + str(e)}

    # Notificar al usuario que se canceló
    background_tasks.add_task(
        send_booking_notification,
        booking[6],  # contact
        booking[2],  # name
        booking[3],  # service
        booking[4],  # date
        booking[5],  # time
        booking_uuid,
        cancelled=True  # Flag para decir que está cancelado
    )

    return {
        "bot_message": (
            f"Tu cita para {booking[3]} el {booking[4]} a las {booking[5]} "
            f"ha sido cancelada correctamente. ID de reserva: {booking_uuid}"
        )
    }