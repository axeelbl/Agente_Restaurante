from app.backend.booking.database import init_db
from dotenv import load_dotenv

def init_services():
    load_dotenv()
    init_db()
