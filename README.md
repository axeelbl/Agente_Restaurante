# Mesa Viva — asistente de restaurante

Aplicación web de demostración para consultar la carta de un restaurante, recibir recomendaciones y gestionar reservas. Combina un frontend sin framework con una API FastAPI, persistencia SQLite y respuestas locales que pueden ampliarse opcionalmente con Groq.

## Funciones

- Carta, menú del día, alérgenos, recomendaciones y galería de fotos.
- Disponibilidad de mesas y creación, modificación o cancelación de reservas.
- Notificaciones opcionales por Resend (email) o Twilio (SMS).
- Registro de conversaciones opcional y desactivado por defecto.
- Rate limiting, CORS configurable, cabeceras de seguridad y validación de entradas.
- Healthcheck en `GET /health`.

## Requisitos

- Python 3.11 o posterior.
- Node.js solo para comprobar la sintaxis del frontend.

## Instalación

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
uvicorn app.backend.main:app --reload
```

En PowerShell, activa el entorno con `.\.venv\Scripts\Activate.ps1` y copia el ejemplo con `Copy-Item .env.example .env`.

Abre <http://127.0.0.1:8000>. Los recursos y las llamadas API usan rutas relativas, por lo que la misma aplicación puede publicarse detrás de un subpath de proxy inverso.

## Configuración

| Variable | Uso | Valor predeterminado |
| --- | --- | --- |
| `GROQ_API_KEY` | Activa respuestas generativas | Sin IA externa |
| `RESEND_API_KEY`, `RESEND_FROM` | Notificaciones de reservas por email | Desactivadas |
| `RESEND_TO` | Destino del CSV de conversaciones | Desactivado |
| `TWILIO_SID`, `TWILIO_TOKEN`, `TWILIO_PHONE` | Notificaciones por SMS | Desactivadas |
| `BOOKINGS_DB_PATH` | Ruta de SQLite | `app/backend/booking/bookings.db` |
| `LEADS_FILE` | Ruta del CSV opcional | `leads.csv` en la raíz |
| `LEAD_LOGGING_ENABLED` | Guarda mensajes y envía el CSV si Resend está configurado | `false` |
| `CORS_ORIGINS` | Orígenes permitidos, separados por comas | localhost sin puerto |

No uses credenciales reales en archivos versionados. Si activas el registro de conversaciones, informa a los usuarios, define una retención y protege el CSV: puede contener datos personales introducidos en el chat. La aplicación no guarda IP, user-agent ni referer en ese registro.

## Desarrollo y verificación

```bash
python -m pip install -r requirements-dev.txt
python -m compileall -q app tests
python -m pytest -q
find app/frontend/js -name '*.js' -print0 | xargs -0 -n1 node --check
git diff --check
pip-audit -r requirements.txt
pip-audit
```

GitHub Actions ejecuta estas comprobaciones en cada push a `main` y en cada pull request.

## Estructura

```text
app/backend/Bots/       # clasificación de intenciones y cliente opcional de Groq
app/backend/booking/    # modelos, agenda, SQLite y notificaciones
app/backend/core/       # aplicación, CORS, seguridad y arranque
app/backend/services/   # lógica de reservas, chat y catálogo
app/frontend/           # HTML, CSS, JavaScript y medios
tests/                  # pruebas de servicio, API y seguridad
```

El catálogo y las rutas de las imágenes se mantienen en `app/backend/services/restaurant_catalog.py`; los horarios y mesas, en `app/backend/booking/scheduling.py`.

## Límites de producción

SQLite y el rate limiter en memoria son adecuados para una única instancia y tráfico moderado. Para varias réplicas o concurrencia alta, usa una base de datos y un backend de rate limiting compartidos. Configura `CORS_ORIGINS` con los dominios HTTPS reales y gestiona secretos desde el proveedor de despliegue.
