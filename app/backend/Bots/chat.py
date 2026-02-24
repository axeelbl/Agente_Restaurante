from groq import Groq
import json
from ..config import GROQ_API_KEY
from .Prompts import BOOKING_DECISION_PROMPT

client = Groq(api_key=GROQ_API_KEY)


def ask_groq(messages, temperature=0.9):
    """
    Envía mensajes a Groq y devuelve la respuesta
    messages: lista de diccionarios {"role": "system/user/assistant", "content": "texto"}
    """
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=temperature
    )
    return response.choices[0].message.content


def decide_and_extract_booking(user_message):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": BOOKING_DECISION_PROMPT},
            {"role": "user", "content": user_message}
        ],
        temperature=0
    )

    content = response.choices[0].message.content

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {"action": "CHAT"}
    

REQUIRED_FIELDS = ["name", "service", "date", "time", "contact"]

def is_complete_booking(booking):
    return all(booking.get(field) for field in REQUIRED_FIELDS)