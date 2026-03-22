from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class BookingRequest(BaseModel):
    name: str
    date: date
    time: str
    party_size: int = Field(ge=1, le=8)
    contact: str
    notes: Optional[str] = ""
    booking_uuid: Optional[str] = None
