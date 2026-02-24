import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from app.backend.core.cors import setup_cors
from app.backend.core.startup import init_services
from app.backend.Bots.chat_routes import router as chat_router
from app.backend.booking.booking_routes import router as booking_router

from app.backend.core.security import setup_security

# Base del proyecto (carpeta "app")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

def create_app() -> FastAPI:
    app = FastAPI(title="AxelBot API", version="1.0")
    
    setup_security(app)

    # Init DB y servicios
    init_services()

    # Routers
    app.include_router(chat_router)
    app.include_router(booking_router)

    # CORS
    setup_cors(app)

    # Frontend
    app.mount(
        "/static",
        StaticFiles(directory=os.path.join(BASE_DIR, "frontend")),
        name="static"
    )

    # Root
    @app.get("/")
    async def root():
        index_path = os.path.join(BASE_DIR, "frontend", "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"error": "Archivo index.html no encontrado."}

    return app


