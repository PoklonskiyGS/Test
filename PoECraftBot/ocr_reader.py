"""
Чтение текста предмета через OCR (без Ctrl+C)
"""
import time
import cv2
import numpy as np
import pytesseract
from PIL import ImageGrab
import os
import subprocess

# Пути к Tesseract
TESSERACT_PATHS = [
    r'C:\Program Files\Tesseract-OCR\tesseract.exe',
    r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
    os.path.expanduser(r'~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'),
]

def find_tesseract():
    """Автоматически ищет путь к tesseract.exe"""
    for path in TESSERACT_PATHS:
        if os.path.exists(path):
            return path
    
    try:
        result = subprocess.run(['where', 'tesseract'], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip().split('\n')[0]
    except:
        pass
    
    return None

TESSERACT_PATH = find_tesseract()
if TESSERACT_PATH:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    print(f"[OCR] Tesseract найден: {TESSERACT_PATH}")
else:
    print("[WARNING] Tesseract не найден! Будет использован Ctrl+C")
    print("Скачайте Tesseract: https://github.com/UB-Mannheim/tesseract/wiki")


def read_item_text_ocr(item_pos, region_size=(180, 300)):
    """
    Читает текст предмета через OCR без использования Ctrl+C
    """
    if not TESSERACT_PATH:
        from item_reader import read_item_text_ctrl_c
        return read_item_text_ctrl_c(item_pos)
    
    x, y = item_pos
    
    # Захватываем область вокруг предмета
    left = max(0, x - region_size[0]//2)
    top = max(0, y - region_size[1]//2)
    right = x + region_size[0]//2
    bottom = y + region_size[1]//2
    
    screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
    
    # Конвертируем в массив OpenCV
    img = np.array(screenshot)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    
    # Предобработка
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, 11, 2)
    denoised = cv2.medianBlur(thresh, 3)
    
    # Распознаем текст
    custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789%+-/() '
    text = pytesseract.image_to_string(denoised, config=custom_config)
    
    return text


def read_item_text(item_pos, hover_delay: float = 0.05) -> str:
    """
    Основная функция чтения предмета (использует OCR если доступно)
    """
    import pydirectinput
    
    x, y = item_pos
    pydirectinput.moveTo(x, y)
    time.sleep(hover_delay)
    
    try:
        if TESSERACT_PATH:
            text = read_item_text_ocr(item_pos)
            if text and len(text.strip()) > 10:
                return text
    except Exception as e:
        print(f"[OCR] Ошибка: {e}, переключение на Ctrl+C")
    
    # Fallback на Ctrl+C
    from item_reader import read_item_text_ctrl_c
    return read_item_text_ctrl_c(item_pos)