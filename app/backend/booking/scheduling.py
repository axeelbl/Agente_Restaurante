from __future__ import annotations

from datetime import datetime, timedelta

from dateutil import parser

from app.backend.booking.repository import get_bookings_for_date


RESERVATION_DURATION_MINUTES = 90
TABLE_LAYOUT = [2, 2, 2, 4, 4, 4, 6, 8]
MAX_PARTY_SIZE = max(TABLE_LAYOUT)
HOLIDAYS = [
    "2026-01-01",
    "2026-12-25",
    "2026-12-26",
]


def build_slots(start_hour: int, start_minute: int, end_hour: int, end_minute: int) -> list[str]:
    slots = []
    current = start_hour * 60 + start_minute
    end = end_hour * 60 + end_minute

    while current <= end:
        slots.append(f"{current // 60:02d}:{current % 60:02d}")
        current += 30

    return slots


WORKING_HOURS = build_slots(13, 0, 15, 30) + build_slots(20, 0, 23, 0)


def is_closed_day(date_str: str) -> bool:
    date = datetime.strptime(date_str, "%Y-%m-%d")
    today = datetime.today().date()

    if date.date() < today:
        return True

    if date.weekday() == 0:
        return True

    if date_str in HOLIDAYS:
        return True

    return False


def parse_date(date_str: str) -> str:
    date_str = date_str.strip().lower()

    if date_str in ["hoy", "today"]:
        return datetime.today().strftime("%Y-%m-%d")

    if date_str in ["mañana", "mañana", "tomorrow"]:
        return (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")

    try:
        dt = parser.parse(date_str, dayfirst=True, fuzzy=True)
        return dt.strftime("%Y-%m-%d")
    except Exception as exc:
        raise ValueError("No se pudo interpretar la fecha") from exc


def parse_time_flexible(time_str: str) -> int:
    processed = preprocess_time_string(time_str)

    try:
        dt = parser.parse(processed, fuzzy=True)
    except Exception as exc:
        raise ValueError("No se pudo interpretar la hora") from exc

    return dt.hour * 60 + dt.minute


def parse_party_size(value) -> int:
    try:
        party_size = int(str(value).strip())
    except (TypeError, ValueError) as exc:
        raise ValueError("El número de comensales no es válido.") from exc

    if party_size < 1:
        raise ValueError("El número de comensales debe ser de al menos 1.")

    if party_size > MAX_PARTY_SIZE:
        raise ValueError(
            f"Ahora mismo gestiónamos reservas online de hasta {MAX_PARTY_SIZE} personas."
        )

    return party_size


def slot_to_minutes(slot: str) -> int:
    hour, minute = map(int, slot.split(":"))
    return hour * 60 + minute


def overlap(start_a: int, end_a: int, start_b: int, end_b: int) -> bool:
    return start_a < end_b and start_b < end_a


def can_allocate_tables(parties: list[int]) -> bool:
    available_tables = sorted(TABLE_LAYOUT)

    for party_size in sorted(parties, reverse=True):
        selected_index = None
        for index, capacity in enumerate(available_tables):
            if capacity >= party_size:
                selected_index = index
                break

        if selected_index is None:
            return False

        available_tables.pop(selected_index)

    return True


def get_overlapping_parties(date: str, time_str: str, exclude_booking_uuid: str | None = None) -> list[int]:
    candidate_start = slot_to_minutes(time_str)
    candidate_end = candidate_start + RESERVATION_DURATION_MINUTES

    parties: list[int] = []
    for booking in get_bookings_for_date(date):
        if exclude_booking_uuid and booking["booking_uuid"] == exclude_booking_uuid:
            continue

        start = slot_to_minutes(booking["time"])
        end = start + RESERVATION_DURATION_MINUTES
        if overlap(candidate_start, candidate_end, start, end):
            parties.append(int(booking["party_size"]))

    return parties


def is_slot_available(
    date: str,
    time_str: str,
    party_size: int,
    exclude_booking_uuid: str | None = None,
) -> bool:
    if time_str not in WORKING_HOURS:
        return False

    existing_parties = get_overlapping_parties(date, time_str, exclude_booking_uuid)
    return can_allocate_tables(existing_parties + [party_size])


def get_available_slots(
    date: str,
    party_size: int,
    exclude_booking_uuid: str | None = None,
) -> list[str]:
    return [
        slot
        for slot in WORKING_HOURS
        if is_slot_available(date, slot, party_size, exclude_booking_uuid)
    ]


def get_nearby_free_slots(
    date: str,
    target_minutes: int,
    party_size: int,
    max_options: int = 3,
    exclude_booking_uuid: str | None = None,
):
    slots = []
    for slot in get_available_slots(date, party_size, exclude_booking_uuid):
        slot_minutes = slot_to_minutes(slot)
        slots.append((abs(slot_minutes - target_minutes), slot))

    slots.sort(key=lambda item: item[0])
    return [slot for _, slot in slots[:max_options]]


def replace_common_expressions(text: str) -> str:
    text = text.lower()
    text = text.replace("y cuarto", ":15")
    text = text.replace("y medía", ":30")
    text = text.replace("y 1/2", ":30")
    text = text.replace("menos cuarto", ":45")
    text = text.replace(": ", ":")
    text = text.replace(".", ":")
    return text


NUM_WORDS = {
    "una": 1,
    "un": 1,
    "dos": 2,
    "tres": 3,
    "cuatro": 4,
    "cinco": 5,
    "seis": 6,
    "siete": 7,
    "ocho": 8,
    "nueve": 9,
    "diez": 10,
    "once": 11,
    "doce": 12,
}


def words_to_numbers(text: str) -> str:
    for word, number in NUM_WORDS.items():
        text = text.replace(word, str(number))
    return text


def normalize_period(text: str) -> str:
    text = text.replace("del mediodía", "PM")
    text = text.replace("de la mañana", "AM")
    text = text.replace("de la mañana", "AM")
    text = text.replace("de la tarde", "PM")
    text = text.replace("de la noche", "PM")
    return text


def preprocess_time_string(text: str) -> str:
    text = text.lower().strip()
    text = replace_common_expressions(text)
    text = words_to_numbers(text)
    text = normalize_period(text)
    return text
