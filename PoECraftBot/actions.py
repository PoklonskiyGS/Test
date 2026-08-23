"""
Мышиные действия (Windows / pydirectinput).

Стандартное применение валюты в PoE:
  ПКМ по валюте в stash -> ЛКМ по предмету.
"""
import time
import random

import pydirectinput


def random_jitter(base: float, jitter: float = 0.15) -> float:
    """Лёгкая рандомизация задержки (human-like, как в Path of Craft)."""
    if jitter <= 0:
        return max(0.0, base)
    return base * random.uniform(max(0.0, 1.0 - jitter), 1.0 + jitter)


def apply_currency(currency_pos, item_pos,
                   click_delay: float = 0.12,
                   server_delay: float = 0.25,
                   jitter: float = 0.15):
    """
    Применяет валюту к предмету:
      1) правый клик по позиции валюты (stash)
      2) левый клик по позиции предмета
    """
    cx, cy = currency_pos
    ix, iy = item_pos

    pydirectinput.moveTo(cx, cy)
    time.sleep(random_jitter(click_delay, jitter))
    pydirectinput.click(button="right")
    time.sleep(random_jitter(click_delay, jitter))

    pydirectinput.moveTo(ix, iy)
    pydirectinput.click(button="left")
    time.sleep(random_jitter(server_delay, jitter))
