"""
Совместимость со старым кодом.
Логика парсинга перенесена в craft_engine (разработка v3.0).
"""
from craft_engine import (
    get_rarity, get_mod_lines, has_target_mod, mod_count,
    parse_item, evaluate, decide_action,
    METHOD_NAMES, STOP_MESSAGES,
)

__all__ = [
    "get_rarity", "get_mod_lines", "has_target_mod", "mod_count",
    "parse_item", "evaluate", "decide_action",
    "METHOD_NAMES", "STOP_MESSAGES",
]
