from app.backend.Bots.chat import ask_groq
from app.backend.Bots.Prompts import SYSTEM_PROMPT

def handle_chat(user_message, request):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
    ]
    
    bot_reply = ask_groq(messages)

    return {"bot_message": bot_reply}
