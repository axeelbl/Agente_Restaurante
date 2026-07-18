from app.backend.Bots.Prompts import SYSTEM_PROMPT
from app.backend.Bots.chat import ask_groq


def fallback_chat_response():
    return (
        "Puedo ayudarte con reservas, disponibilidad, carta, menú del día, fotos del local "
        "y recomendaciones de platos. Por ejemplo: 'Quiero reservar para 4 mañana a las 21:00', "
        "'Enséñame la carta' o 'Recomiéndame algo vegetariano'."
    )


def handle_chat(user_message, request):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    try:
        bot_reply = ask_groq(messages)
    except Exception:
        bot_reply = fallback_chat_response()

    return {"bot_message": bot_reply}
