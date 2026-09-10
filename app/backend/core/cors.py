import os

from fastapi.middleware.cors import CORSMiddleware


def _allowed_origins() -> list[str]:
    configured = os.getenv("CORS_ORIGINS", "http://localhost,http://127.0.0.1")
    return [origin.strip().rstrip("/") for origin in configured.split(",") if origin.strip()]


def setup_cors(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_allowed_origins(),
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type"],
    )
