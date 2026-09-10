import time

from fastapi import APIRouter, BackgroundTasks, Request
from pydantic import BaseModel, Field

from app.backend.Bots.chat import decide_and_extract_booking
from app.backend.config import LEAD_LOGGING_ENABLED
from app.backend.core.security import limiter
from app.backend.csv_utils import save_lead
from app.backend.email_utils import send_csv_email
from app.backend.services.booking_service import (
    handle_availability,
    handle_availability_overview,
    handle_booking,
    handle_cancel_booking,
    handle_modify_booking,
)
from app.backend.services.chat_service import handle_chat
from app.backend.services.restaurant_service import handle_restaurant_request


router = APIRouter()


class MessageRequest(BaseModel):
    user_message: str = Field(min_length=1, max_length=500)


def record_lead(user_message: str, bot_reply: str, response_time: float) -> None:
    if not LEAD_LOGGING_ENABLED:
        return

    save_lead(
        user_message,
        bot_reply,
        {
            "ip": "",
            "user_agent": "",
            "language": "",
            "referer": "",
            "response_time": response_time,
        },
    )
    send_csv_email()


@router.post("/chat")
@limiter.limit("20/minute")
def chat_endpoint(
    msg: MessageRequest,
    request: Request,
    background_tasks: BackgroundTasks,
):
    user_message = msg.user_message.strip()
    if not user_message:
        return {"bot_message": "Escribe un mensaje para continuar."}

    start_time = time.monotonic()
    decision = decide_and_extract_booking(user_message)

    if decision.get("action") == "RESERVAR":
        response = handle_booking(decision, background_tasks)
    elif decision.get("action") == "CHECK_AVAILABILITY":
        booking_data = decision.get("booking", {})
        if decision.get("availability_date") or booking_data.get("date"):
            response = handle_availability(decision)
        else:
            party_size = booking_data.get("party_size") or 2
            try:
                party_size = int(party_size)
            except (TypeError, ValueError):
                party_size = 2
            response = handle_availability_overview(party_size=party_size)
    elif decision.get("action") == "MODIFY_BOOKING":
        response = handle_modify_booking(decision, background_tasks)
    elif decision.get("action") == "CANCEL_BOOKING":
        response = handle_cancel_booking(decision, background_tasks)
    else:
        response = handle_restaurant_request(user_message, decision.get("action"))
        if response is None:
            response = handle_chat(user_message, request)

    if LEAD_LOGGING_ENABLED:
        elapsed = round(time.monotonic() - start_time, 2)
        background_tasks.add_task(record_lead, user_message, response["bot_message"], elapsed)
    return response
