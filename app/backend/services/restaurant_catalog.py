from __future__ import annotations


RESTAURANT_INFO = {
    "name": "Mesa Viva",
    "address": "Calle de Alcala 145, Madrid",
    "phone": "+34 910 123 456",
    "reservation_phone": "+34 910 123 456",
    "hours": {
        "martes_domingo": {
            "comida": "13:00-16:00",
            "cena": "20:00-23:30",
        },
        "lunes": "cerrado",
    },
    "cuisine_types": [
        "cocina mediterranea",
        "arroces",
        "tapas",
        "parrilla suave",
    ],
    "reservations": True,
    "terrace": True,
    "pets": "Solo en la terraza y con correa.",
    "parking": "Hay un parking publico a 2 minutos andando.",
    "takeaway": True,
    "delivery": False,
    "payments": ["efectivo", "tarjeta", "Bizum"],
    "large_groups": "Aceptamos grupos de hasta 8 personas online. Para grupos mayores, mejor llamarnos.",
    "allergens": "Podemos informar de alergenos plato por plato y adaptar varias opciones bajo consulta.",
}


MENU_CATEGORIES = [
    {
        "id": "entrantes",
        "name": "Entrantes",
        "items": [
            {
                "name": "Croquetas de jamon iberico",
                "description": "Crujientes por fuera y muy cremosas por dentro.",
                "price": 8.5,
                "available": True,
                "allergens": ["gluten", "lacteos", "huevo"],
                "vegetarian": False,
                "vegan": False,
                "gluten_free": False,
                "tags": ["clasico", "rapido", "compartir", "carne"],
                "featured": True,
            },
            {
                "name": "Burrata con tomates asados",
                "description": "Burrata cremosa con tomates confitados, albahaca y aceite de hierbas.",
                "price": 11.5,
                "available": True,
                "allergens": ["lacteos"],
                "vegetarian": True,
                "vegan": False,
                "gluten_free": True,
                "tags": ["ligero", "vegetariano", "compartir"],
                "featured": True,
            },
            {
                "name": "Pulpo a la brasa",
                "description": "Pulpo con parmentier suave y pimenton ahumado.",
                "price": 15.0,
                "available": True,
                "allergens": ["pescado"],
                "vegetarian": False,
                "vegan": False,
                "gluten_free": True,
                "tags": ["especialidad", "mar", "compartir", "tipico"],
                "featured": True,
            },
        ],
    },
    {
        "id": "principales",
        "name": "Principales",
        "items": [
            {
                "name": "Arroz meloso de setas",
                "description": "Arroz cremoso con setas de temporada y parmesano.",
                "price": 16.5,
                "available": True,
                "allergens": ["lacteos"],
                "vegetarian": True,
                "vegan": False,
                "gluten_free": True,
                "tags": ["vegetariano", "especialidad", "tipico"],
                "featured": True,
            },
            {
                "name": "Curry suave de garbanzos",
                "description": "Curry de verduras y garbanzos con arroz basmati.",
                "price": 15.5,
                "available": True,
                "allergens": [],
                "vegetarian": True,
                "vegan": True,
                "gluten_free": True,
                "tags": ["vegano", "vegetariano", "ligero", "barato"],
                "featured": False,
            },
            {
                "name": "Lubina al horno",
                "description": "Lubina con verduras salteadas y salsa citrica.",
                "price": 18.0,
                "available": True,
                "allergens": ["pescado"],
                "vegetarian": False,
                "vegan": False,
                "gluten_free": True,
                "tags": ["pescado", "ligero", "especialidad"],
                "featured": True,
            },
            {
                "name": "Secreto iberico",
                "description": "Secreto iberico con patatas rusticas y jugo reducido.",
                "price": 19.5,
                "available": True,
                "allergens": [],
                "vegetarian": False,
                "vegan": False,
                "gluten_free": True,
                "tags": ["carne", "especialidad", "tipico"],
                "featured": True,
            },
            {
                "name": "Burger Mesa Viva",
                "description": "Hamburguesa de vaca madurada con cheddar y cebolla caramelizada.",
                "price": 14.0,
                "available": True,
                "allergens": ["gluten", "lacteos"],
                "vegetarian": False,
                "vegan": False,
                "gluten_free": False,
                "tags": ["carne", "rapido", "barato"],
                "featured": False,
            },
        ],
    },
    {
        "id": "bebidas",
        "name": "Bebidas",
        "items": [
            {
                "name": "Limonada casera",
                "description": "Limon natural, hierbabuena y un toque de jengibre.",
                "price": 3.0,
                "available": True,
                "allergens": [],
                "vegetarian": True,
                "vegan": True,
                "gluten_free": True,
                "tags": ["ligero", "rapido", "barato"],
                "featured": False,
            },
            {
                "name": "Copa de Rioja",
                "description": "Vino tinto joven servido por copa.",
                "price": 4.2,
                "available": True,
                "allergens": ["sulfitos"],
                "vegetarian": True,
                "vegan": True,
                "gluten_free": True,
                "tags": ["vino"],
                "featured": False,
            },
            {
                "name": "Tinto de verano",
                "description": "Clasico y fresco, ideal para compartir.",
                "price": 3.5,
                "available": True,
                "allergens": ["sulfitos"],
                "vegetarian": True,
                "vegan": True,
                "gluten_free": True,
                "tags": ["vino", "barato"],
                "featured": False,
            },
        ],
    },
    {
        "id": "postres",
        "name": "Postres",
        "items": [
            {
                "name": "Tarta de queso al horno",
                "description": "Cremosa, con base fina y coulis de frutos rojos.",
                "price": 6.0,
                "available": True,
                "allergens": ["gluten", "lacteos", "huevo"],
                "vegetarian": True,
                "vegan": False,
                "gluten_free": False,
                "tags": ["postre", "especialidad"],
                "featured": True,
            },
            {
                "name": "Brownie de chocolate",
                "description": "Con nueces y helado de vainilla.",
                "price": 5.5,
                "available": True,
                "allergens": ["gluten", "lacteos", "frutos secos", "huevo"],
                "vegetarian": True,
                "vegan": False,
                "gluten_free": False,
                "tags": ["postre", "tipico"],
                "featured": False,
            },
            {
                "name": "Fruta de temporada",
                "description": "Corte fresco del dia.",
                "price": 4.5,
                "available": True,
                "allergens": [],
                "vegetarian": True,
                "vegan": True,
                "gluten_free": True,
                "tags": ["postre", "ligero", "vegano"],
                "featured": False,
            },
        ],
    },
]


MENU_OF_DAY = {
    "name": "Menu del día",
    "price": 16.9,
    "first_courses": [
        "Crema de calabaza con pipas tostadas",
        "Ensalada de quinoa, tomate seco y feta",
        "Pasta corta con pesto de albahaca",
    ],
    "main_courses": [
        "Pollo rustido con patatas al romero",
        "Merluza a la plancha con verduras",
        "Arroz de verduras de temporada",
    ],
    "includes": [
        "Pan",
        "Bebida",
        "Postre o cafe",
    ],
}


PHOTO_COLLECTIONS = [
    {
        "name": "Platos destacados",
        "description": "Una seleccion de nuestros platos mas pedidos.",
        "tags": ["fotos", "platos", "destacados", "carta visual", "comida"],
        "photos": [
            "/static/pictures/restaurante/burrata.svg",
            "/static/pictures/restaurante/arroz.svg",
            "/static/pictures/restaurante/secreto.svg",
        ],
    },
    {
        "name": "Local y terraza",
        "description": "Vista del comedor interior y de la terraza.",
        "tags": ["local", "terraza", "interior", "restaurante", "sitio"],
        "photos": [
            "/static/pictures/restaurante/sala.svg",
            "/static/pictures/restaurante/terraza.svg",
        ],
    },
    {
        "name": "Postres",
        "description": "Nuestras opciones dulces del final.",
        "tags": ["postres", "dulces"],
        "photos": [
            "/static/pictures/restaurante/postres.svg",
        ],
    },
    {
        "name": "Menu del dia",
        "description": "Una referencia visual del menu del dia.",
        "tags": ["menu del dia", "menu", "diario"],
        "photos": [
            "/static/pictures/restaurante/menu-dia.svg",
        ],
    },
]


def get_all_menu_items() -> list[dict]:
    items: list[dict] = []
    for category in MENU_CATEGORIES:
        for item in category["items"]:
            enriched = dict(item)
            enriched["category"] = category["name"]
            items.append(enriched)
    return items
