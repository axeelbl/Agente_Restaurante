import time

from fastapi import APIRouter, BackgroundTasks, Request
from pydantic import BaseModel

from app.backend.Bots.chat import decide_and_extract_booking
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
    user_message: str


@router.post("/chat")
@limiter.limit("20/minute")
async def chat_endpoint(
    msg: MessageRequest,
    request: Request,
    background_tasks: BackgroundTasks,
):
    user_message = msg.user_message
    if len(user_message) > 500:
        return {"bot_message": "Mensaje demasiado largo."}

    decision = decide_and_extract_booking(user_message)
    start_time = time.time()

    def record_lead(bot_reply: str):
        meta = {
            "ip": request.client.host,
            "user_agent": request.headers.get("user-agent", ""),
            "language": request.headers.get("accept-language", ""),
            "referer": request.headers.get("referer", ""),
            "response_time": round(time.time() - start_time, 2),
        }
        save_lead(user_message, bot_reply, meta)
        try:
            send_csv_email()
        except Exception as exc:
            print("Error enviando CSV:", exc)

    if decision.get("action") == "RESERVAR":
        response = handle_booking(decision, background_tasks)
        record_lead(response["bot_message"])
        return response

    if decision.get("action") == "CHECK_AVAILABILITY":
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
        record_lead(response["bot_message"])
        return response

    if decision.get("action") == "MODIFY_BOOKING":
        response = handle_modify_booking(decision, background_tasks)
        record_lead(response["bot_message"])
        return response

    if decision.get("action") == "CANCEL_BOOKING":
        response = handle_cancel_booking(decision, background_tasks)
        record_lead(response["bot_message"])
        return response

    restaurant_response = handle_restaurant_request(user_message, decision.get("action"))
    if restaurant_response:
        record_lead(restaurant_response["bot_message"])
        return restaurant_response

    response = handle_chat(user_message, request)
    record_lead(response["bot_message"])
    return response
