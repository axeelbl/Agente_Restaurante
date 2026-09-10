import html
import re

from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded


def get_client_key(request):
    ip = request.client.host if request.client else "unknown"
    lang = request.headers.get("accept-language", "")
    return f"{ip}:{lang}"


limiter = Limiter(key_func=get_client_key)


async def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Demasiadas peticiones. Intenta más tarde."},
    )


def setup_security(app):
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

    @app.middleware("http")
    async def security_headers(request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "img-src 'self' data:; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "font-src 'self';"
        )
        return response


def validate_text_field(value: str, field_name: str, max_length=50) -> str:
    if not value or not value.strip():
        raise ValueError(f"{field_name} no puede estar vacío")

    value = value.strip()
    if len(value) > max_length:
        raise ValueError(f"{field_name} demasiado largo")
    if not re.match(r"^[A-Za-zÀ-ÿ0-9\s.,'-]+$", value):
        raise ValueError(f"{field_name} contiene caracteres no permitidos")
    return value


def validate_contact(contact: str | None) -> str | None:
    if contact is None:
        return None

    contact = contact.strip()
    email_regex = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    phone_candidate = re.sub(r"[\s().-]+", "", contact)
    phone_regex = r"^\+?\d{7,15}$"

    if re.fullmatch(email_regex, contact):
        return html.escape(contact)
    if re.fullmatch(phone_regex, phone_candidate):
        return html.escape(phone_candidate)
    raise ValueError("Contacto inválido (email o teléfono)")
