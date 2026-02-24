from .database import get_connection
import random
import string

def generate_public_id(length=8):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))

# ------------------------------
# Consultar horas ya reservadas
# ------------------------------
def get_booked_hours(date: str) -> list[str]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT time FROM bookings WHERE date = ?",
        (date,)
    )

    rows = cursor.fetchall()
    conn.close()

    return [row[0] for row in rows]


# ------------------------------
# Guardar reserva nueva con UUID
# ------------------------------
def save_booking(booking):
    conn = get_connection()
    cursor = conn.cursor()

    # Generar UUID
    while True:
        booking_uuid = generate_public_id()
        cursor.execute("SELECT 1 FROM bookings WHERE booking_uuid = ?", (booking_uuid,))
        if cursor.fetchone() is None:
            break
    
    cursor.execute("""
        INSERT INTO bookings (booking_uuid, name, service, date, time, contact)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        booking_uuid,
        booking.name,
        booking.service,
        str(booking.date),
        booking.time,
        booking.contact
    ))

    conn.commit()
    conn.close()
    
    # Devolver el UUID para enviarlo al usuario
    return booking_uuid


# ------------------------------
# Buscar reserva por UUID
# ------------------------------
def get_booking_by_uuid(booking_uuid: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, booking_uuid, name, service, date, time, contact FROM bookings WHERE booking_uuid = ?",
        (booking_uuid,)
    )
    row = cursor.fetchone()
    conn.close()
    return row  # None si no existe


# ------------------------------
# Modificar reserva por UUID
# ------------------------------
def update_booking(booking_uuid: str, new_date: str, new_time: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE bookings
        SET date = ?, time = ?
        WHERE booking_uuid = ?
    """, (new_date, new_time, booking_uuid))

    if cursor.rowcount == 0:
        conn.close()
        raise Exception("Reserva no encontrada")

    conn.commit()
    conn.close()


# ------------------------------
# Anular reserva por UUID
# ------------------------------
def delete_booking(booking_uuid: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM bookings WHERE booking_uuid = ?",
        (booking_uuid,)
    )

    if cursor.rowcount == 0:
        conn.close()
        raise Exception("No se encontró ninguna reserva con ese ID")

    conn.commit()
    conn.close()