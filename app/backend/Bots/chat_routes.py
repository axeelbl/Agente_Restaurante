from fastapi import APIRouter, Request, BackgroundTasks
from pydantic import BaseModel

from app.backend.Bots.chat import decide_and_extract_booking
from app.backend.services.booking_service import handle_booking, handle_availability, handle_availability_overview, handle_modify_booking, handle_cancel_booking
from app.backend.services.chat_service import handle_chat
from app.backend.services.recommend_cut import recommend_cut_by_text
from app.backend.csv_utils import save_lead
from app.backend.email_utils import send_csv_email
import time

from app.backend.core.security import limiter

router = APIRouter()

class MessageRequest(BaseModel):
    user_message: str

@router.post("/chat")
@limiter.limit("20/minute")
async def chat_endpoint(
    msg: MessageRequest,
    request: Request,
    background_tasks: BackgroundTasks
):
    user_message = msg.user_message
    if len(user_message) > 500:
        return {"bot_message": "Mensaje demasiado largo."}
    decision = decide_and_extract_booking(user_message)

    # Función para guardar lead y enviar CSV
    def record_lead(bot_reply: str):
        meta = {
            "ip": request.client.host,
            "user_agent": request.headers.get("user-agent", ""),
            "language": request.headers.get("accept-language", ""),
            "referer": request.headers.get("referer", ""),
            "response_time": round(time.time() - start_time, 2)
        }
        save_lead(user_message, bot_reply, meta)
        try:
            send_csv_email()
        except Exception as e:
            print("Error enviando CSV:", e)

    start_time = time.time()  # Para medir tiempo de respuesta

    # RESERVA
    if decision.get("action") == "RESERVAR":
        response = handle_booking(decision, background_tasks)
        record_lead(response["bot_message"])
        return response

    # DISPONIBILIDAD
    if decision.get("action") == "CHECK_AVAILABILITY":
        if decision.get("availability_date"):
            response = handle_availability(decision.get("availability_date"))
        else:
            response = handle_availability_overview()
        record_lead(response["bot_message"])
        return response

    # MODIFICAR RESERVA
    if decision.get("action") == "MODIFY_BOOKING":
        response = handle_modify_booking(decision, background_tasks)
        record_lead(response["bot_message"])
        return response

    # CANCELAR RESERVA
    if decision.get("action") == "CANCEL_BOOKING":
        response = handle_cancel_booking(decision, background_tasks)
        record_lead(response["bot_message"])
        return response

    # Dentro del endpoint /chat
    if decision.get("action") == "SHOW_PHOTOS":
        response = recommend_cut_by_text(user_message)
        record_lead(response["bot_message"])
        return response
    
    # CHAT normal
    response = handle_chat(user_message, request)
    record_lead(response["bot_message"])
    return response
