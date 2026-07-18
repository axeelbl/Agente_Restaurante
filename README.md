# Mesa Viva - Asistente inteligente de restaurante

Mesa Viva es una aplicación web para restaurantes que centraliza en un chat la información clave del local: carta, menú del día, recomendaciones, fotos, dudas frecuentes y gestión de reservas.

El proyecto combina un frontend ligero en HTML, CSS y JavaScript con una API en FastAPI. El asistente puede resolver consultas de forma local con reglas del dominio y, cuando está configurado, apoyarse en Groq para conversaciones más abiertas.

## Funcionalidades principales

- Chat conversaciónal para carta, recomendaciones, fotos e información del restaurante.
- Reserva online con validación de fecha, hora, contacto y número de comensales.
- Consulta de disponibilidad por día, hora y tamaño del grupo.
- Modificación y cancelación de reservas medíante ID y contacto asociado.
- Catálogo editable de platos, precios, alérgenos, etiquetas y fotos.
- Registro local de leads en CSV y envío opcional por SendGrid.
- Protecciones básicas: rate limiting, cabeceras de seguridad, validación de inputs y exclusion de secretos del repositorio.

## Stack técnico

- Backend: FastAPI, Pydantic, SQLite, SlowAPI.
- Frontend: HTML, CSS modular y JavaScript vanilla.
- IA opcional: Groq (`llama-3.1-8b-instant`).
- Email opcional: SendGrid.
- Tests: `unittest`.

## Estructura del proyecto

```text
app/
  backend/
    Bots/                 # Rutas y lógica de decision del chat
    booking/              # Modelos, persistencia, horarios y rutas de reservas
    core/                 # Creación de la app, CORS, seguridad y arranque
    services/             # Servicios de chat, reservas y restaurante
    config.py             # Carga de variables de entorno
    csv_útils.py          # Registro de leads
    email_útils.py        # Envio opcional de CSV por email
    main.py               # Punto de entrada ASGI
  frontend/
    css/                  # Estilos por area de la interfaz
    js/                   # Controladores de chat, UI, avatar y reservas
    pictures/             # Imagenes e iconos del restaurante
    index.html            # Interfaz principal
tests/                    # Pruebas de servicios de reservas y restaurante
requirements.txt          # Dependencias Python
```

## Requisitos

- Python 3.11 o superior recomendado.
- `pip`.
- Cuenta/API key de Groq solo si se quiere activar la respuesta generativa.
- Cuenta/API key de SendGrid solo si se quiere enviar el CSV de leads por email.

## Instalacion

1. Crear y activar un entorno virtual:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. Instalar dependencias:

```powershell
pip install -r requirements.txt
```

3. Crear el archivo de entorno:

```powershell
Copy-Item .env.example .env
```

4. Rellenar solo las variables que se vayan a usar. No subas `.env` al repositorio.

## Variables de entorno

| Variable | Uso | Obligatoria |
| --- | --- | --- |
| `GROQ_API_KEY` | Activa respuestas generativas con Groq | No |
| `SENDGRID_API_KEY` | Permite enviar el CSV de leads por email | No |
| `SENDGRID_FROM` | Remitente validado en SendGrid | No |
| `SENDGRID_TO` | Destinatario del CSV de leads | No |
| `BOOKINGS_DB_PATH` | Ruta alternativa para la base de datos SQLite | No |

Sin `GROQ_API_KEY`, el sistema sigue funcionando con detección local de intenciones para carta, fotos, FAQs, disponibilidad y reservas.

## Ejecución local

Desde la raíz del proyecto:

```powershell
uvicorn app.backend.main:app --reload
```

Después abre:

```text
http://127.0.0.1:8000
```

La API sirve el frontend desde `/` y los assets desde `/static`.

## Endpoints principales

| Método | Ruta | Descripción |
| --- | --- | --- |
| `POST` | `/chat` | Procesa mensajes del asistente |
| `GET` | `/booking/availability` | Devuelve huecos disponibles |
| `POST` | `/booking/reserve` | Crea una reserva |
| `POST` | `/booking/modify` | Modifica una reserva existente |
| `POST` | `/booking/cancel` | Cancela una reserva existente |

## Tests

Ejecutar la suite:

```powershell
python -m unittest discover -s tests
```

Los tests crean bases de datos temporales dentro de `tests/.tmp/`, carpeta ignorada por Git.

## Datos locales y seguridad

Este repositorio está preparado para no versionar secretos ni datos operativos:

- `.env`, `.env.*` y `sendgrid.env` quedan fuera del control de versiones.
- `leads.csv` queda fuera del control de versiones.
- Bases de datos SQLite locales (`*.db`, `*.sqlite`, WAL/SHM) quedan fuera del control de versiones.
- El entorno virtual (`venv/`) y caches de tests también estan ignorados.

Antes de publicar cambios, revisa siempre:

```powershell
git status --short
git diff --cached
```

## Personalización

- Edita la información del restaurante en `app/backend/services/restaurant_catalog.py`.
- Ajusta horarios, festivos, duracion de reservas y mesas en `app/backend/booking/scheduling.py`.
- Modifica textos, estilos y componentes visuales en `app/frontend/`.

## Notas de producción

- Usa variables de entorno reales en el proveedor de despliegue, nunca en archivos versionados.
- Configura CORS según el dominio final si frontend y backend se despliegan por separado.
- Sustituye SQLite por una base de datos gestiónada si se espera concurrencia alta o múltiples instancias.
- Revisa límites de rate limiting según tráfico real.
