from datetime import date

from pydantic import BaseModel, Field, field_validator


BOOKING_ID_PATTERN = r"^[A-Z0-9]{6,12}$"


class BookingRequest(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    date: date
    time: str = Field(pattern=r"^\d{1,2}:\d{2}$")
    party_size: int = Field(ge=1, le=8)
    contact: str = Field(min_length=7, max_length=254)
    notes: str = Field(default="", max_length=120)
    booking_uuid: str | None = Field(default=None, pattern=BOOKING_ID_PATTERN)


class BookingModifyRequest(BaseModel):
    booking_uuid: str = Field(pattern=BOOKING_ID_PATTERN)
    contact: str = Field(min_length=7, max_length=254)
    new_date: date | None = None
    new_time: str | None = Field(default=None, pattern=r"^\d{1,2}:\d{2}$")
    new_party_size: int | None = Field(default=None, ge=1, le=8)
    new_notes: str | None = Field(default=None, max_length=120)

    @field_validator("booking_uuid", mode="before")
    @classmethod
    def normalize_booking_uuid(cls, value):
        return str(value).strip().upper()

    @field_validator("new_date", "new_time", "new_party_size", "new_notes", mode="before")
    @classmethod
    def blank_change_is_omitted(cls, value):
        return None if value == "" else value


class BookingCancelRequest(BaseModel):
    booking_uuid: str = Field(pattern=BOOKING_ID_PATTERN)
    contact: str = Field(min_length=7, max_length=254)

    @field_validator("booking_uuid", mode="before")
    @classmethod
    def normalize_booking_uuid(cls, value):
        return str(value).strip().upper()
