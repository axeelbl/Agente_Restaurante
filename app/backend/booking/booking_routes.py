# RUTAS DE LA API PARA PODER GESTIONAR LAS RESERVAS DE MANERA MANUAL

from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from .models import BookingRequest
from .repository import get_booked_hours, save_booking, update_booking, delete_booking, get_booking_by_uuid
from .scheduling import WORKING_HOURS, is_closed_day, parse_date
from .notifications import send_booking_notification
from app.backend.core.security import limiter, validate_contact,validate_text_field

import html


router = APIRouter(prefix="/booking", tags=["booking"])

@router.get("/availability")
@limiter.limit("60/minute")
def availability(request: Request, date: str):
    if is_closed_day(date):
        return []  # Cierra ese día o ya pasó

    booked = get_booked_hours(date)
    return [h for h in WORKING_HOURS if h not in booked]


@router.post("/reserve")
@limiter.limit("20/minute")
def reserve(request: Request, booking: BookingRequest, background_tasks: BackgroundTasks):
    try:
        # Validar y sanitizar campos de texto
        safe_name = validate_text_field(booking.name, "Nombre")
        safe_service = validate_text_field(booking.service, "Servicio")
        safe_contact = validate_contact(booking.contact)

        # Validar fecha
        safe_date = parse_date(str(booking.date))
        if is_closed_day(safe_date):
            raise ValueError("Día cerrado o pasado")

        # Validar hora
        safe_time = booking.time
        if safe_time not in WORKING_HOURS:
            raise ValueError("Hora inválida")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        # Guardar reserva usando los datos sanitizados
        booking_uuid = save_booking(BookingRequest(
            name=safe_name,
            service=safe_service,
            date=safe_date,
            time=safe_time,
            contact=safe_contact
        ))
    except Exception:
        raise HTTPException(status_code=409, detail="Hora no disponible")

    # Notificación al usuario
    background_tasks.add_task(
        send_booking_notification,
        safe_contact,
        safe_name,
        safe_service,
        safe_date,
        safe_time,
        booking_uuid 
    )

    return {"status": "ok", "booking_uuid": booking_uuid}




@router.post("/modify")
@limiter.limit("10/minute")
def modify_booking(request: Request, decision: dict, background_tasks: BackgroundTasks):
    booking_uuid = decision.get("booking_uuid")
    contact = decision.get("contact")
    new_date = decision.get("new_date")
    new_time = decision.get("new_time")

    if not booking_uuid or not contact or not new_date or not new_time:
        raise HTTPException(status_code=400, detail="Faltan datos para modificar la reserva")

    try:
        safe_contact = validate_contact(contact)
        safe_new_date = parse_date(str(new_date))
        if is_closed_day(safe_new_date):
            raise ValueError("Fecha inválida")
        if new_time not in WORKING_HOURS:
            raise ValueError("Hora inválida")
        if new_time in get_booked_hours(safe_new_date):
            raise ValueError("Hora ya reservada")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    booking = get_booking_by_uuid(booking_uuid)
    if not booking or booking[6] != safe_contact:  # booking[6] es el contacto
        raise HTTPException(status_code=404, detail="Reserva no encontrada o contacto incorrecto")

    safe_name = validate_text_field(booking[2], "Nombre")
    safe_service = validate_text_field(booking[3], "Servicio")
    safe_new_time = html.escape(new_time)

    try:
        update_booking(booking_uuid, safe_new_date, new_time)
    except Exception as e:
        raise HTTPException(status_code=409, detail=str(e))

    background_tasks.add_task(
        send_booking_notification,
        safe_contact,
        safe_name,
        safe_service,
        safe_new_date,
        safe_new_time,
        booking_uuid,
    )

    return {"status": "ok", "message": "Reserva modificada correctamente"}


@router.post("/cancel")
@limiter.limit("5/minute")
def cancel_booking(request: Request, decision: dict, background_tasks: BackgroundTasks):
    booking_uuid = decision.get("booking_uuid")
    contact = decision.get("contact")
    
    if not booking_uuid or not contact:
        raise HTTPException(status_code=400, detail="Faltan datos para cancelar la reserva")

    safe_contact = validate_contact(contact)
    booking = get_booking_by_uuid(booking_uuid)
    if not booking or booking[6] != safe_contact:
        raise HTTPException(status_code=404, detail="Reserva no encontrada o contacto incorrecto")

    safe_name = validate_text_field(booking[2], "Nombre")
    safe_service = validate_text_field(booking[3], "Servicio")
    safe_date = html.escape(str(booking[4]))
    safe_time = html.escape(booking[5])

    try:
        delete_booking(booking_uuid)
    except Exception as e:
        raise HTTPException(status_code=409, detail=str(e))

    background_tasks.add_task(
        send_booking_notification,
        safe_contact,
        safe_name,
        safe_service,
        safe_date,
        safe_time,
        booking_uuid,
        cancelled=True
    )

    return {"status": "ok", "message": "Reserva cancelada correctamente"}
