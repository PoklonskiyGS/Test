"""
База предметов для PoE Craft Bot
"""
import json
import os

# БАЗА ПРЕДМЕТОВ (только базовые параметры)
ITEM_DATABASE = {
    "boots": {
        "name": "Сапоги",
        "icon": "👢",
        "implicit_count": 1,
        "implicit_mods": ["Movement Speed"],
    },
    "gloves": {
        "name": "Перчатки",
        "icon": "🧤",
        "implicit_count": 0,
        "implicit_mods": [],
    },
    "helmet": {
        "name": "Шлем",
        "icon": "⛑️",
        "implicit_count": 0,
        "implicit_mods": [],
    },
    "body_armour": {
        "name": "Нагрудник",
        "icon": "👕",
        "implicit_count": 0,
        "implicit_mods": [],
    },
    "ring": {
        "name": "Кольцо",
        "icon": "💍",
        "implicit_count": 0,
        "implicit_mods": [],
    },
    "amulet": {
        "name": "Амулет",
        "icon": "📿",
        "implicit_count": 0,
        "implicit_mods": [],
    },
    "belt": {
        "name": "Пояс",
        "icon": "🔗",
        "implicit_count": 0,
        "implicit_mods": [],
    },
    "wand": {
        "name": "Жезл",
        "icon": "🪄",
        "implicit_count": 1,
        "implicit_mods": ["increased Spell Damage"],
    },
    "dagger": {
        "name": "Кинжал",
        "icon": "🗡️",
        "implicit_count": 0,
        "implicit_mods": [],
    },
    "bow": {
        "name": "Лук",
        "icon": "🏹",
        "implicit_count": 0,
        "implicit_mods": [],
    },
    "quiver": {
        "name": "Колчан",
        "icon": "🏹",
        "implicit_count": 1,
        "implicit_mods": ["to Accuracy Rating"],
    },
    "shield": {
        "name": "Щит",
        "icon": "🛡️",
        "implicit_count": 0,
        "implicit_mods": [],
    },
}

# Список для выпадающего меню
ITEM_LIST = [
    ("boots", "👢 Сапоги"),
    ("gloves", "🧤 Перчатки"),
    ("helmet", "⛑️ Шлем"),
    ("body_armour", "👕 Нагрудник"),
    ("ring", "💍 Кольцо"),
    ("amulet", "📿 Амулет"),
    ("belt", "🔗 Пояс"),
    ("wand", "🪄 Жезл"),
    ("dagger", "🗡️ Кинжал"),
    ("bow", "🏹 Лук"),
    ("quiver", "🏹 Колчан"),
    ("shield", "🛡️ Щит"),
]

# ВСЕ ДОСТУПНЫЕ МОДЫ ДЛЯ ВЫБОРА (общий список)
# Пользователь сам выбирает из этого списка нужные
AVAILABLE_MODS = [
    # Основные
    "Movement Speed",
    "to maximum Life",
    "to maximum Energy Shield",
    "to maximum Mana",
    "increased Damage",
    "increased Attack Speed",
    "increased Cast Speed",
    
    # Сопротивления
    "to Fire Resistance",
    "to Cold Resistance",
    "to Lightning Resistance",
    "to All Elemental Resistances",
    
    # Броня
    "increased Armour",
    "increased Evasion Rating",
    
    # Оружие
    "increased Physical Damage",
    "increased Elemental Damage",
    "increased Critical Strike Chance",
    "increased Critical Strike Multiplier",
    "to Accuracy Rating",
    
    # Аксессуары
    "increased Rarity of Items found",
    "increased Quantity of Items found",
    "to Attributes",
    "increased Flask Duration",
    "increased Flask Effect",
    "increased Spell Damage",
    "to Level of all Spell Gems",
]

# Моды с числовыми значениями (предустановленные, но пользователь может изменить)
DEFAULT_VALUE_MODS = {
    "boots": [
        {"name": "Movement Speed", "min_value": 25},
    ],
    "gloves": [
        {"name": "to maximum Life", "min_value": 50},
    ],
    "helmet": [
        {"name": "to maximum Life", "min_value": 60},
    ],
    "body_armour": [
        {"name": "to maximum Life", "min_value": 80},
    ],
    "ring": [
        {"name": "to maximum Life", "min_value": 40},
    ],
    "amulet": [
        {"name": "to maximum Life", "min_value": 50},
    ],
    "belt": [
        {"name": "to maximum Life", "min_value": 60},
    ],
    "wand": [
        {"name": "increased Spell Damage", "min_value": 40},
    ],
    "dagger": [
        {"name": "increased Physical Damage", "min_value": 100},
    ],
    "bow": [
        {"name": "increased Physical Damage", "min_value": 100},
    ],
    "quiver": [
        {"name": "to maximum Life", "min_value": 40},
    ],
    "shield": [
        {"name": "to maximum Life", "min_value": 50},
    ],
}


def get_item_info(item_key: str):
    return ITEM_DATABASE.get(item_key, ITEM_DATABASE["boots"])

def get_implicit_count(item_key: str) -> int:
    return get_item_info(item_key).get("implicit_count", 0)

def get_default_value_mods(item_key: str) -> list:
    return DEFAULT_VALUE_MODS.get(item_key, [])