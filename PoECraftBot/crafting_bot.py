"""
Основной цикл крафта (стиль Path of Craft Basic).

Порядок работы:
  1. Читаем предмет (Ctrl+C или OCR)
  2. Парсим: редкость, аффиксы, quality, цвета соккетов
  3. Оцениваем цели (простые моды / по значению / по ВЕСУ)
  4. Если цель достигнута:
       - Orb of Chance (цвета соккетов, если включён и задан паттерн)
       - Alchemy Orb (сделать Rare, если включён "Alchemy в финале")
       - Фаза Rare: Eldritch Orb (если включён)
  5. Иначе — решаем следующую валюту и применяем
  6. Лимит использований валюты -> пауза
"""
import time

import config
from craft_engine import (
    parse_item, evaluate, decide_action,
    METHOD_NAMES, STOP_MESSAGES, format_progress,
)
from item_reader import read_item_text
from actions import apply_currency


def run(positions, recipe, should_stop, log=print):
    """
    positions: {"item": [x, y], "chaos": [x, y], ...}
    recipe:    dict (схема BotConfig v2: targets, methods, delays, ...)
    should_stop: callable() -> bool

    Возвращает (status, message).
    """
    item_pos = tuple(positions["item"])
    methods = recipe.get("methods", {}) or {}
    targets = recipe.get("targets", []) or []
    total_weight = int(recipe.get("total_weight", 0) or 0)
    excluded = [x for x in (recipe.get("excluded_mods") or []) if x and x.strip()]
    implicit = int(recipe.get("implicit_count", 0) or 0)
    click_delay = float(recipe.get("click_delay", 0.12))
    server_delay = float(recipe.get("server_delay", 0.25))
    max_attempts = int(recipe.get("max_attempts", 2000))
    max_uses = int(recipe.get("max_currency_uses", 0) or 0)

    if not targets:
        return ("no_position", "Не заданы целевые моды")

    state = {"essence_uses": 0}
    attempts = 0
    uses = 0
    read_errors = 0

    log("")
    log("=" * 62)
    log("⚒️  СТАРТ КРАФТА (режим Path of Craft)")
    enabled = ", ".join(METHOD_NAMES[k] for k in METHOD_NAMES if methods.get(k))
    log(f"   Целевых модов: {len(targets)}"
        + (f", суммарный вес: {total_weight}" if total_weight > 0 else ""))
    log(f"   Методы: {enabled or '—'}")
    log(f"   Макс. попыток: {max_attempts}"
        + (f", лимит валюты: {max_uses}" if max_uses > 0 else ""))
    log(f"   Чтение: {'OCR' if config.USE_OCR else 'Ctrl+C'}")
    log("=" * 62 + "\n")

    # ---------- вспомогательные ----------

    def need_pos(key):
        if key not in positions or not positions[key]:
            log(f"[ERROR] Не задана позиция: {METHOD_NAMES.get(key, key)}")
            return None
        return tuple(positions[key])

    def do_apply(key):
        nonlocal uses
        pos = need_pos(key)
        if pos is None:
            return False
        apply_currency(pos, item_pos, click_delay, server_delay)
        uses += 1
        return True

    def limit_hit():
        if max_uses > 0 and uses >= max_uses:
            log(f"⏸️  ПАУЗА: достигнут лимит использований валюты ({max_uses})")
            return True
        return False

    def do_read():
        nonlocal read_errors
        try:
            text = read_item_text(item_pos)
        except Exception as e:
            log(f"[ERROR] Ошибка чтения: {e}")
            read_errors += 1
            return None
        if not text or not text.strip():
            read_errors += 1
            log(f"[!] Пустой текст (ошибок подряд: {read_errors})")
            return None
        read_errors = 0
        return text

    def log_progress(n, item, ev):
        if n <= 5 or n % 10 == 0:
            log(f"[{n}] {format_progress(item, ev, implicit)}")
            for r in ev["results"]:
                if r["found"]:
                    extra = f" = {r['value']}" if r["value"] else ""
                    log(f"   ✅ {r['name']}{extra}")
                else:
                    if r["value"] and r["min_value"]:
                        log(f"   ⚠️ {r['name']}: {r['value']} (нужно >= {r['min_value']})")
                    elif r["value"]:
                        log(f"   ⚠️ {r['name']}: значение не то")
                    else:
                        log(f"   ❌ {r['name']}: не найден")

    # ---------- главный цикл ----------

    while attempts < max_attempts:
        if should_stop():
            return ("stopped", STOP_MESSAGES["stopped"])
        if limit_hit():
            return ("limit", STOP_MESSAGES["limit"])

        attempts += 1
        text = do_read()
        if text is None:
            if read_errors >= 3:
                return ("read_error", STOP_MESSAGES["read_error"])
            time.sleep(0.4)
            continue

        item = parse_item(text)

        if not item["rarity"]:
            read_errors += 1
            if attempts <= 3:
                log(f"[DEBUG] Rarity не распознана: {text[:120]!r}")
            if read_errors >= 3:
                return ("read_error", "Rarity не распознана — проверьте позицию/OCR")
            time.sleep(0.3)
            continue
        read_errors = 0

        if item["corrupted"]:
            return ("corrupted", STOP_MESSAGES["corrupted"])
        if item["unidentified"]:
            return ("unidentified", STOP_MESSAGES["unidentified"])

        ev = evaluate(item, targets, total_weight)
        mcount = max(0, item["affix_count"] - max(0, implicit))
        log_progress(attempts, item, ev)

        # ================= УСПЕХ =================
        if ev["success"]:

            # --- Orb of Chance: цвета соккетов ---
            pattern = (methods.get("chance_pattern") or "").strip().upper()
            if methods.get("chance") and pattern:
                max_rolls = int(methods.get("chance_max_rolls", 10) or 10)
                for i in range(max_rolls):
                    if item["sockets"] == pattern:
                        break
                    if not item["sockets"]:
                        log("   ⚠️ Цвета соккетов не найдены в тексте — Chance пропущен")
                        break
                    log(f"   🎲 Chance {i + 1}/{max_rolls}: {item['sockets']} -> нужен {pattern}")
                    if not do_apply("chance"):
                        return ("no_position", f"Нет позиции: {METHOD_NAMES['chance']}")
                    if limit_hit():
                        return ("limit", STOP_MESSAGES["limit"])
                    text = do_read()
                    if text is None:
                        break
                    item = parse_item(text)
                    if item["corrupted"]:
                        return ("corrupted", STOP_MESSAGES["corrupted"])

            # --- Alchemy в финале ---
            if methods.get("alchemy_finish"):
                log("   🔮 Alchemy Orb (делаем Rare)...")
                if not do_apply("alchemy"):
                    return ("no_position", f"Нет позиции: {METHOD_NAMES['alchemy']}")
                if limit_hit():
                    return ("limit", STOP_MESSAGES["limit"])

                if methods.get("eldritch"):
                    # --- фаза Rare: Eldritch до цели ---
                    ok = False
                    while attempts < max_attempts:
                        if should_stop():
                            return ("stopped", STOP_MESSAGES["stopped"])
                        if limit_hit():
                            return ("limit", STOP_MESSAGES["limit"])
                        attempts += 1
                        text = do_read()
                        if text is None:
                            if read_errors >= 3:
                                return ("read_error", STOP_MESSAGES["read_error"])
                            time.sleep(0.3)
                            continue
                        item2 = parse_item(text)
                        if not item2["rarity"]:
                            time.sleep(0.3)
                            continue
                        if item2["corrupted"]:
                            return ("corrupted", STOP_MESSAGES["corrupted"])
                        ev2 = evaluate(item2, targets, total_weight)
                        log_progress(attempts, item2, ev2)
                        if ev2["success"]:
                            ok = True
                            break
                        log("   🌑 Eldritch Orb...")
                        if not do_apply("eldritch"):
                            return ("no_position", f"Нет позиции: {METHOD_NAMES['eldritch']}")
                    return ("success_rare",
                            "Рейр готов, цели достигнуты" if ok
                            else "Рейр: достигнут максимум попыток")

                return ("success", "Цели достигнуты, применён Alchemy Orb")

            return ("success", STOP_MESSAGES["success"])

        # ================= НЕ ДОСТИГНУТО: следующий шаг =================
        action = decide_action(item, ev, methods, excluded, state, mcount)

        if action in STOP_MESSAGES:
            return (action, STOP_MESSAGES[action])

        log(f"   → {METHOD_NAMES[action]}")
        if not do_apply(action):
            return ("no_position", f"Нет позиции: {METHOD_NAMES[action]}")
        if action == "essence":
            state["essence_uses"] += 1

    return ("max_attempts", STOP_MESSAGES["max_attempts"])
