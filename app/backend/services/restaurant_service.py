from __future__ import annotations

import unicodedata

from app.backend.services.restaurant_catalog import (
    MENU_CATEGORIES,
    MENU_OF_DAY,
    PHOTO_COLLECTIONS,
    RESTAURANT_INFO,
    get_all_menu_items,
)


def normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text.lower())
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def handle_restaurant_request(user_message: str, action: str | None = None) -> dict | None:
    message = normalize_text(user_message)

    if action == "SHOW_PHOTOS" or should_show_photos(message):
        return build_photo_response(message)

    if action == "SHOW_MENU" or should_show_menu(message):
        return build_menu_response(message)

    if action == "RECOMMEND_DISH" or should_recommend_dishes(message):
        return build_recommendation_response(message)

    faq_topics = match_faq_topics(message)
    if action == "SHOW_FAQ" or faq_topics:
        return build_faq_response(faq_topics or ["general"])

    return None


def should_show_photos(message: str) -> bool:
    return any(
        keyword in message
        for keyword in [
            "foto",
            "fotos",
            "imagenes",
            "imagen",
            "carta visual",
            "ensename platos",
            "ver platos",
            "ver local",
        ]
    )


def should_show_menu(message: str) -> bool:
    return any(
        keyword in message
        for keyword in [
            "carta",
            "menu del dia",
            "menu de hoy",
            "postres",
            "bebidas",
            "que teneis",
            "sugerencias",
        ]
    )


def should_recommend_dishes(message: str) -> bool:
    return any(
        keyword in message
        for keyword in [
            "recomi",
            "algo ligero",
            "algo rapido",
            "algo barato",
            "vegetar",
            "vegano",
            "carne",
            "pescado",
            "plato tipico",
            "especialidad",
        ]
    )


def match_faq_topics(message: str) -> list[str]:
    topic_map = {
        "horario": ["horario", "abris", "abierto", "cerrado"],
        "ubicacion": ["direccion", "ubicacion", "donde estais", "donde esta", "como llegar"],
        "telefono": ["telefono", "llamar", "contacto"],
        "reservas": ["haceis reservas", "aceptais reservas", "se puede reservar"],
        "terraza": ["terraza", "exterior"],
        "mascotas": ["mascotas", "perros", "admitis mascotas"],
        "alergenos": ["alergenos", "gluten", "lactosa", "alergias"],
        "vegetariano": ["vegetariano", "vegano", "sin carne"],
        "comida": ["tipo de comida", "que cocina", "especialidad", "que cocinais"],
        "pagos": ["pago", "pagais", "tarjeta", "bizum", "efectivo"],
        "parking": ["parking", "aparcamiento"],
        "takeaway": ["llevar", "take away", "para llevar"],
        "delivery": ["domicilio", "delivery", "reparto"],
        "grupos": ["grupo", "grupos", "cumpleanos", "cumpleanos", "muchas personas"],
    }

    matches: list[str] = []
    for topic, keywords in topic_map.items():
        if any(keyword in message for keyword in keywords):
            matches.append(topic)
    return matches


def build_faq_response(topics: list[str]) -> dict:
    answers: list[str] = []

    if "general" in topics:
        answers.append(
            f"{RESTAURANT_INFO['name']} esta en {RESTAURANT_INFO['address']} y atendemos de martes a domingo."
        )

    for topic in topics:
        if topic == "horario":
            answers.append(
                "Horario: martes a domingo comida de "
                f"{RESTAURANT_INFO['hours']['martes_domingo']['comida']} y cena de "
                f"{RESTAURANT_INFO['hours']['martes_domingo']['cena']}. "
                f"Lunes {RESTAURANT_INFO['hours']['lunes']}."
            )
        elif topic == "ubicacion":
            answers.append(f"Estamos en {RESTAURANT_INFO['address']}.")
        elif topic == "telefono":
            answers.append(f"Nuestro telefono es {RESTAURANT_INFO['phone']}.")
        elif topic == "reservas":
            answers.append("Si, aceptamos reservas online y por telefono.")
        elif topic == "terraza":
            answers.append("Si, tenemos terraza.")
        elif topic == "mascotas":
            answers.append(RESTAURANT_INFO["pets"])
        elif topic == "alergenos":
            answers.append(RESTAURANT_INFO["allergens"])
        elif topic == "vegetariano":
            answers.append("Tenemos opciones vegetarianas y veganas en carta y menu del dia.")
        elif topic == "comida":
            answers.append(
                "Trabajamos "
                + ", ".join(RESTAURANT_INFO["cuisine_types"][:-1])
                + " y "
                + RESTAURANT_INFO["cuisine_types"][-1]
                + "."
            )
        elif topic == "pagos":
            answers.append("Aceptamos " + ", ".join(RESTAURANT_INFO["payments"]) + ".")
        elif topic == "parking":
            answers.append(RESTAURANT_INFO["parking"])
        elif topic == "takeaway":
            answers.append("Si, preparamos comida para llevar.")
        elif topic == "delivery":
            answers.append("No trabajamos con envio a domicilio por ahora.")
        elif topic == "grupos":
            answers.append(RESTAURANT_INFO["large_groups"])

    return {"bot_message": "\n\n".join(dict.fromkeys(answers))}


def build_menu_response(message: str) -> dict:
    if "menu del dia" in message or "menu de hoy" in message or "lleva el menu" in message:
        return {"bot_message": format_menu_of_day()}

    if "postres" in message:
        return {"bot_message": format_single_category("Postres")}

    if "bebidas" in message or "beber" in message:
        return {"bot_message": format_single_category("Bebidas")}

    if "sugerencias" in message:
        featured_items = [item for item in get_all_menu_items() if item.get("featured")]
        return {
            "bot_message": "Sugerencias de la casa:\n" + format_items(featured_items[:4])
        }

    return {"bot_message": format_full_menu()}


def build_photo_response(message: str) -> dict:
    collections = PHOTO_COLLECTIONS

    if "postre" in message:
        collections = [collection for collection in PHOTO_COLLECTIONS if collection["name"] == "Postres"]
    elif "terraza" in message or "interior" in message or "local" in message:
        collections = [collection for collection in PHOTO_COLLECTIONS if collection["name"] == "Local y terraza"]
    elif "menu del dia" in message:
        collections = [collection for collection in PHOTO_COLLECTIONS if collection["name"] == "Menu del dia"]
    elif "plato" in message or "comida" in message:
        collections = [collection for collection in PHOTO_COLLECTIONS if collection["name"] == "Platos destacados"]

    photos: list[str] = []
    lines: list[str] = []
    for collection in collections:
        lines.append(f"- {collection['name']}: {collection['description']}")
        photos.extend(collection["photos"])

    return {
        "bot_message": "Aqui tienes algunas fotos del restaurante:\n" + "\n".join(lines),
        "photos": list(dict.fromkeys(photos)),
    }


def build_recommendation_response(message: str) -> dict:
    if "menu del dia" in message:
        return {"bot_message": format_menu_of_day()}

    preferences = extract_preferences(message)
    items = rank_menu_items(preferences)

    if not items:
        fallback_items = [item for item in get_all_menu_items() if item.get("featured")]
        return {
            "bot_message": "Te sugiero empezar por nuestras especialidades:\n" + format_items(fallback_items[:3])
        }

    intro = "Te recomiendo estas opciones:\n"
    if preferences:
        intro = "Segun lo que buscas, te recomiendo:\n"

    return {"bot_message": intro + format_items(items[:3])}


def extract_preferences(message: str) -> set[str]:
    preferences: set[str] = set()

    if "vegetar" in message:
        preferences.add("vegetarian")
    if "vegano" in message:
        preferences.add("vegan")
    if "ligero" in message or "suave" in message:
        preferences.add("light")
    if "rapido" in message or "rapida" in message:
        preferences.add("quick")
    if "barato" in message or "economico" in message:
        preferences.add("budget")
    if "carne" in message:
        preferences.add("meat")
    if "pescado" in message or "marisco" in message:
        preferences.add("fish")
    if "tipico" in message or "especialidad" in message or "casa" in message:
        preferences.add("signature")
    if "postre" in message or "dulce" in message:
        preferences.add("dessert")

    return preferences


def rank_menu_items(preferences: set[str]) -> list[dict]:
    scored_items: list[tuple[int, dict]] = []

    for item in get_all_menu_items():
        if not item.get("available", True):
            continue

        score = 0
        tags = set(item.get("tags", []))
        category_name = normalize_text(item["category"])

        if preferences and category_name == "bebidas":
            score -= 6

        if preferences and category_name == "postres" and "dessert" not in preferences:
            score -= 4

        if not preferences and item.get("featured"):
            score += 3

        if "vegetarian" in preferences:
            if item.get("vegetarian"):
                score += 4
            else:
                score -= 4

        if "vegan" in preferences:
            if item.get("vegan"):
                score += 5
            else:
                score -= 5

        if "light" in preferences and "ligero" in tags:
            score += 3
        if "quick" in preferences and "rapido" in tags:
            score += 3
        if "budget" in preferences and "barato" in tags:
            score += 3
        if "meat" in preferences and "carne" in tags:
            score += 4
        if "fish" in preferences and ("pescado" in tags or "mar" in tags):
            score += 4
        if "signature" in preferences and ("especialidad" in tags or item.get("featured")):
            score += 4
        if "dessert" in preferences and category_name == "postres":
            score += 5

        score += sum(1 for tag in tags if tag in {"especialidad", "tipico"} and "signature" in preferences)

        if score > 0:
            scored_items.append((score, item))

    scored_items.sort(key=lambda item: (-item[0], item[1]["price"]))
    return [item for _, item in scored_items]


def format_full_menu() -> str:
    sections = ["Carta actual:"]
    for category in MENU_CATEGORIES:
        sections.append("")
        sections.append(f"{category['name']}:")
        sections.append(format_items(category["items"]))
    return "\n".join(sections)


def format_single_category(category_name: str) -> str:
    for category in MENU_CATEGORIES:
        if category["name"] == category_name:
            return f"{category_name}:\n" + format_items(category["items"])
    return "No encuentro esa categoria ahora mismo."


def format_menu_of_day() -> str:
    lines = [
        f"{MENU_OF_DAY['name']} - {format_price(MENU_OF_DAY['price'])}",
        "",
        "Primeros:",
    ]
    lines.extend(f"- {course}" for course in MENU_OF_DAY["first_courses"])
    lines.append("")
    lines.append("Segundos:")
    lines.extend(f"- {course}" for course in MENU_OF_DAY["main_courses"])
    lines.append("")
    lines.append("Incluye:")
    lines.extend(f"- {item}" for item in MENU_OF_DAY["includes"])
    return "\n".join(lines)


def format_items(items: list[dict]) -> str:
    lines: list[str] = []
    for item in items:
        markers = []
        if item.get("vegetarian"):
            markers.append("vegetariano")
        if item.get("vegan"):
            markers.append("vegano")
        if item.get("gluten_free"):
            markers.append("sin gluten")

        allergen_text = ""
        if item.get("allergens"):
            allergen_text = " | Alergenos: " + ", ".join(item["allergens"])

        marker_text = ""
        if markers:
            marker_text = " | " + ", ".join(markers)

        lines.append(
            f"- {item['name']} ({format_price(item['price'])})"
            f": {item['description']}{marker_text}{allergen_text}"
        )
    return "\n".join(lines)


def format_price(value: float) -> str:
    return f"{value:.2f} EUR"
