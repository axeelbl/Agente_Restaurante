from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.backend.Bots.chat_routes import router as chat_router
from app.backend.booking.booking_routes import router as booking_router
from app.backend.booking.database import get_connection
from app.backend.core.cors import setup_cors
from app.backend.core.security import setup_security
from app.backend.core.startup import init_services


FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_services()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="Mesa Viva API", version="2.1", lifespan=lifespan)

    setup_security(app)
    app.include_router(chat_router)
    app.include_router(booking_router)
    setup_cors(app)

    @app.get("/health", tags=["operations"])
    def healthcheck():
        connection = get_connection()
        try:
            connection.execute("SELECT 1").fetchone()
        finally:
            connection.close()
        return {"status": "ok"}

    # Keep this mount last so API routes take precedence. Relative frontend URLs
    # then work both at / locally and behind a reverse-proxy subpath.
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
    return app
