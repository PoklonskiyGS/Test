"""
Тест чтения позиции
"""
import time
import json
import sys

try:
    from item_reader import read_item_text
except ImportError:
    print("❌ item_reader.py не найден!")
    sys.exit(1)

try:
    with open("positions.json", "r") as f:
        positions = json.load(f)
except FileNotFoundError:
    print("❌ positions.json не найден!")
    print("Сначала задайте позиции через GUI")
    sys.exit(1)

item_pos = tuple(positions.get("item", [0, 0]))
if item_pos == (0, 0):
    print("❌ Позиция предмета не задана!")
    sys.exit(1)

print(f"📌 Позиция предмета: {item_pos}")
print("🔄 Наведите курсор на предмет в игре...")
time.sleep(2)

print("\n📖 Читаю предмет...")
text = read_item_text(item_pos)

print(f"📊 Длина текста: {len(text)} символов")
print("-"*50)
print("ТЕКСТ ПРЕДМЕТА:")
print(text[:500] if text else "(пусто)")
print("-"*50)

if text and "Rarity:" in text:
    print("✅ Предмет читается нормально!")
    from item_parser import get_mod_lines
    mods = get_mod_lines(text)
    print(f"📊 Найдено модов: {len(mods)}")
    if mods:
        for i, mod in enumerate(mods, 1):
            print(f"  {i}. {mod}")
else:
    print("❌ Предмет не читается!")
    print("\nПроверьте:")
    print("1. Предмет в инвентаре")
    print("2. Включен 'Always Highlight'")
    print("3. Запуск от администратора")
    print("4. OCR установлен (если включен)")