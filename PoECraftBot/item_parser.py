"""
Парсинг текста предмета
"""
NON_MOD_MARKERS = (
    "Item Class:", "Rarity:", "Requirements:", "Sockets:",
    "Item Level:", "Quality:", "Armour:", "Evasion Rating:",
    "Energy Shield:", "Physical Damage:", "Elemental Damage:",
    "Critical Strike Chance:", "Attacks per Second:", "Weapon Range:",
    "Chance to Block:", "Limited to:", "Corrupted", "Unidentified",
)

def get_rarity(item_text: str) -> str:
    for line in item_text.splitlines():
        if line.startswith("Rarity:"):
            return line.split(":", 1)[1].strip()
    return ""

def get_mod_lines(item_text: str) -> list:
    blocks = item_text.split("--------")
    mod_lines = []
    
    for block in blocks:
        lines = [l.strip() for l in block.strip().splitlines() if l.strip()]
        if not lines:
            continue
        if any(any(line.startswith(m) for m in NON_MOD_MARKERS) for line in lines):
            continue
        for line in lines:
            if any(ch.isdigit() for ch in line) or "%" in line:
                mod_lines.append(line)
    return mod_lines

def has_target_mod(item_text: str, target_mods: list) -> bool:
    mods = get_mod_lines(item_text)
    joined = " | ".join(mods).lower()
    return any(target.lower() in joined for target in target_mods)

def mod_count(item_text: str) -> int:
    return len(get_mod_lines(item_text))