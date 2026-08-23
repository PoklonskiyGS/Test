"""
Тесты движка крафта (чистая логика, без игры).
Запуск:  python test_engine.py
"""
import random

from craft_engine import (
    parse_item, evaluate, decide_action, parse_socket_colors,
    get_rarity, mod_count,
)

# ----------------------------------------------------------------------
# Образцы текста (формат clipboard'а PoE)
# ----------------------------------------------------------------------

MAGIC_BOOTS = """Flickerstriders
Boots
--------
Armour: 39
--------
Quality: +5%
--------
+8 to Dexterity
10% increased Movement Speed
--------
Rarity: Magic
Item Class: Boots
Requires Level 8
--------
"""

RARE_AXE = """Brutal Grief
Rare Two-Handed Axe
--------
Physical Damage: 112 to 168
Attack Speed: 0.80
--------
+25 to Strength
20% increased Axe Damage
Adds 25 to 40 Physical Damage
--------
Rarity: Rare
Item Class: Two-Handed Axes
Requires Level 35
--------
"""

MAGIC_DAGGER = """Basilisk Stab
Dagger
--------
Physical Damage: 12 to 21
Critical Hit Chance: 5%
Attack Speed: 1.70
--------
Sockets: Red Blue Red
--------
+10 to Strength
20% increased Critical Strike Chance
--------
Rarity: Magic
Item Class: Daggers
Requires Level 15
--------
"""

QUALITY_ITEM = """Sneaky Greaves
Boots
--------
Armour: 45
--------
Quality: +40%
--------
+10 to Dexterity
--------
Rarity: Magic
Item Class: Boots
Requires Level 10
--------
"""

OCR_FALLBACK = """Flickerstriders
Boots
Armour: 39
+8 to Dexterity
10% increased Movement Speed
"""

CORRUPTED_ITEM = """Flickerstriders
Boots
--------
Armour: 39
--------
+8 to Dexterity
Corrupted
--------
Rarity: Magic
Item Class: Boots
Requires Level 8
--------
"""


# ----------------------------------------------------------------------
# Тесты
# ----------------------------------------------------------------------

def test_parse_magic():
    item = parse_item(MAGIC_BOOTS)
    assert item["rarity"] == "Magic", item
    assert item["quality"] == 5
    assert item["affix_count"] == 2, item["affixes"]
    assert any("Movement Speed" in a for a in item["affixes"])
    assert not item["corrupted"]
    assert not item["unidentified"]
    assert item["name"] == "Flickerstriders"


def test_parse_rare():
    item = parse_item(RARE_AXE)
    assert item["rarity"] == "Rare", item
    assert item["affix_count"] == 3, item["affixes"]
    # «Adds 25 to 40 Physical Damage» — это аффикс рейра, не база
    assert any("Adds 25 to 40" in a for a in item["affixes"]), item["affixes"]
    # базовый «Physical Damage: 112 to 168» не должен попасть в аффиксы
    assert not any(a.startswith("Physical Damage:") for a in item["affixes"])


def test_sockets():
    item = parse_item(MAGIC_DAGGER)
    assert item["sockets"] == "RBR", item["sockets"]
    assert item["socket_count"] == 3
    assert parse_socket_colors("G G G") == "GGG"
    assert parse_socket_colors("Green Blue") == "GB"
    assert parse_socket_colors("") == ""


def test_corrupted():
    item = parse_item(CORRUPTED_ITEM)
    assert item["corrupted"] is True
    assert item["affix_count"] == 1


def test_ocr_fallback():
    item = parse_item(OCR_FALLBACK)
    # без «Rarity:» — fallback: считаем только строки с цифрами
    assert item["affix_count"] == 2, item["affixes"]
    assert not any("Armour" in a for a in item["affixes"])
    assert get_rarity(OCR_FALLBACK) == ""
    assert mod_count(OCR_FALLBACK) == 2


def test_evaluate_simple():
    item = parse_item(MAGIC_BOOTS)
    ev = evaluate(item, [{"name": "Movement Speed", "min_value": 0, "weight": 1}])
    assert ev["success"] is True
    assert ev["weight_gained"] == 1


def test_evaluate_value():
    item = parse_item(MAGIC_BOOTS)
    ev = evaluate(item, [{"name": "Movement Speed", "min_value": 15, "weight": 1}])
    assert ev["success"] is False          # 10 < 15
    assert ev["results"][0]["value"] == 10
    ev2 = evaluate(item, [{"name": "Movement Speed", "min_value": 10, "weight": 1}])
    assert ev2["success"] is True


def test_evaluate_weight():
    item = parse_item(MAGIC_BOOTS)
    targets = [
        {"name": "Movement Speed", "min_value": 0, "weight": 2},
        {"name": "to maximum Life", "min_value": 0, "weight": 2},
    ]
    ev = evaluate(item, targets, total_weight=4)
    assert ev["success"] is False
    assert ev["weight_gained"] == 2
    ev2 = evaluate(item, targets, total_weight=2)
    assert ev2["success"] is True          # 2 >= 2
    # total_weight=0 -> все моды
    ev3 = evaluate(item, targets, total_weight=0)
    assert ev3["success"] is False


def test_decide_augmentation():
    item = parse_item(MAGIC_BOOTS)
    methods = {"augmentation": True, "alteration": True}
    ev = evaluate(item, [{"name": "to maximum Life", "min_value": 0, "weight": 1}])
    assert decide_action(item, ev, methods, [], {}, mcount=1) == "augmentation"
    # 0 модов -> тоже augmentation
    assert decide_action(item, ev, methods, [], {}, mcount=0) == "augmentation"


def test_decide_alteration():
    item = parse_item(MAGIC_BOOTS)
    methods = {"augmentation": True, "alteration": True}
    ev = evaluate(item, [{"name": "to maximum Life", "min_value": 0, "weight": 1}])
    # 2 мода: augmentation не может добавить третий -> reroll
    assert decide_action(item, ev, methods, [], {}, mcount=2,
                         rng=random.Random(42)) == "alteration"


def test_decide_chaos():
    item = parse_item(MAGIC_BOOTS)
    methods = {"augmentation": True, "chaos": True}
    ev = evaluate(item, [{"name": "Life", "min_value": 0, "weight": 1}])
    assert decide_action(item, ev, methods, [], {}, mcount=2,
                         rng=random.Random(1)) == "chaos"


def test_decide_deck():
    item = parse_item(MAGIC_BOOTS)
    methods = {"stacked_deck": True, "deck_chance": 100}
    ev = evaluate(item, [{"name": "Life", "min_value": 0, "weight": 1}])
    assert decide_action(item, ev, methods, [], {}, mcount=2,
                         rng=random.Random(1)) == "stacked_deck"
    # 0% -> deck не применяется
    methods0 = {"stacked_deck": True, "deck_chance": 0, "alteration": True}
    assert decide_action(item, ev, methods0, [], {}, mcount=2,
                         rng=random.Random(1)) == "alteration"


def test_decide_vaal():
    item = parse_item(MAGIC_BOOTS)
    methods = {"augmentation": True, "vaal": True}
    ev = evaluate(item, [{"name": "Life", "min_value": 0, "weight": 1}])
    action = decide_action(item, ev, methods, ["Movement Speed"], {}, mcount=2,
                           rng=random.Random(1))
    assert action == "vaal"
    # без совпадения исключений — не vaal
    action2 = decide_action(item, ev, methods, ["to maximum Life"], {}, mcount=2,
                            rng=random.Random(1))
    assert action2 != "vaal"


def test_decide_essence():
    item = parse_item(QUALITY_ITEM)  # quality 40%, 1 мод
    methods = {"augmentation": True, "essence": True,
               "essence_quality": 30, "max_essence_uses": 5}
    ev = evaluate(item, [{"name": "Life", "min_value": 0, "weight": 1}])
    assert decide_action(item, ev, methods, [], {}, mcount=1) == "essence"
    # лимит капаний исчерпан -> augmentation
    state = {"essence_uses": 5}
    assert decide_action(item, ev, methods, [], state, mcount=1) == "augmentation"
    # не хватает качества
    methods_lowq = dict(methods, essence_quality=90)
    assert decide_action(item, ev, methods_lowq, [], {}, mcount=1) == "augmentation"


def test_decide_rare():
    item = parse_item(RARE_AXE)
    ev = evaluate(item, [{"name": "Life", "min_value": 0, "weight": 1}])
    methods = {"eldritch": True}
    assert decide_action(item, ev, methods, [], {}, mcount=3) == "eldritch"
    assert decide_action(item, ev, {}, [], {}, mcount=3) == "stop_rare_no_eldritch"


def test_decide_normal_stop():
    item = parse_item(OCR_FALLBACK)
    ev = evaluate(item, [{"name": "Life", "min_value": 0, "weight": 1}])
    assert decide_action(item, ev, {"alteration": True}, [], {}, mcount=2) == "stop_not_magic"


def test_decide_no_method():
    item = parse_item(MAGIC_BOOTS)
    ev = evaluate(item, [{"name": "Life", "min_value": 0, "weight": 1}])
    assert decide_action(item, ev, {}, [], {}, mcount=2) == "stop_no_method"


# ----------------------------------------------------------------------

TESTS = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]


def main():
    failed = 0
    for t in TESTS:
        try:
            t()
            print(f"✅ {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"❌ {t.__name__}: {e}")
        except Exception as e:
            failed += 1
            print(f"❌ {t.__name__}: {type(e).__name__}: {e}")
    print("-" * 40)
    print(f"Пройдено: {len(TESTS) - failed}/{len(TESTS)}")
    return failed


if __name__ == "__main__":
    raise SystemExit(1 if main() else 0)
