"""
Чтение текста предмета из игры (Ctrl+C или OCR)
"""
import time
import pydirectinput
import pyperclip
import config

def read_item_text_ctrl_c(item_pos, hover_delay: float = 0.05) -> str:
    """Оригинальный метод через Ctrl+C"""
    x, y = item_pos
    pydirectinput.moveTo(x, y)
    time.sleep(hover_delay)
    
    pyperclip.copy("")
    pydirectinput.keyDown("ctrl")
    pydirectinput.press("c")
    pydirectinput.keyUp("ctrl")
    time.sleep(0.05)
    
    return pyperclip.paste()


def read_item_text(item_pos, hover_delay: float = 0.05) -> str:
    """Читает текст предмета (OCR если включен, иначе Ctrl+C)"""
    if config.USE_OCR:
        try:
            from ocr_reader import read_item_text as read_ocr
            return read_ocr(item_pos, hover_delay)
        except Exception as e:
            print(f"[OCR Fallback] {e}")
            return read_item_text_ctrl_c(item_pos, hover_delay)
    else:
        return read_item_text_ctrl_c(item_pos, hover_delay)