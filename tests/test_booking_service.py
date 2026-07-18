import os
import unittest
import uuid
from datetime import date, timedelta

from app.backend.booking.database import init_db
from app.backend.booking.repository import get_booking_by_uuid
from app.backend.booking.scheduling import is_closed_day
from app.backend.services.booking_service import handle_booking


class DummyBackgroundTasks:
    def __init__(self):
        self.tasks = []

    def add_task(self, func, *args, **kwargs):
        self.tasks.append((func, args, kwargs))


def next_open_day():
    current = date.today() + timedelta(days=1)
    while is_closed_day(current.strftime("%Y-%m-%d")):
        current += timedelta(days=1)
    return current


class BookingServiceTests(unittest.TestCase):
    def setUp(self):
        temp_root = os.path.join(os.getcwd(), "tests", ".tmp")
        os.makedirs(temp_root, exist_ok=True)
        self.db_path = os.path.join(temp_root, f"test-bookings-{uuid.uuid4().hex}.db")
        os.environ["BOOKINGS_DB_PATH"] = self.db_path
        init_db()
        self.background_tasks = DummyBackgroundTasks()
        self.open_day = next_open_day()

    def tearDown(self):
        os.environ.pop("BOOKINGS_DB_PATH", None)
        for suffix in ["", "-wal", "-shm"]:
            try:
                os.remove(self.db_path + suffix)
            except FileNotFoundError:
                pass

    def test_valid_booking_is_created(self):
        response = handle_booking(
            {
                "booking": {
                    "name": "Ana Perez",
                    "date": self.open_day.strftime("%d/%m/%Y"),
                    "time": "21:00",
                    "party_size": 4,
                    "contact": "+34910123456",
                    "notes": "terraza",
                }
            },
            self.background_tasks,
        )

        self.assertIn("Reserva confirmada", response["bot_message"])
        self.assertIn("booking_uuid", response)
        self.assertEqual(len(self.background_tasks.tasks), 1)

        stored_booking = get_booking_by_uuid(response["booking_uuid"])
        self.assertIsNotNone(stored_booking)
        self.assertEqual(stored_booking["party_size"], 4)
        self.assertEqual(stored_booking["notes"], "terraza")

    def test_phone_with_spaces_is_accepted_and_normalized(self):
        response = handle_booking(
            {
                "booking": {
                    "name": "Ana Perez",
                    "date": self.open_day.strftime("%d/%m/%Y"),
                    "time": "21:30",
                    "party_size": 2,
                    "contact": "+34 666 66 66 66",
                }
            },
            self.background_tasks,
        )

        self.assertIn("booking_uuid", response)
        stored_booking = get_booking_by_uuid(response["booking_uuid"])
        self.assertEqual(stored_booking["contact"], "+34666666666")

    def test_past_date_is_rejected(self):
        past_day = date.today() - timedelta(days=1)
        response = handle_booking(
            {
                "booking": {
                    "name": "Luis Gomez",
                    "date": past_day.strftime("%d/%m/%Y"),
                    "time": "21:00",
                    "party_size": 2,
                    "contact": "luis@example.com",
                }
            },
            self.background_tasks,
        )

        self.assertIn("cerrados o ya ha pasado", response["bot_message"])

    def test_full_slot_suggests_nearby_alternatives(self):
        first_response = handle_booking(
            {
                "booking": {
                    "name": "Grupo Grande",
                    "date": self.open_day.strftime("%d/%m/%Y"),
                    "time": "13:00",
                    "party_size": 8,
                    "contact": "+34910000001",
                }
            },
            self.background_tasks,
        )
        self.assertIn("booking_uuid", first_response)

        second_response = handle_booking(
            {
                "booking": {
                    "name": "Otro Grupo",
                    "date": self.open_day.strftime("%d/%m/%Y"),
                    "time": "13:00",
                    "party_size": 8,
                    "contact": "+34910000002",
                }
            },
            self.background_tasks,
        )

        self.assertIn("alternativas", second_response["bot_message"])
        self.assertIn("14:30", second_response["bot_message"])


if __name__ == "__main__":
    unittest.main()
