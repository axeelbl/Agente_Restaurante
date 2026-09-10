import secrets
import string

from .database import BOOKINGS_TABLE, get_connection


def generate_public_id(length=8):
    chars = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))


def get_bookings_for_date(date: str) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        f"""
        SELECT id, booking_uuid, name, date, time, contact, party_size, notes
        FROM {BOOKINGS_TABLE}
        WHERE date = ?
        ORDER BY time ASC, party_size DESC
        """,
        (date,),
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_booked_hours(date: str) -> list[str]:
    bookings = get_bookings_for_date(date)
    return sorted({booking["time"] for booking in bookings})


def find_duplicate_booking(contact: str, date: str, time: str, exclude_booking_uuid: str | None = None):
    conn = get_connection()
    cursor = conn.cursor()

    query = f"""
        SELECT booking_uuid
        FROM {BOOKINGS_TABLE}
        WHERE contact = ? AND date = ? AND time = ?
    """
    params: list[str] = [contact, date, time]

    if exclude_booking_uuid:
        query += " AND booking_uuid != ?"
        params.append(exclude_booking_uuid)

    cursor.execute(query, tuple(params))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def save_booking(booking):
    conn = get_connection()
    cursor = conn.cursor()

    while True:
        booking_uuid = generate_public_id()
        cursor.execute(
            f"SELECT 1 FROM {BOOKINGS_TABLE} WHERE booking_uuid = ?",
            (booking_uuid,),
        )
        if cursor.fetchone() is None:
            break

    cursor.execute(
        f"""
        INSERT INTO {BOOKINGS_TABLE} (
            booking_uuid, name, date, time, contact, party_size, notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            booking_uuid,
            booking.name,
            str(booking.date),
            booking.time,
            booking.contact,
            booking.party_size,
            booking.notes or "",
        ),
    )

    conn.commit()
    conn.close()
    return booking_uuid


def get_booking_by_uuid(booking_uuid: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        f"""
        SELECT id, booking_uuid, name, date, time, contact, party_size, notes
        FROM {BOOKINGS_TABLE}
        WHERE booking_uuid = ?
        """,
        (booking_uuid,),
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_booking(
    booking_uuid: str,
    new_date: str,
    new_time: str,
    new_party_size: int,
    new_notes: str = "",
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        f"""
        UPDATE {BOOKINGS_TABLE}
        SET date = ?, time = ?, party_size = ?, notes = ?
        WHERE booking_uuid = ?
        """,
        (new_date, new_time, new_party_size, new_notes or "", booking_uuid),
    )

    if cursor.rowcount == 0:
        conn.close()
        raise Exception("Reserva no encontrada")

    conn.commit()
    conn.close()


def delete_booking(booking_uuid: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        f"DELETE FROM {BOOKINGS_TABLE} WHERE booking_uuid = ?",
        (booking_uuid,),
    )

    if cursor.rowcount == 0:
        conn.close()
        raise Exception("No se ha encontrado ninguna reserva con ese ID")

    conn.commit()
    conn.close()
