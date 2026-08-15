"""Menu + gaming catalogue. Behavioural tags only — nothing sensitive."""

FOOD = [
    {"id": "paneer",   "name": "Smoky Peri-Peri Paneer",  "icon": "🌶️", "price": 240, "tags": ["spicy", "hero", "share"],            "gaming_friendly": True},
    {"id": "nachos",   "name": "Loaded Nachos",            "icon": "🧀", "price": 210, "tags": ["share", "snack"],                    "gaming_friendly": True},
    {"id": "slider",   "name": "Truffle Mushroom Sliders", "icon": "🍔", "price": 260, "tags": ["hero", "meal"],                     "gaming_friendly": True},
    {"id": "fries",    "name": "Masala Peri Fries",        "icon": "🍟", "price": 140, "tags": ["snack", "share"],                    "gaming_friendly": True},
    {"id": "wrap",     "name": "Paneer Tikka Wrap",        "icon": "🌯", "price": 190, "tags": ["meal", "onehand"],                  "gaming_friendly": True},
    {"id": "lava",     "name": "Belgian Choco Lava",       "icon": "🍫", "price": 180, "tags": ["dessert", "celebrate"],             "gaming_friendly": False},
    {"id": "coldbrew", "name": "Signature Cold Brew",      "icon": "🧊", "price": 160, "tags": ["drink", "coffee"],                  "gaming_friendly": True},
    {"id": "cortado",  "name": "Iced Cortado",             "icon": "☕", "price": 150, "tags": ["drink", "coffee", "winddown"],      "gaming_friendly": False},
    {"id": "filter",   "name": "South Filter Coffee",      "icon": "☕", "price": 90,  "tags": ["drink", "coffee", "morning"],       "gaming_friendly": False},
]

GAMES = [
    {"id": "fc25",      "name": "EA FC 25 (PS5)",       "icon": "⚽",  "price": 200, "platform": "ps5", "tags": ["squad", "sports"]},
    {"id": "tekken",    "name": "Tekken 8 (PS5)",       "icon": "🥋", "price": 200, "platform": "ps5", "tags": ["versus", "competitive"]},
    {"id": "valorant",  "name": "Valorant (Gaming PC)", "icon": "🎯", "price": 180, "platform": "pc",  "tags": ["squad", "competitive"]},
    {"id": "beatsaber", "name": "Beat Saber (VR)",      "icon": "🕶️", "price": 250, "platform": "vr",  "tags": ["active", "solo"]},
    {"id": "f1sim",     "name": "F1 Racing Sim",        "icon": "🏎️", "price": 300, "platform": "sim", "tags": ["thrill", "solo"]},
    {"id": "godofwar",  "name": "God of War (PS5)",     "icon": "🪓", "price": 200, "platform": "ps5", "tags": ["story", "solo"]},
]

FOOD_BY_ID = {f["id"]: f for f in FOOD}
GAMES_BY_ID = {g["id"]: g for g in GAMES}
