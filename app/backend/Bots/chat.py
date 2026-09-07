import json
import re

from groq import Groq

from ..config import GROQ_API_KEY
from .Prompts import BOOKING_DECISION_PROMPT
from app.backend.services.restaurant_service import normalize_text


client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
MODEL = "llama-3.3-70b-versatile"


def ask_groq(messages, temperature=0.9):
    if client is None:
        raise RuntimeError("Groq no configurado")

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content


def extract_contact(message: str):
    match = re.search(
        r"([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}|\+?\d{7,15})",
        message,
    )
    return match.group(1) if match else None


def extract_date(message: str):
    match = re.search(
        r"\b(\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?|\d{4}-\d{2}-\d{2}|hoy|manana|mañana)\b",
        message,
    )
    return match.group(1) if match else None


def extract_time(message: str):
    match = re.search(r"\b(\d{1,2}[:.]\d{2})\b", message)
    if match:
        return match.group(1).replace(".", ":")

    hour_match = re.search(r"(?:a las|sobre las|hacia las)\s+(\d{1,2})\b", message)
    if hour_match:
        return f"{int(hour_match.group(1)):02d}:00"

    return None


def extract_party_size(message: str):
    match = re.search(
        r"\b(\d{1,2})\s*(?:personas|persona|comensales|adultos|cubiertos)\b",
        message,
    )
    if match:
        return int(match.group(1))

    para_match = re.search(r"\bpara\s+(\d{1,2})\b", message)
    if para_match:
        return int(para_match.group(1))

    return None


def extract_booking_uuid(message: str):
    match = re.search(
        r"(?:id|codigo|codigo de reserva|reserva)\s*[:#]?\s*([A-Z0-9]{6,12})",
        message,
        re.IGNORECASE,
    )
    return match.group(1).upper() if match else None


def extract_name(message: str):
    match = re.search(
        r"(?:me llamo|soy|a nombre de|nombre(?: es)?)[\s:]+([A-Za-zÀ-ÿ' -]{2,40})",
        message,
        re.IGNORECASE,
    )
    if not match:
        return None
    return match.group(1).strip(" .,-")


def extract_notes(message: str):
    normalized = normalize_text(message)
    notes = []
    for keyword in ["terraza", "interior", "trona", "alergia", "cumpleanos", "ventana"]:
        if keyword in normalized:
            notes.append(keyword)

    note_match = re.search(r"(?:observaciones?|nota|detalle)[:\s]+(.+)$", message, re.IGNORECASE)
    if note_match:
        notes.append(note_match.group(1).strip())

    if not notes:
        return None
    return ", ".join(dict.fromkeys(notes))


def local_decide_and_extract_booking(user_message: str):
    normalized = normalize_text(user_message)

    booking = {
        "name": extract_name(user_message),
        "date": extract_date(normalized),
        "time": extract_time(normalized),
        "party_size": extract_party_size(normalized),
        "contact": extract_contact(user_message),
        "notes": extract_notes(user_message),
        "booking_uuid": extract_booking_uuid(user_message),
    }

    if any(pattern in normalized for pattern in ["foto", "fotos", "imagen", "imagenes", "carta visual"]):
        return {"action": "SHOW_PHOTOS", "booking": booking, "availability_date": booking["date"]}

    if any(pattern in normalized for pattern in ["carta", "menu del dia", "menu de hoy", "postres", "bebidas", "sugerencias"]):
        return {"action": "SHOW_MENU", "booking": booking, "availability_date": booking["date"]}

    if any(
        pattern in normalized
        for pattern in [
            "que me recomiendas",
            "recomiendame",
            "algo ligero",
            "algo rapido",
            "algo barato",
            "vegetar",
            "vegano",
            "sin carne",
            "carne",
            "pescado",
            "plato tipico",
            "especialidad",
        ]
    ):
        return {"action": "RECOMMEND_DISH", "booking": booking, "availability_date": booking["date"]}

    faq_patterns = [
        "horario",
        "direccion",
        "ubicacion",
        "telefono",
        "terraza",
        "mascotas",
        "alergenos",
        "gluten",
        "parking",
        "bizum",
        "tarjeta",
        "llevar",
        "domicilio",
        "grupos",
    ]
    if any(pattern in normalized for pattern in faq_patterns):
        return {"action": "SHOW_FAQ", "booking": booking, "availability_date": booking["date"]}

    if any(pattern in normalized for pattern in ["cancelar", "anular reserva", "cancela mi reserva"]):
        return {"action": "CANCEL_BOOKING", "booking": booking, "availability_date": booking["date"]}

    if any(
        pattern in normalized
        for pattern in ["modificar reserva", "cambiar", "mover reserva", "reprogramar reserva"]
    ):
        return {"action": "MODIFY_BOOKING", "booking": booking, "availability_date": booking["date"]}

    if any(
        pattern in normalized
        for pattern in ["quiero reservar", "reservar mesa", "hacer una reserva", "reserva para"]
    ):
        return {"action": "RESERVAR", "booking": booking, "availability_date": booking["date"]}

    if any(
        pattern in normalized
        for pattern in ["disponibilidad", "hay mesa", "teneis mesa", "hueco", "sitio", "mesa para"]
    ):
        return {"action": "CHECK_AVAILABILITY", "booking": booking, "availability_date": booking["date"]}

    return {"action": "CHAT", "booking": booking, "availability_date": booking["date"]}


def decide_and_extract_booking(user_message):
    local_response = local_decide_and_extract_booking(user_message)
    if local_response["action"] != "CHAT" or client is None:
        return local_response

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": BOOKING_DECISION_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0,
        )
    except Exception:
        return local_response

    content = response.choices[0].message.content

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return local_response


REQUIRED_FIELDS = ["name", "date", "time", "party_size", "contact"]


def is_complete_booking(booking):
    return all(booking.get(field) for field in REQUIRED_FIELDS)
