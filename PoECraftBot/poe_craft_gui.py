"""
Полноценный GUI для PoE Craft Bot с базой предметов
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config_gui import BotConfig
from item_database import (
    ITEM_LIST, ITEM_DATABASE, AVAILABLE_MODS,
    get_item_info, get_implicit_count,
    get_default_value_mods
)


class PoECraftGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PoE Craft Bot v2.0")
        self.root.geometry("750x820")
        self.root.resizable(False, False)
        
        self.is_running = False
        self.bot_thread = None
        self.positions = {}
        self.config = BotConfig()
        self.selected_item_key = "boots"
        
        self.setup_styles()
        self.create_widgets()
        self.load_config()
        self.setup_hotkeys()
        self.setup_position_hotkeys()
        self.update_positions_status()
        self.update_ocr_status()
        
    def setup_styles(self):
        style = ttk.Style()
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Status.TLabel', font=('Arial', 10))
        style.configure('Hotkey.TLabel', font=('Arial', 8, 'bold'), foreground='blue')
        style.configure('Title.TLabel', font=('Arial', 10, 'bold'))
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        header = ttk.Label(main_frame, text="⚙️ PoE Craft Bot v2.0", style='Header.TLabel')
        header.pack(pady=(0, 15))
        
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Вкладки
        self.create_item_database_tab(notebook)
        self.create_mods_tab(notebook)
        self.create_settings_tab(notebook)
        self.create_positions_tab(notebook)
        self.create_hotkeys_tab(notebook)
        
        # Статус бар
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_label = ttk.Label(status_frame, text="⚪ Готов к работе", style='Status.TLabel')
        self.status_label.pack(side=tk.LEFT)
        
        # Кнопки управления
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.start_btn = ttk.Button(control_frame, text="▶ Запустить", 
                                   command=self.toggle_bot, width=15)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="■ Остановить", 
                  command=self.stop_bot, width=15).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="💾 Сохранить", 
                  command=self.save_config, width=15).pack(side=tk.RIGHT, padx=5)
        
        # Лог
        log_frame = ttk.LabelFrame(main_frame, text="📋 Лог", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, font=('Consolas', 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
    
    # ============================================================
    # ВКЛАДКА 1: БАЗА ПРЕДМЕТОВ
    # ============================================================
    
    def create_item_database_tab(self, notebook):
        """Вкладка с базой предметов"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="📦 База предметов")
        
        # === 1. ВЫБОР ПРЕДМЕТА ===
        select_frame = ttk.LabelFrame(tab, text="1️⃣ Выберите тип предмета", padding="10")
        select_frame.pack(fill=tk.X, pady=5, padx=10)
        
        ttk.Label(select_frame, text="Тип предмета:").pack(anchor=tk.W)
        
        self.item_type_var = tk.StringVar()
        self.item_type_combo = ttk.Combobox(select_frame, textvariable=self.item_type_var,
                                            values=[name for _, name in ITEM_LIST],
                                            state="readonly", width=35)
        self.item_type_combo.pack(fill=tk.X, pady=5)
        self.item_type_combo.bind('<<ComboboxSelected>>', self.on_item_selected)
        
        # === 2. ИНФОРМАЦИЯ О ПРЕДМЕТЕ ===
        info_frame = ttk.LabelFrame(tab, text="📋 Информация о предмете", padding="10")
        info_frame.pack(fill=tk.X, pady=5, padx=10)
        
        self.item_info_text = tk.Text(info_frame, height=5, font=('Consolas', 9), bg='#f0f0f0')
        self.item_info_text.pack(fill=tk.X)
        
        # === 3. ВЫБОР МОДОВ ===
        mods_frame = ttk.LabelFrame(tab, text="2️⃣ Выберите моды для поиска", padding="10")
        mods_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=10)
        
        # Поиск модов
        search_frame = ttk.Frame(mods_frame)
        search_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(search_frame, text="🔍 Поиск мода:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.mod_search_entry = ttk.Entry(search_frame, width=25)
        self.mod_search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.mod_search_entry.bind('<KeyRelease>', self.filter_available_mods)
        
        # Список доступных модов
        list_frame = ttk.Frame(mods_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.available_mods_listbox = tk.Listbox(list_frame, height=6, 
                                                  yscrollcommand=scrollbar.set,
                                                  font=('Arial', 9))
        self.available_mods_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.available_mods_listbox.yview)
        
        # Кнопки управления модами
        btn_frame = ttk.Frame(mods_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="→ Добавить мод", 
                  command=self.add_mod_from_list).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="← Удалить мод", 
                  command=self.remove_selected_simple_mod).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="🗑️ Очистить все", 
                  command=self.clear_all_selected_mods).pack(side=tk.LEFT, padx=2)
        
        # Список выбранных модов
        ttk.Label(mods_frame, text="✅ Выбранные моды:", style='Title.TLabel').pack(anchor=tk.W, pady=(10, 0))
        
        self.selected_mods_listbox = tk.Listbox(mods_frame, height=4, font=('Arial', 9))
        self.selected_mods_listbox.pack(fill=tk.X, pady=5)
        
        # === 4. КНОПКИ ПРИМЕНЕНИЯ ===
        btn_frame2 = ttk.Frame(tab)
        btn_frame2.pack(fill=tk.X, pady=10, padx=10)
        
        ttk.Button(btn_frame2, text="✅ Применить настройки", 
                  command=self.apply_item_preset).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame2, text="🔄 Сбросить", 
                  command=self.reset_item_selection).pack(side=tk.LEFT, padx=5)
        
        # Загружаем первый предмет
        if ITEM_LIST:
            self.item_type_combo.set(ITEM_LIST[0][1])
            self.on_item_selected(None)
        
        # Загружаем доступные моды
        self.load_available_mods()
    
    # ============================================================
    # МЕТОДЫ ДЛЯ РАБОТЫ С БАЗОЙ ПРЕДМЕТОВ
    # ============================================================
    
    def load_available_mods(self, filter_text=""):
        """Загружает список доступных модов с фильтром"""
        from item_database import AVAILABLE_MODS
        
        self.available_mods_listbox.delete(0, tk.END)
        
        filter_lower = filter_text.lower()
        for mod in sorted(AVAILABLE_MODS):
            if filter_text == "" or filter_lower in mod.lower():
                self.available_mods_listbox.insert(tk.END, mod)
    
    def filter_available_mods(self, event):
        """Фильтрует список модов при вводе"""
        filter_text = self.mod_search_entry.get().strip()
        self.load_available_mods(filter_text)
    
    def add_mod_from_list(self):
        """Добавляет выбранный мод из списка доступных в выбранные"""
        selection = self.available_mods_listbox.curselection()
        if selection:
            mod = self.available_mods_listbox.get(selection[0])
            # Проверяем, нет ли уже такого мода
            current_mods = list(self.selected_mods_listbox.get(0, tk.END))
            if mod not in current_mods:
                self.selected_mods_listbox.insert(tk.END, mod)
                self.log(f"➕ Добавлен мод: {mod}")
                self.save_config()
    
    def remove_selected_simple_mod(self):
        """Удаляет выбранный мод из списка выбранных"""
        selection = self.selected_mods_listbox.curselection()
        if selection:
            mod = self.selected_mods_listbox.get(selection[0])
            self.selected_mods_listbox.delete(selection[0])
            self.log(f"➖ Удален мод: {mod}")
            self.save_config()
    
    def clear_all_selected_mods(self):
        """Очищает все выбранные моды"""
        self.selected_mods_listbox.delete(0, tk.END)
        self.log("🗑️ Все выбранные моды очищены")
        self.save_config()
    
    def on_item_selected(self, event):
        """Обработчик выбора предмета"""
        selected = self.item_type_var.get()
        
        item_key = None
        for key, name in ITEM_LIST:
            if name == selected:
                item_key = key
                break
        
        if not item_key:
            return
        
        self.selected_item_key = item_key
        info = get_item_info(item_key)
        
        # Обновляем информацию
        text = f"""
📋 {info.get('icon', '')} {info.get('name', 'Неизвестно')}
─────────────────────────────────────
📌 Implicit модов: {info.get('implicit_count', 0)}
📌 Implicit моды: {', '.join(info.get('implicit_mods', ['Нет'])) if info.get('implicit_mods') else 'Нет'}
        """
        self.item_info_text.delete(1.0, tk.END)
        self.item_info_text.insert(1.0, text)
    
    def apply_item_preset(self):
        """Применяет настройки для выбранного предмета"""
        if not hasattr(self, 'selected_item_key') or not self.selected_item_key:
            self.log("⚠️ Сначала выберите предмет!")
            return
        
        item_key = self.selected_item_key
        info = get_item_info(item_key)
        
        # 1. Устанавливаем implicit
        implicit_count = info.get('implicit_count', 0)
        self.implicit_var.set(implicit_count)
        
        # 2. Очищаем текущие моды в основных списках
        self.simple_mods_listbox.delete(0, tk.END)
        for item in self.value_mods_tree.get_children():
            self.value_mods_tree.delete(item)
        
        # 3. Добавляем моды из списка выбранных
        selected_mods = list(self.selected_mods_listbox.get(0, tk.END))
        for mod in selected_mods:
            self.simple_mods_listbox.insert(tk.END, mod)
        
        # 4. Добавляем моды с числовыми значениями (только для выбранных)
        default_mods = get_default_value_mods(item_key)
        for mod in default_mods:
            if mod['name'] in selected_mods:
                self.value_mods_tree.insert('', 'end', text=mod['name'], values=(mod['min_value'],))
        
        self.log(f"✅ Применены настройки для {info.get('name', 'предмета')}")
        self.log(f"   Implicit модов: {implicit_count}")
        self.log(f"   Выбрано модов: {len(selected_mods)}")
        
        self.save_config()
    
    def reset_item_selection(self):
        """Сброс выбора"""
        self.selected_mods_listbox.delete(0, tk.END)
        self.simple_mods_listbox.delete(0, tk.END)
        for item in self.value_mods_tree.get_children():
            self.value_mods_tree.delete(item)
        self.mod_search_entry.delete(0, tk.END)
        self.load_available_mods()
        self.log("🔄 Все настройки сброшены")
        self.save_config()
    
    # ============================================================
    # ВКЛАДКА 2: МОДЫ
    # ============================================================
    
    def create_mods_tab(self, notebook):
        """Вкладка с модами (основная)"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="🎯 Моды")
        
        # Информация
        info_label = ttk.Label(tab, text="Здесь отображаются моды, которые будут искаться ботом", 
                              font=('Arial', 9), foreground="gray")
        info_label.pack(anchor=tk.W, pady=5, padx=10)
        
        # Простые моды
        simple_frame = ttk.LabelFrame(tab, text="📝 Простые моды (поиск по строке)", padding="10")
        simple_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=10)
        
        self.simple_mods_listbox = tk.Listbox(simple_frame, height=5, font=('Arial', 9))
        self.simple_mods_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        input_frame = ttk.Frame(simple_frame)
        input_frame.pack(fill=tk.X)
        
        ttk.Label(input_frame, text="Добавить мод:").pack(side=tk.LEFT, padx=(0, 5))
        self.simple_mod_entry = ttk.Entry(input_frame, width=30)
        self.simple_mod_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.simple_mod_entry.bind('<Return>', lambda e: self.add_simple_mod())
        
        ttk.Button(input_frame, text="Добавить", command=self.add_simple_mod).pack(side=tk.LEFT, padx=2)
        ttk.Button(input_frame, text="Удалить", command=self.delete_simple_mod).pack(side=tk.LEFT, padx=2)
        
        # Моды с числовыми значениями
        value_frame = ttk.LabelFrame(tab, text="📊 Моды с числовыми значениями", padding="10")
        value_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=10)
        
        columns = ('min',)
        self.value_mods_tree = ttk.Treeview(value_frame, columns=columns, height=4)
        self.value_mods_tree.heading('#0', text='Название мода')
        self.value_mods_tree.heading('min', text='Мин. значение')
        self.value_mods_tree.column('#0', width=250)
        self.value_mods_tree.column('min', width=120)
        self.value_mods_tree.pack(fill=tk.BOTH, expand=True, pady=5)
        
        value_input_frame = ttk.Frame(value_frame)
        value_input_frame.pack(fill=tk.X)
        
        ttk.Label(value_input_frame, text="Мод:").pack(side=tk.LEFT, padx=(0, 5))
        self.value_mod_name = ttk.Entry(value_input_frame, width=25)
        self.value_mod_name.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Label(value_input_frame, text="Мин.:").pack(side=tk.LEFT, padx=(0, 5))
        self.value_mod_min = ttk.Entry(value_input_frame, width=8)
        self.value_mod_min.pack(side=tk.LEFT, padx=(0, 5))
        self.value_mod_min.insert(0, "25")
        
        ttk.Button(value_input_frame, text="Добавить", command=self.add_value_mod).pack(side=tk.LEFT, padx=2)
        ttk.Button(value_input_frame, text="Удалить", command=self.delete_value_mod).pack(side=tk.LEFT, padx=2)
    
    # ============================================================
    # МЕТОДЫ ДЛЯ РАБОТЫ С МОДАМИ
    # ============================================================
    
    def add_simple_mod(self):
        """Добавляет простой мод"""
        mod = self.simple_mod_entry.get().strip()
        if mod:
            current_mods = list(self.simple_mods_listbox.get(0, tk.END))
            if mod not in current_mods:
                self.simple_mods_listbox.insert(tk.END, mod)
                self.simple_mod_entry.delete(0, tk.END)
                self.log(f"➕ Добавлен мод: {mod}")
                self.save_config()
    
    def delete_simple_mod(self):
        """Удаляет выбранный простой мод"""
        selection = self.simple_mods_listbox.curselection()
        if selection:
            mod = self.simple_mods_listbox.get(selection[0])
            self.simple_mods_listbox.delete(selection[0])
            self.log(f"➖ Удален мод: {mod}")
            self.save_config()
    
    def add_value_mod(self):
        """Добавляет мод с числовым значением"""
        name = self.value_mod_name.get().strip()
        min_val = self.value_mod_min.get().strip()
        
        if name and min_val:
            try:
                min_val = int(min_val)
                exists = False
                for item in self.value_mods_tree.get_children():
                    values = self.value_mods_tree.item(item)
                    if values['text'] == name:
                        exists = True
                        break
                if not exists:
                    self.value_mods_tree.insert('', 'end', text=name, values=(min_val,))
                    self.value_mod_name.delete(0, tk.END)
                    self.log(f"➕ Добавлен мод: {name} >= {min_val}")
                    self.save_config()
                else:
                    self.log(f"⚠️ Мод '{name}' уже существует")
            except ValueError:
                self.log("❌ Ошибка: значение должно быть числом")
    
    def delete_value_mod(self):
        """Удаляет выбранный мод с числовым значением"""
        selection = self.value_mods_tree.selection()
        if selection:
            item = self.value_mods_tree.item(selection[0])
            self.value_mods_tree.delete(selection[0])
            self.log(f"➖ Удален мод: {item['text']}")
            self.save_config()
    
    # ============================================================
    # ВКЛАДКА 3: НАСТРОЙКИ
    # ============================================================
    
    def create_settings_tab(self, notebook):
        """Вкладка с настройками"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="⚙️ Настройки")
        
        settings_frame = ttk.LabelFrame(tab, text="Параметры крафта", padding="15")
        settings_frame.pack(fill=tk.X, pady=10, padx=10)
        
        # Implicit моды
        row = ttk.Frame(settings_frame)
        row.pack(fill=tk.X, pady=5)
        ttk.Label(row, text="Implicit модов:").pack(side=tk.LEFT, padx=(0, 10))
        self.implicit_var = tk.IntVar(value=1)
        ttk.Spinbox(row, from_=0, to=5, textvariable=self.implicit_var, width=5).pack(side=tk.LEFT)
        
        # Стоп на количестве модов
        row = ttk.Frame(settings_frame)
        row.pack(fill=tk.X, pady=5)
        ttk.Label(row, text="Останавливаться при:").pack(side=tk.LEFT, padx=(0, 10))
        self.stop_count_var = tk.IntVar(value=2)
        ttk.Spinbox(row, from_=1, to=6, textvariable=self.stop_count_var, width=5).pack(side=tk.LEFT)
        ttk.Label(row, text="модах").pack(side=tk.LEFT, padx=(5, 0))
        
        # Задержки
        row = ttk.Frame(settings_frame)
        row.pack(fill=tk.X, pady=5)
        ttk.Label(row, text="Задержка клика (сек):").pack(side=tk.LEFT, padx=(0, 10))
        self.click_delay_var = tk.DoubleVar(value=0.12)
        ttk.Entry(row, textvariable=self.click_delay_var, width=5).pack(side=tk.LEFT)
        
        row = ttk.Frame(settings_frame)
        row.pack(fill=tk.X, pady=5)
        ttk.Label(row, text="Задержка сервера (сек):").pack(side=tk.LEFT, padx=(0, 10))
        self.server_delay_var = tk.DoubleVar(value=0.25)
        ttk.Entry(row, textvariable=self.server_delay_var, width=5).pack(side=tk.LEFT)
        
        row = ttk.Frame(settings_frame)
        row.pack(fill=tk.X, pady=5)
        ttk.Label(row, text="Макс. попыток:").pack(side=tk.LEFT, padx=(0, 10))
        self.max_attempts_var = tk.IntVar(value=2000)
        ttk.Entry(row, textvariable=self.max_attempts_var, width=8).pack(side=tk.LEFT)
        
        # OCR
        row = ttk.Frame(settings_frame)
        row.pack(fill=tk.X, pady=5)
        self.use_ocr_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(row, text="Использовать OCR (без Ctrl+C)", 
                       variable=self.use_ocr_var, command=self.toggle_ocr).pack(side=tk.LEFT)
        
        # Статус OCR
        self.ocr_status_label = ttk.Label(settings_frame, text="", font=('Arial', 9))
        self.ocr_status_label.pack(anchor=tk.W, pady=5)
    
    def toggle_ocr(self):
        """Включает/выключает OCR"""
        import config
        config.USE_OCR = self.use_ocr_var.get()
        self.update_ocr_status()
        self.log(f"OCR {'включен' if config.USE_OCR else 'выключен'}")
        self.save_config()
    
    def update_ocr_status(self):
        """Обновляет статус OCR"""
        try:
            from ocr_reader import TESSERACT_PATH
            if TESSERACT_PATH:
                status = "✅ OCR доступен" if self.use_ocr_var.get() else "⏹️ OCR отключен"
                self.ocr_status_label.config(text=f"{status} (Tesseract: {TESSERACT_PATH})", foreground="green")
            else:
                self.ocr_status_label.config(text="❌ OCR не доступен (установите Tesseract)", foreground="red")
        except:
            self.ocr_status_label.config(text="❌ OCR не доступен", foreground="red")
    
    # ============================================================
    # ВКЛАДКА 4: ПОЗИЦИИ
    # ============================================================
    
    def create_positions_tab(self, notebook):
        """Вкладка с позициями"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="📌 Позиции")
        
        hotkey_frame = ttk.LabelFrame(tab, text="⌨️ Горячие клавиши для захвата", padding="10")
        hotkey_frame.pack(fill=tk.X, pady=5, padx=10)
        
        hotkeys_info = """
        Ctrl + 1  →  Захватить позицию предмета
        Ctrl + 2  →  Захватить позицию Orb of Alteration
        Ctrl + 3  →  Захватить позицию Orb of Augmentation
        
        📌 Как использовать:
        1. Наведите курсор на элемент в игре
        2. Нажмите соответствующую комбинацию клавиш
        3. Услышите звуковой сигнал - позиция сохранена!
        """
        info_label = ttk.Label(hotkey_frame, text=hotkeys_info, font=('Arial', 9),
                              justify=tk.LEFT, foreground="gray")
        info_label.pack(anchor=tk.W, pady=5)
        
        positions = [
            ("item", "Предмет", "🎯", "Ctrl+1"),
            ("alteration_orb", "Orb of Alteration", "🔵", "Ctrl+2"),
            ("augmentation_orb", "Orb of Augmentation", "🟢", "Ctrl+3"),
        ]
        
        for key, name, icon, hotkey in positions:
            frame = ttk.Frame(tab)
            frame.pack(fill=tk.X, pady=5, padx=20)
            
            label = ttk.Label(frame, text=f"{icon} {name}:")
            label.pack(side=tk.LEFT, padx=(0, 10))
            
            pos_label = ttk.Label(frame, text="Не задано", foreground="gray")
            pos_label.pack(side=tk.LEFT, expand=True)
            setattr(self, f"{key}_pos_label", pos_label)
            
            ttk.Button(frame, text="Задать", command=lambda k=key: self.capture_position(k)).pack(side=tk.RIGHT, padx=2)
            ttk.Label(frame, text=hotkey, style='Hotkey.TLabel').pack(side=tk.RIGHT, padx=2)
        
        ttk.Button(tab, text="🗑️ Очистить все позиции", command=self.clear_positions).pack(pady=20)
        
        stat_frame = ttk.LabelFrame(tab, text="📊 Статус позиций", padding="10")
        stat_frame.pack(fill=tk.X, padx=20, pady=10)
        self.pos_status_label = ttk.Label(stat_frame, text="Позиции не заданы", foreground="gray")
        self.pos_status_label.pack()
    
    # ============================================================
    # МЕТОДЫ ДЛЯ РАБОТЫ С ПОЗИЦИЯМИ
    # ============================================================
    
    def setup_position_hotkeys(self):
        """Настраивает горячие клавиши для захвата позиций"""
        try:
            import keyboard
            for hotkey in ['ctrl+1', 'ctrl+2', 'ctrl+3']:
                try:
                    keyboard.remove_hotkey(hotkey)
                except:
                    pass
            keyboard.add_hotkey('ctrl+1', lambda: self.capture_position_hotkey('item'))
            keyboard.add_hotkey('ctrl+2', lambda: self.capture_position_hotkey('alteration_orb'))
            keyboard.add_hotkey('ctrl+3', lambda: self.capture_position_hotkey('augmentation_orb'))
            self.log("⌨️ Хоткеи для позиций: Ctrl+1, Ctrl+2, Ctrl+3")
        except Exception as e:
            self.log(f"⚠️ Ошибка хоткеев: {e}")
    
    def capture_position_hotkey(self, pos_name):
        """Захватывает позицию через горячую клавишу"""
        try:
            import pyautogui
            import winsound
            x, y = pyautogui.position()
            screen_width, screen_height = pyautogui.size()
            if not (0 <= x <= screen_width and 0 <= y <= screen_height):
                self.log(f"⚠️ Координаты ({x}, {y}) вне экрана!")
                return
            self.positions[pos_name] = [x, y]
            label = getattr(self, f"{pos_name}_pos_label")
            label.config(text=f"({x}, {y})", foreground="green")
            winsound.Beep(1000, 150)
            winsound.Beep(1200, 100)
            names = {"item": "Предмет", "alteration_orb": "Alteration", "augmentation_orb": "Augmentation"}
            self.log(f"🎯 {names.get(pos_name)}: ({x}, {y})")
            self.save_config()
            self.update_positions_status()
        except Exception as e:
            self.log(f"❌ Ошибка: {e}")
    
    def capture_position(self, pos_name):
        """Захватывает текущую позицию мыши (через кнопку)"""
        try:
            import pyautogui
            import winsound
            x, y = pyautogui.position()
            self.positions[pos_name] = [x, y]
            label = getattr(self, f"{pos_name}_pos_label")
            label.config(text=f"({x}, {y})", foreground="green")
            winsound.Beep(1000, 100)
            names = {"item": "Предмет", "alteration_orb": "Alteration", "augmentation_orb": "Augmentation"}
            self.log(f"📌 {names.get(pos_name)}: ({x}, {y})")
            self.save_config()
            self.update_positions_status()
        except Exception as e:
            self.log(f"❌ Ошибка: {e}")
    
    def clear_positions(self):
        """Очищает все позиции"""
        self.positions = {}
        for key in ["item", "alteration_orb", "augmentation_orb"]:
            label = getattr(self, f"{key}_pos_label")
            label.config(text="Не задано", foreground="gray")
        self.log("🗑️ Все позиции очищены")
        self.save_config()
        self.update_positions_status()
    
    def update_positions_status(self):
        """Обновляет статус позиций"""
        required = ["item", "alteration_orb", "augmentation_orb"]
        set_positions = [p for p in required if p in self.positions]
        if len(set_positions) == 3:
            self.pos_status_label.config(text="✅ Все позиции заданы!", foreground="green")
        elif len(set_positions) > 0:
            missing = [p for p in required if p not in self.positions]
            self.pos_status_label.config(text=f"⚠️ Задано: {len(set_positions)}/3. Не хватает: {', '.join(missing)}", foreground="orange")
        else:
            self.pos_status_label.config(text="❌ Позиции не заданы", foreground="red")
    
    # ============================================================
    # ВКЛАДКА 5: ХОТКЕИ
    # ============================================================
    
    def create_hotkeys_tab(self, notebook):
        """Вкладка с хоткеями"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="⌨️ Хоткеи")
        
        info = ttk.Label(tab, text="Настройка глобальных горячих клавиш", font=('Arial', 10))
        info.pack(pady=10)
        
        frame1 = ttk.Frame(tab)
        frame1.pack(fill=tk.X, pady=10, padx=20)
        ttk.Label(frame1, text="Старт/Пауза:").pack(side=tk.LEFT, padx=(0, 10))
        self.toggle_hotkey_var = tk.StringVar(value="F8")
        ttk.Entry(frame1, textvariable=self.toggle_hotkey_var, width=10).pack(side=tk.LEFT)
        
        frame2 = ttk.Frame(tab)
        frame2.pack(fill=tk.X, pady=10, padx=20)
        ttk.Label(frame2, text="Выход:").pack(side=tk.LEFT, padx=(0, 10))
        self.quit_hotkey_var = tk.StringVar(value="F9")
        ttk.Entry(frame2, textvariable=self.quit_hotkey_var, width=10).pack(side=tk.LEFT)
        
        info_frame = ttk.LabelFrame(tab, text="Информация", padding="10")
        info_frame.pack(fill=tk.X, padx=20, pady=10)
        ttk.Label(info_frame, text="Хоткеи работают даже когда PoE в фокусе", wraplength=400).pack()
        ttk.Label(info_frame, text="Для позиций: Ctrl+1, Ctrl+2, Ctrl+3", wraplength=400, foreground="blue").pack()
    
    # ============================================================
    # МЕТОДЫ ДЛЯ ХОТКЕЕВ
    # ============================================================
    
    def setup_hotkeys(self):
        """Настраивает горячие клавиши"""
        try:
            import keyboard
            keyboard.unhook_all()
            toggle_key = self.toggle_hotkey_var.get().lower()
            quit_key = self.quit_hotkey_var.get().lower()
            keyboard.add_hotkey(toggle_key, self.toggle_bot)
            keyboard.add_hotkey(quit_key, self.emergency_stop)
            self.log(f"⌨️ Хоткеи: {toggle_key} - старт/пауза, {quit_key} - выход")
        except Exception as e:
            self.log(f"⚠️ Ошибка хоткеев: {e}")
    
    def emergency_stop(self):
        """Аварийная остановка"""
        self.stop_bot()
        self.log("🛑 Аварийная остановка!")
        self.root.after(100, self.root.destroy)
    
    # ============================================================
    # МЕТОДЫ УПРАВЛЕНИЯ БОТОМ
    # ============================================================
    
    def toggle_bot(self):
        """Включает/выключает бота"""
        if not self.is_running:
            self.start_bot()
        else:
            self.stop_bot()
    
    def start_bot(self):
        """Запускает бота"""
        # Проверяем наличие позиций
        required_positions = ["item", "alteration_orb", "augmentation_orb"]
        missing = [p for p in required_positions if p not in self.positions]
        if missing:
            messagebox.showwarning("Ошибка", f"Не заданы позиции: {', '.join(missing)}")
            return
        
        # Проверяем наличие модов
        simple_mods = list(self.simple_mods_listbox.get(0, tk.END))
        value_mods = []
        for item in self.value_mods_tree.get_children():
            values = self.value_mods_tree.item(item)
            value_mods.append({
                "name": values['text'],
                "min_value": values['values'][0]
            })
        
        if not simple_mods and not value_mods:
            messagebox.showwarning("Ошибка", "Не заданы целевые моды!")
            return
        
        self.is_running = True
        self.start_btn.config(text="⏸ Пауза")
        self.status_label.config(text="🟢 Бот запущен", foreground="green")
        self.log("🚀 Запуск бота...")
        
        # Сохраняем настройки перед запуском
        self.save_config()
        
        # Запускаем бота в отдельном потоке
        self.bot_thread = threading.Thread(target=self.run_bot, daemon=True)
        self.bot_thread.start()
    
    def stop_bot(self):
        """Останавливает бота"""
        self.is_running = False
        self.start_btn.config(text="▶ Запустить")
        self.status_label.config(text="🔴 Бот остановлен", foreground="red")
        self.log("⏹ Бот остановлен")
    
    def run_bot(self):
        """Основной цикл бота (запускается в отдельном потоке)"""
        try:
            import config as bot_config
            from crafting_bot import run
            
            # Обновляем конфигурацию из GUI
            bot_config.TARGET_MODS = list(self.simple_mods_listbox.get(0, tk.END))
            
            bot_config.TARGET_MODS_WITH_VALUES = []
            for item in self.value_mods_tree.get_children():
                values = self.value_mods_tree.item(item)
                bot_config.TARGET_MODS_WITH_VALUES.append({
                    "name": values['text'],
                    "min_value": values['values'][0]
                })
            
            bot_config.IMPLICIT_MOD_COUNT = self.implicit_var.get()
            bot_config.STOP_AFTER_MOD_COUNT = self.stop_count_var.get()
            bot_config.CLICK_DELAY = self.click_delay_var.get()
            bot_config.SERVER_RESPONSE_DELAY = self.server_delay_var.get()
            bot_config.MAX_ATTEMPTS = self.max_attempts_var.get()
            bot_config.USE_OCR = self.use_ocr_var.get()
            
            positions = self.positions.copy()
            
            def should_stop():
                return not self.is_running
            
            self.log("🔄 Начинаю крафт...")
            success = run(positions, should_stop)
            
            if success:
                self.log("✅ КРАФТ ЗАВЕРШЕН УСПЕШНО!")
                self.status_label.config(text="✅ Успех!", foreground="green")
            else:
                self.log("❌ Крафт завершен без результата")
                self.status_label.config(text="❌ Неудача", foreground="red")
        except Exception as e:
            self.log(f"❌ Ошибка в боте: {e}")
            import traceback
            self.log(traceback.format_exc())
            self.status_label.config(text="❌ Ошибка", foreground="red")
        finally:
            self.is_running = False
            self.root.after(0, lambda: self.start_btn.config(text="▶ Запустить"))
    
    # ============================================================
    # МЕТОДЫ СОХРАНЕНИЯ/ЗАГРУЗКИ
    # ============================================================
    
    def load_config(self):
        """Загружает конфигурацию из файла"""
        try:
            config = self.config.get("config", {})
            
            # Загружаем моды
            for mod in config.get("target_mods", []):
                self.simple_mods_listbox.insert(tk.END, mod)
                self.selected_mods_listbox.insert(tk.END, mod)
            
            for mod in config.get("target_mods_with_values", []):
                self.value_mods_tree.insert('', 'end', text=mod.get("name", ""), values=(mod.get("min_value", 0),))
            
            # Загружаем позиции
            self.positions = config.get("positions", {})
            for key, coords in self.positions.items():
                label = getattr(self, f"{key}_pos_label", None)
                if label:
                    label.config(text=f"({coords[0]}, {coords[1]})", foreground="green")
            
            # Загружаем настройки
            settings = config.get("settings", {})
            self.implicit_var.set(settings.get("implicit_mod_count", 1))
            self.stop_count_var.set(settings.get("stop_after_mod_count", 2))
            self.click_delay_var.set(settings.get("click_delay", 0.12))
            self.server_delay_var.set(settings.get("server_response_delay", 0.25))
            self.max_attempts_var.set(settings.get("max_attempts", 2000))
            self.use_ocr_var.set(settings.get("use_ocr", False))
            
            # Загружаем хоткеи
            hotkeys = config.get("hotkeys", {})
            self.toggle_hotkey_var.set(hotkeys.get("toggle", "F8"))
            self.quit_hotkey_var.set(hotkeys.get("quit", "F9"))
            
            # Загружаем выбранный предмет
            selected = config.get("selected_item", "boots")
            for key, name in ITEM_LIST:
                if key == selected:
                    self.item_type_combo.set(name)
                    self.selected_item_key = key
                    self.on_item_selected(None)
                    break
            
            self.log("📂 Конфигурация загружена")
            self.update_positions_status()
            self.update_ocr_status()
            
        except Exception as e:
            self.log(f"Ошибка загрузки: {e}")
    
    def save_config(self):
        """Сохраняет конфигурацию в файл"""
        try:
            config = {
                "target_mods": list(self.simple_mods_listbox.get(0, tk.END)),
                "target_mods_with_values": [],
                "positions": self.positions,
                "selected_item": getattr(self, 'selected_item_key', 'boots'),
                "settings": {
                    "implicit_mod_count": self.implicit_var.get(),
                    "stop_after_mod_count": self.stop_count_var.get(),
                    "click_delay": self.click_delay_var.get(),
                    "server_response_delay": self.server_delay_var.get(),
                    "max_attempts": self.max_attempts_var.get(),
                    "use_ocr": self.use_ocr_var.get(),
                },
                "hotkeys": {
                    "toggle": self.toggle_hotkey_var.get(),
                    "quit": self.quit_hotkey_var.get()
                }
            }
            
            for item in self.value_mods_tree.get_children():
                values = self.value_mods_tree.item(item)
                config["target_mods_with_values"].append({
                    "name": values['text'],
                    "min_value": values['values'][0]
                })
            
            self.config.config = config
            self.config.save()
            self.log("💾 Конфигурация сохранена")
        except Exception as e:
            self.log(f"Ошибка сохранения: {e}")
    
    # ============================================================
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    # ============================================================
    
    def log(self, message):
        """Добавляет сообщение в лог"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()