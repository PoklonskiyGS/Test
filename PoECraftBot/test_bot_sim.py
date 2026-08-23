"""
Симуляция полного цикла бота БЕЗ игры:
подменяем чтение предмета и мышиные клики фейками и проверяем
последовательность действий бота.

Запуск:  python test_bot_sim.py
"""
import sys
import os
import types

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ---- стабы Windows-модулей ----
def _stub(name):
    mod = types.ModuleType(name)
    sys.modules[name] = mod
    return mod

pdi = _stub("pydirectinput")
pdi.moveTo = lambda *a, **k: None
pdi.click = lambda *a, **k: None
pdi.keyDown = lambda *a, **k: None
pdi.keyUp = lambda *a, **k: None
pdi.press = lambda *a, **k: None

pc = _stub("pyperclip")
pc.copy = lambda *a: None
pc.paste = lambda *a: ""

pa = _stub("pyautogui")
pa.position = lambda: (0, 0)
pa.size = lambda: (1920, 1080)

import crafting_bot as cb  # noqa: E402

# ----------------------------------------------------------------------
# Текст предметов (формат clipboard'а PoE)
# ----------------------------------------------------------------------

HEAD = "Flickerstriders\nBoots\n--------\nArmour: 39\n--------\n"
TAIL = "--------\nRarity: Magic\nItem Class: Boots\nRequires Level 8\n--------\n"

MAGIC_ONE = HEAD + "+8 to Dexterity\n" + TAIL
MAGIC_TWO_HIT = HEAD + "+8 to Dexterity\n10% increased Movement Speed\n" + TAIL
MAGIC_TWO_MISS = HEAD + "+8 to Dexterity\n+12 to Strength\n" + TAIL

SOCKETS_RGB = "Sockets: Red Green Blue\n--------\n"
SOCKETS_RBR = "Sockets: Red Blue Red\n--------\n"
MAGIC_HIT_RGB = HEAD + SOCKETS_RGB + "+8 to Dexterity\n10% increased Movement Speed\n" + TAIL
MAGIC_HIT_RBR = HEAD + SOCKETS_RBR + "+8 to Dexterity\n10% increased Movement Speed\n" + TAIL

RARE_HIT = ("Brutal Grief\nRare Two-Handed Axe\n--------\n"
            "Physical Damage: 112 to 168\nAttack Speed: 0.80\n--------\n"
            "+25 to Strength\n20% increased Axe Damage\n10% increased Movement Speed\n"
            "--------\nRarity: Rare\nItem Class: Two-Handed Axes\nRequires Level 35\n--------\n")

CORRUPTED = HEAD + "+8 to Dexterity\nCorrupted\n" + TAIL

UNIDENTIFIED = ("Unidentified\n--------\nRarity: Magic\nItem Class: Boots\n--------\n")


class FakeGame:
    """Ложная игра: выдаёт предзаданные тексты, записывает «клик» по валюте."""

    POS = {
        "item": (999, 999), "alteration": (20, 20), "augmentation": (30, 30),
        "chaos": (40, 40), "alchemy": (50, 50), "vaal": (60, 60),
        "chance": (70, 70), "essence": (80, 80), "stacked_deck": (90, 90),
        "eldritch": (100, 100),
    }

    def __init__(self, reads, fallback=None):
        self.reads = list(reads)
        self.fallback = fallback
        self.applied = []
        self._key_by_pos = {v: k for k, v in self.POS.items()}

    def read(self, pos):
        if self.reads:
            return self.reads.pop(0)
        return self.fallback or ""

    def apply(self, cpos, ipos, cd=0.0, sd=0.0, jitter=0.0):
        self.applied.append(self._key_by_pos[tuple(cpos)])


def make_recipe(**kw):
    r = {
        "targets": [{"name": "Movement Speed", "min_value": 0, "weight": 1}],
        "total_weight": 0,
        "excluded_mods": [],
        "methods": {"augmentation": True, "alteration": True},
        "implicit_count": 0,
        "click_delay": 0.0,
        "server_delay": 0.0,
        "max_attempts": 100,
        "max_currency_uses": 0,
    }
    r.update(kw)
    return r


def run_case(game, recipe):
    cb.apply_currency = game.apply
    cb.read_item_text = game.read
    logs = []
    status, message = cb.run(FakeGame.POS, recipe, lambda: False, log=logs.append)
    return status, message, game.applied


# ----------------------------------------------------------------------
# Сценарии
# ----------------------------------------------------------------------

def s1_augment_until_hit():
    g = FakeGame([MAGIC_ONE, MAGIC_TWO_HIT])
    status, _, applied = run_case(g, make_recipe())
    assert status == "success", status
    assert applied == ["augmentation"], applied


def s2_weight_success():
    g = FakeGame([MAGIC_TWO_HIT])
    recipe = make_recipe(
        targets=[{"name": "Movement Speed", "min_value": 0, "weight": 2},
                 {"name": "to maximum Life", "min_value": 0, "weight": 2}],
        total_weight=2)
    status, _, applied = run_case(g, recipe)
    assert status == "success", status
    assert applied == [], applied


def s3_chaos_alchemy_eldritch():
    g = FakeGame([MAGIC_TWO_MISS, MAGIC_TWO_HIT, RARE_HIT])
    recipe = make_recipe(methods={
        "chaos": True, "alchemy_finish": True, "eldritch": True})
    status, _, applied = run_case(g, recipe)
    assert status == "success_rare", (status, applied)
    assert applied == ["chaos", "alchemy"], applied


def s4_currency_limit():
    g = FakeGame([MAGIC_TWO_MISS], fallback=MAGIC_TWO_MISS)
    recipe = make_recipe(max_currency_uses=1)
    status, _, applied = run_case(g, recipe)
    assert status == "limit", status
    assert applied == ["alteration"], applied


def s5_corrupted():
    g = FakeGame([CORRUPTED])
    status, _, applied = run_case(g, make_recipe())
    assert status == "corrupted", status
    assert applied == [], applied


def s6_chance_pattern():
    g = FakeGame([MAGIC_HIT_RGB, MAGIC_HIT_RBR])
    recipe = make_recipe(methods={
        "augmentation": True, "alteration": True,
        "chance": True, "chance_pattern": "RBR", "chance_max_rolls": 5})
    status, _, applied = run_case(g, recipe)
    assert status == "success", status
    assert applied == ["chance"], applied


def s7_unidentified():
    g = FakeGame([UNIDENTIFIED])
    status, _, _ = run_case(g, make_recipe())
    assert status == "unidentified", status


# ----------------------------------------------------------------------

CASES = [v for k, v in sorted(globals().items()) if k.startswith("s") and callable(v)]


def main():
    failed = 0
    for c in CASES:
        try:
            c()
            print(f"✅ {c.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"❌ {c.__name__}: {e}")
        except Exception as e:
            failed += 1
            print(f"❌ {c.__name__}: {type(e).__name__}: {e}")
    print("-" * 40)
    print(f"Пройдено: {len(CASES) - failed}/{len(CASES)}")
    return failed


if __name__ == "__main__":
    raise SystemExit(1 if main() else 0)
