"""
Движок крафта — чистая логика БЕЗ игровых зависимостей.

Зона ответственности:
  * разбор текста предмета (clipboard / OCR) в структурированный вид;
  * оценка целевых модов (простые / по значению / по весу);
  * решение, какую валюту применить следующей.

Модуль можно импортировать без pydirectinput/pyautogui/keyboard —
на нём пишутся тесты логики (test_engine.py).
"""
import re
import random

# ----------------------------------------------------------------------
# Цвета соккетов (для Orb of Chance)
# ----------------------------------------------------------------------

COLOR_TOKENS = {
    "r": "R", "red": "R",
    "g": "G", "green": "G",
    "b": "B", "blue": "B",
}

# Маркеры НЕ-аффиксов — используются в FALLBACK-режиме
# (когда в тексте не найден блок "Rarity:", например при OCR)
FALLBACK_MARKERS = (
    "item class:", "rarity:", "requirements:", "requires", "sockets:",
    "item level:", "quality:", "armour:", "evasion rating:", "energy shield:",
    "physical damage:", "elemental damage:", "critical strike chance:",
    "critical hit chance:", "attacks per second:", "weapon range:",
    "chance to block:", "limited to:", "durability:", "mana regenerated:",
    "corrupted", "unidentified", "adds ",
)

# Строки, которые МОГУТ затесаться в блок аффиксов — отбрасываем
AFFIX_BLOCK_SKIP = (
    "quality:", "sockets:", "rarity:", "requires", "item class:",
    "item level:", "corrupted", "unidentified",
)


def _is_affix_line(line: str, skip_markers: tuple) -> bool:
    low = line.lower()
    return not any(low.startswith(m) for m in skip_markers)


def _first_number(line: str) -> int:
    m = re.search(r"([+-]?\d+)", line)
    return int(m.group(1)) if m else 0


def parse_socket_colors(text_after_colon: str) -> str:
    """'Red Green Red' / 'R G R' -> 'RGR'"""
    out = []
    for tok in re.split(r"[\s,/–—-]+", text_after_colon or ""):
        c = COLOR_TOKENS.get(tok.lower())
        if c:
            out.append(c)
    return "".join(out)


# ----------------------------------------------------------------------
# Разбор предмета
# ----------------------------------------------------------------------

def parse_item(text: str) -> dict:
    """
    Разбирает текст тултипа предмета.

    Формат clipboard'а PoE: блоки, разделённые строками "--------".
    Блок аффиксов — тот, что непосредственно перед блоком "Rarity:".

    Возвращает dict:
      name, rarity, quality, sockets, socket_count,
      affixes (list[str]), affix_count, corrupted, unidentified, raw
    """
    empty = {
        "name": "", "rarity": "", "quality": None, "sockets": "",
        "socket_count": 0, "affixes": [], "affix_count": 0,
        "corrupted": False, "unidentified": False, "raw": text or "",
    }
    if not text or not text.strip():
        return empty

    raw_lines = [l.rstrip() for l in text.strip().splitlines()]
    lines = [l.strip() for l in raw_lines if l.strip()]

    name = lines[0] if lines else ""
    rarity = ""
    quality = None
    sockets = ""
    corrupted = False
    unidentified = False

    for l in lines:
        low = l.lower()
        if low.startswith("rarity:"):
            rarity = l.split(":", 1)[1].strip()
        elif low.startswith("quality:"):
            m = re.search(r"(\d+)", l)
            if m:
                quality = int(m.group(1))
        elif low.startswith("sockets:"):
            sockets = parse_socket_colors(l.split(":", 1)[1])
        elif low == "corrupted":
            corrupted = True
        elif low.startswith("unidentified"):
            unidentified = True

    # Разбиваем на блоки
    blocks, cur = [], []
    for l in raw_lines:
        s = l.strip()
        if s.startswith("--------"):
            blocks.append(cur)
            cur = []
        else:
            cur.append(s)
    blocks.append(cur)

    # Блок аффиксов = блок перед блоком "Rarity:"
    affixes = []
    for i, block in enumerate(blocks):
        if any(l.lower().startswith("rarity:") for l in block):
            if i > 0:
                affixes = [l for l in blocks[i - 1]
                           if l and _is_affix_line(l, AFFIX_BLOCK_SKIP)]
            break

    if not affixes:
        # FALLBACK: OCR или нестандартный формат — старый построчный подход
        for l in lines:
            low = l.lower()
            if low.startswith("--------"):
                continue
            if any(low.startswith(m) for m in FALLBACK_MARKERS):
                continue
            if any(ch.isdigit() for ch in l) or "%" in l:
                affixes.append(l)

    return {
        "name": name,
        "rarity": rarity,
        "quality": quality,
        "sockets": sockets,
        "socket_count": len(sockets),
        "affixes": affixes,
        "affix_count": len(affixes),
        "corrupted": corrupted,
        "unidentified": unidentified,
        "raw": text,
    }


# ----------------------------------------------------------------------
# Совместимость со старым item_parser
# ----------------------------------------------------------------------

def get_rarity(item_text: str) -> str:
    return parse_item(item_text)["rarity"]


def get_mod_lines(item_text: str) -> list:
    return parse_item(item_text)["affixes"]


def has_target_mod(item_text: str, target_mods: list) -> bool:
    joined = " | ".join(get_mod_lines(item_text)).lower()
    return any(t.lower() in joined for t in target_mods)


def mod_count(item_text: str) -> int:
    return len(get_mod_lines(item_text))


# ----------------------------------------------------------------------
# Оценка целевых модов
# ----------------------------------------------------------------------

def evaluate(item: dict, targets: list, total_weight: int = 0) -> dict:
    """
    Проверяет целевые моды на предмете.

    target = {"name": str, "min_value": int (0 = не важно), "weight": int}

    Успех:
      * если total_weight > 0 — сумма весов найденных модов >= total_weight;
      * иначе — найдены ВСЕ целевые моды.
    """
    affixes = item.get("affixes", [])
    results = []
    weight_gained = 0
    total_weight = int(total_weight or 0)

    for t in targets:
        name = (t.get("name") or "").strip()
        min_value = int(t.get("min_value") or 0)
        weight = int(t.get("weight") or 1)
        found = False
        value = 0
        if name:
            best = 0
            for line in affixes:
                if name.lower() in line.lower():
                    v = _first_number(line)
                    if v > best:
                        best = v
                    if v >= min_value:
                        found = True
                        value = v
                        break
            if not found:
                value = best
        results.append({
            "name": name,
            "min_value": min_value,
            "weight": weight,
            "found": found,
            "value": value,
        })
        if found:
            weight_gained += weight

    if total_weight > 0:
        success = weight_gained >= total_weight
    else:
        success = bool(results) and all(r["found"] for r in results)

    return {
        "success": success,
        "weight_gained": weight_gained,
        "weight_total": total_weight,
        "results": results,
    }


# ----------------------------------------------------------------------
# Решение: какая валюта следующая
# ----------------------------------------------------------------------

def _deck_chance(m: dict) -> float:
    try:
        return float(m.get("deck_chance", 0) or 0)
    except (TypeError, ValueError):
        return 0.0


def decide_action(item: dict, ev: dict, methods: dict, excluded_mods: list,
                  state: dict, mcount: int, rng=None) -> str:
    """
    Выбирает следующую валюту для предмета (когда цель ещё НЕ достигнута).

    mcount — количество реальных аффиксов (без implicit).
    Возвращает ключ метода или "stop_*".
    """
    rng = rng or random
    m = methods or {}

    # --- Редкий предмет: помогает только Eldritch ---
    if item.get("rarity") == "Rare":
        return "eldritch" if m.get("eldritch") else "stop_rare_no_eldritch"

    if item.get("rarity") != "Magic":
        return "stop_not_magic"

    # --- Магический предмет ---

    # 1. Vaal Orb — убрать "плохой" мод из списка исключений
    if m.get("vaal"):
        for line in item.get("affixes", []):
            if any(x.strip().lower() in line.lower()
                   for x in excluded_mods if x and x.strip()):
                return "vaal"

    # 2. Essence — при достаточном качестве и малом числе модов
    if m.get("essence"):
        max_uses = int(m.get("max_essence_uses", 5) or 5)
        if state.get("essence_uses", 0) < max_uses:
            q = item.get("quality")
            need_q = int(m.get("essence_quality", 0) or 0)
            if q is not None and q >= need_q and mcount <= 1:
                return "essence"

    # 3. По количеству модов
    if mcount <= 0:
        if m.get("augmentation"):
            return "augmentation"
        if m.get("alteration"):
            return "alteration"
        return "stop_no_method"

    if mcount == 1:
        if m.get("augmentation"):
            return "augmentation"
        if m.get("chaos"):
            return "chaos"
        if m.get("stacked_deck") and rng.random() * 100 < _deck_chance(m):
            return "stacked_deck"
        if m.get("alteration"):
            return "alteration"
        return "stop_no_method"

    # mcount >= 2
    if m.get("stacked_deck") and rng.random() * 100 < _deck_chance(m):
        return "stacked_deck"
    if m.get("chaos"):
        return "chaos"
    if m.get("alteration"):
        return "alteration"
    return "stop_no_method"


# ----------------------------------------------------------------------
# Человекочитаемые имена (для лога)
# ----------------------------------------------------------------------

METHOD_NAMES = {
    "augmentation": "Orb of Augmentation",
    "alteration": "Orb of Alteration",
    "chaos": "Chaos Orb",
    "vaal": "Vaal Orb",
    "essence": "Essence",
    "stacked_deck": "Stacked Deck",
    "chance": "Orb of Chance",
    "alchemy": "Alchemy Orb",
    "eldritch": "Eldritch Orb",
}

STOP_MESSAGES = {
    "stopped": "Остановлено пользователем",
    "success": "Целевые моды найдены!",
    "success_rare": "Рейр крафнут, цели достигнуты",
    "corrupted": "Предмет коррупнут — остановка",
    "unidentified": "Предмет не идентифицирован",
    "stop_not_magic": "Предмет не Magic — делать нечего",
    "stop_rare_no_eldritch": "Предмет уже Rare, но Eldritch Orb не включён",
    "stop_no_method": "Не включён ни один подходящий метод крафта",
    "read_error": "Не удаётся прочитать предмет",
    "max_attempts": "Достигнут максимум попыток",
    "limit": "Достигнут лимит валюты (пауза)",
    "no_position": "Не задана позиция валюты",
}


def format_progress(item: dict, ev: dict, implicit: int = 0) -> str:
    """Компактная строка прогресса для лога."""
    mcount = max(0, item.get("affix_count", 0) - max(0, implicit))
    if ev["weight_total"] > 0:
        weight = f"{ev['weight_gained']}/{ev['weight_total']} веса"
    else:
        found_n = sum(1 for r in ev["results"] if r["found"])
        weight = f"{found_n}/{len(ev['results'])} модов"
    q = f", quality {item['quality']}%" if item.get("quality") is not None else ""
    s = f", соккеты {item['sockets']}" if item.get("sockets") else ""
    return f"{item.get('rarity', '?')}, аффиксов: {mcount}{q}{s}, цель: {weight}"
