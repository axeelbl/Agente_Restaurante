from fastapi import APIRouter, BackgroundTasks, HTTPException, Request

from .models import BookingCancelRequest, BookingModifyRequest, BookingRequest
from .scheduling import get_available_slots, is_closed_day, parse_date, parse_party_size
from app.backend.core.security import limiter
from app.backend.services.booking_service import (
    handle_booking,
    handle_cancel_booking,
    handle_modify_booking,
)


router = APIRouter(prefix="/booking", tags=["booking"])


@router.get("/availability")
@limiter.limit("60/minute")
def availability(request: Request, date: str, party_size: int = 2, booking_uuid: str | None = None):
    try:
        safe_date = parse_date(date)
        safe_party_size = parse_party_size(party_size)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if is_closed_day(safe_date):
        return []

    return get_available_slots(safe_date, safe_party_size, booking_uuid)


@router.post("/reserve")
@limiter.limit("20/minute")
def reserve(request: Request, booking: BookingRequest, background_tasks: BackgroundTasks):
    response = handle_booking({"booking": booking.model_dump(mode="json")}, background_tasks)
    if response.get("booking_uuid"):
        return {"status": "ok", "booking_uuid": response["booking_uuid"]}
    raise HTTPException(status_code=400, detail=response["bot_message"])


@router.post("/modify")
@limiter.limit("10/minute")
def modify_booking(
    request: Request,
    decision: BookingModifyRequest,
    background_tasks: BackgroundTasks,
):
    data = decision.model_dump(mode="json")
    response = handle_modify_booking(
        {
            "booking": {
                "booking_uuid": data["booking_uuid"],
                "contact": data["contact"],
                "date": data["new_date"],
                "time": data["new_time"],
                "party_size": data["new_party_size"],
                "notes": data["new_notes"],
            }
        },
        background_tasks,
    )

    if response["bot_message"].startswith("Perfecto"):
        return {"status": "ok", "message": response["bot_message"]}
    raise HTTPException(status_code=400, detail=response["bot_message"])


@router.post("/cancel")
@limiter.limit("5/minute")
def cancel_booking(
    request: Request,
    decision: BookingCancelRequest,
    background_tasks: BackgroundTasks,
):
    data = decision.model_dump(mode="json")
    response = handle_cancel_booking({"booking": data}, background_tasks)
    if "ha sido cancelada correctamente" in response["bot_message"]:
        return {"status": "ok", "message": response["bot_message"]}
    raise HTTPException(status_code=400, detail=response["bot_message"])
