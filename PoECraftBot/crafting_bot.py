"""
Логика Alt + Augment спама с поддержкой числовых модов
"""
import time
import re
import pydirectinput
import config
from item_parser import get_rarity, has_target_mod, mod_count
from item_reader import read_item_text


def has_target_mod_with_value(item_text: str, target_mods_with_values: list) -> tuple:
    """
    Проверяет наличие модов с числовыми значениями
    Возвращает: (найден_ли, детали_поиска)
    """
    if not target_mods_with_values:
        return False, []
    
    results = []
    mods = []
    
    # Получаем строки модов
    blocks = item_text.split("--------")
    for block in blocks:
        lines = [l.strip() for l in block.strip().splitlines() if l.strip()]
        if not lines:
            continue
        for line in lines:
            if any(ch.isdigit() for ch in line) or "%" in line:
                mods.append(line)
    
    for target in target_mods_with_values:
        target_name = target.get("name", "").lower()
        min_value = target.get("min_value", 0)
        found = False
        value = 0
        
        for mod in mods:
            if target_name in mod.lower():
                numbers = re.findall(r'([+-]?\d+)', mod)
                if numbers:
                    value = int(numbers[0])
                    if value >= min_value:
                        found = True
                        break
        
        results.append({
            "name": target["name"],
            "found": found,
            "value": value,
            "required": min_value,
            "success": found and value >= min_value
        })
    
    all_found = all(r["success"] for r in results) if results else False
    return all_found, results


def apply_currency(currency_pos, item_pos):
    cx, cy = currency_pos
    ix, iy = item_pos
    
    pydirectinput.moveTo(cx, cy)
    pydirectinput.click(button="right")
    time.sleep(config.CLICK_DELAY)
    
    pydirectinput.moveTo(ix, iy)
    pydirectinput.click(button="left")
    time.sleep(config.SERVER_RESPONSE_DELAY)


def run(positions, should_stop) -> bool:
    item_pos = tuple(positions["item"])
    alt_pos = tuple(positions["alteration_orb"])
    aug_pos = tuple(positions["augmentation_orb"])
    
    print("\n" + "="*60)
    print("[INFO] Запуск крафт-бота")
    print(f"[INFO] Позиция предмета: {item_pos}")
    print(f"[INFO] OCR включен: {config.USE_OCR}")
    print(f"[INFO] Целевые моды: {config.TARGET_MODS}")
    print(f"[INFO] Моды с значениями: {config.TARGET_MODS_WITH_VALUES}")
    print("="*60 + "\n")
    
    attempts = 0
    error_count = 0
    
    while attempts < config.MAX_ATTEMPTS:
        if should_stop():
            print("[STOP] Остановлено пользователем.")
            return False
        
        attempts += 1
        
        try:
            item_text = read_item_text(item_pos)
        except Exception as e:
            print(f"[ERROR] Ошибка чтения: {e}")
            error_count += 1
            if error_count > 5:
                print("[ERROR] Слишком много ошибок!")
                return False
            time.sleep(0.5)
            continue
        
        if not item_text or not item_text.strip():
            print(f"[!] Пустой текст (попытка {attempts})")
            error_count += 1
            if error_count > 3:
                print("[!] Предмет не читается! Проверьте позицию.")
                return False
            time.sleep(0.5)
            continue
        
        rarity = get_rarity(item_text)
        
        if attempts == 1:
            print(f"[DEBUG] Rarity: '{rarity}'")
            print(f"[DEBUG] Текст: {item_text[:200]}")
        
        if rarity != "Magic":
            print(f"[!] Предмет не Magic (rarity='{rarity}')")
            return False
        
        mods_now = mod_count(item_text) - config.IMPLICIT_MOD_COUNT
        
        # === ПРОВЕРКА МОДОВ ===
        found = False
        found_details = []
        
        # 1. Простые моды
        if config.TARGET_MODS:
            found_simple = has_target_mod(item_text, config.TARGET_MODS)
            if found_simple:
                found = True
                found_details.append("Найден простой мод")
        
        # 2. Моды с числовыми значениями
        if config.TARGET_MODS_WITH_VALUES:
            found_value, value_results = has_target_mod_with_value(
                item_text, config.TARGET_MODS_WITH_VALUES
            )
            if found_value:
                found = True
                for r in value_results:
                    if r["success"]:
                        found_details.append(f"{r['name']} >= {r['required']} (найдено {r['value']})")
            elif attempts <= 5 or attempts % 20 == 0:
                for r in value_results:
                    if r["found"]:
                        print(f"  ⚠️ {r['name']}: найдено {r['value']}, нужно >= {r['required']}")
                    else:
                        print(f"  ❌ {r['name']}: не найден")
        
        if attempts <= 5 or attempts % 20 == 0:
            print(f"[{attempts}] Модов: {mods_now}, Целевой найден: {found}")
            if found_details:
                print(f"  ✅ {', '.join(found_details)}")
        
        # === ПРИНЯТИЕ РЕШЕНИЯ ===
        if mods_now >= 2:
            if found:
                print(f"\n✅ УСПЕХ! Найдено за {attempts} попыток")
                print(f"✅ {', '.join(found_details)}")
                return True
            if attempts % 10 == 0:
                print(f"[{attempts}] Реролл Alteration...")
            apply_currency(alt_pos, item_pos)
            continue
        
        if mods_now == 1:
            if attempts % 10 == 0:
                print(f"[{attempts}] Добавляю Augment...")
            apply_currency(aug_pos, item_pos)
            continue
        
        if attempts % 10 == 0:
            print(f"[{attempts}] 0 модов - реролл...")
        apply_currency(alt_pos, item_pos)
    
    print("[!] Достигнут MAX_ATTEMPTS")
    return False