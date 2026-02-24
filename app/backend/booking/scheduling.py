from datetime import datetime, timedelta
from dateutil import parser

from app.backend.booking.repository import get_booked_hours


WORKING_HOURS = [
    "09:00","09:30","10:00","10:30","11:00","11:30","12:00","12:30","13:00","13:30",
    "16:00","16:30","17:00","17:30","18:00","18:30","19:00","19:30","20:00","20:30",
]

HOLIDAYS = [
    "2026-01-01",
    "2026-12-25",
    "2026-12-26",
    "2026-02-05",
]

def is_closed_day(date_str: str) -> bool:
    """
    Retorna True si la fecha es:
    - Domingo
    - Festivo
    - Fecha pasada
    """
    date = datetime.strptime(date_str, "%Y-%m-%d")
    today = datetime.today().date()

    # Fecha pasada
    if date.date() < today:
        return True

    # Domingo
    if date.weekday() == 6:
        return True

    # Festivo
    if date_str in HOLIDAYS:
        return True

    return False


def parse_date(date_str: str) -> str:
    """
    Convierte casi cualquier formato humano a YYYY-MM-DD
    """
    date_str = date_str.strip().lower()

    # Casos naturales
    if date_str in ["hoy", "today"]:
        return datetime.today().strftime("%Y-%m-%d")

    if date_str in ["mañana", "manana", "tomorrow"]:
        return (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")

    try:
        dt = parser.parse(
            date_str,
            dayfirst=True,      # Importante en España
            fuzzy=True          # Ignora texto basura
        )
        return dt.strftime("%Y-%m-%d")
    except Exception:
        raise ValueError("No se pudo interpretar la fecha")
    

def parse_time_flexible(time_str: str) -> int:
    """
    Interpreta casi cualquier hora humana y devuelve minutos desde 00:00
    """
    s = preprocess_time_string(time_str)

    try:
        dt = parser.parse(s, fuzzy=True)
    except Exception:
        raise ValueError("No se pudo interpretar la hora")

    return dt.hour * 60 + dt.minute

def get_nearby_free_slots(date: str, target_minutes: int, max_options=3):
    booked = set(get_booked_hours(date))

    slots = []
    for h in WORKING_HOURS:
        if h in booked:
            continue

        hour, minute = map(int, h.split(":"))
        slot_minutes = hour * 60 + minute
        slots.append((abs(slot_minutes - target_minutes), h))

    slots.sort(key=lambda x: x[0])
    return [h for _, h in slots[:max_options]]


# LO DE ABAJO ES PARA ACEPTAR LA HORA DE TODAS LAS MANERAS POSIBLES

def replace_common_expressions(s: str) -> str:
    s = s.lower()
    s = s.replace("y cuarto", ":15")
    s = s.replace("y media", ":30")
    s = s.replace("y 1/2", ":30")
    s = s.replace("menos cuarto", ":45")
    s = s.replace(": ", ":")  # limpiar espacios extra
    return s

NUM_WORDS = {
    "una": 1, "un": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5,
    "seis": 6, "siete": 7, "ocho": 8, "nueve": 9, "diez": 10,
    "once": 11, "doce": 12,
}

def words_to_numbers(s: str) -> str:
    for word, num in NUM_WORDS.items():
        s = s.replace(word, str(num))
    return s

def normalize_period(s: str) -> str:
    s = s.replace("de la mañana", "AM")
    s = s.replace("de la tarde", "PM")
    s = s.replace("de la noche", "PM")  # puedes ajustar si quieres distinguir
    return s

def preprocess_time_string(s: str) -> str:
    s = s.lower().strip()
    s = replace_common_expressions(s)
    s = words_to_numbers(s)
    s = normalize_period(s)
    return s