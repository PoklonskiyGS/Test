"""
Запуск GUI-версии PoE Craft Bot
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import tkinter as tk
except ImportError:
    print("Ошибка: tkinter не установлен!")
    print("Установите: pip install tk")
    sys.exit(1)

try:
    from poe_craft_gui import PoECraftGUI
except ImportError as e:
    print(f"Ошибка импорта GUI: {e}")
    print("Убедитесь, что файл poe_craft_gui.py существует")
    sys.exit(1)

def main():
    try:
        root = tk.Tk()
        app = PoECraftGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"Ошибка запуска: {e}")
        import traceback
        traceback.print_exc()
        input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()