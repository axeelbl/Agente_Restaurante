# recommend_cut.py
import random
from app.backend.services.cuts_catalog import CUTS

def recommend_cut_by_text(user_message: str):
    """
    Decide qué fotos mostrar según el mensaje del usuario.
    - "ver fotos" → todas las fotos
    - Consulta por corte específico → fotos de ese corte
    - "recomiéndame un corte" → corte aleatorio con fotos
    """
    user_message = user_message.lower().strip()
    photos_to_show = set()
    selected_cut = None

    # 1️⃣ Mostrar todas las fotos
    if user_message == "ver fotos":
        bot_msg = "Aquí tienes todas nuestras fotos de cortes disponibles:"
        for cut in CUTS:
            bot_msg += f"\n- {cut['name']}: {cut['description']}"
            for photo in cut.get("photos", []):
                photos_to_show.add(photo)
        return {"bot_message": bot_msg, "photos": list(photos_to_show)}

    # 2️⃣ Recomendación aleatoria
    if "recomiendame un corte" in user_message or "recomiéndame un corte" in user_message:
        selected_cut = random.choice(CUTS)
        bot_msg = f"Te recomiendo el corte '{selected_cut['name']}': {selected_cut['description']}"
        for photo in selected_cut.get("photos", []):
            photos_to_show.add(photo)
        return {"bot_message": bot_msg, "photos": list(photos_to_show)}

    # 3️⃣ Buscar corte específico por nombre o tags
    for cut in CUTS:
        if cut["name"].lower() in user_message or any(tag.lower() in user_message for tag in cut.get("tags", [])):
            selected_cut = cut
            break

    # 4️⃣ Si encontró → mostrar fotos del corte
    if selected_cut:
        bot_msg = f"¡Claro! Aquí tienes algunas fotos del corte '{selected_cut['name']}': {selected_cut['description']}"
        for photo in selected_cut.get("photos", []):
            photos_to_show.add(photo)
        return {"bot_message": bot_msg, "photos": list(photos_to_show)}

    # 5️⃣ Si no encontró → mostrar cortes populares
    bot_msg = "No encontramos exactamente lo que buscas. Te muestro algunos cortes populares:"
    for cut in CUTS[:3]:
        bot_msg += f"\n- {cut['name']}: {cut['description']}"
        for photo in cut.get("photos", []):
            photos_to_show.add(photo)
    return {"bot_message": bot_msg, "photos": list(photos_to_show)}