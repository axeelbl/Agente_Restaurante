from pydantic import BaseModel
from datetime import date
from typing import Optional

class BookingRequest(BaseModel):
    name: str
    service: str
    date: date
    time: str
    contact: str
    booking_uuid: Optional[str] = None  # UUID generado por el sistema, opcional al crear