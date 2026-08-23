"""
PoE Craft Bot v3.0 — полный GUI

Функционал в духе Path of Craft (Basic):
  ⚒️  Крафт множественными валютами:
      Augmentation, Alteration, Chaos, Vaal, Alchemy, Chance,
      Stacked Deck, Essence, Eldritch
  ⚖️  Крафт по весу модов (суммарный вес)
  ⏸️  Пауза по лимиту использований валюты
  🖱  Human-like задержки (лёгкая рандомизация)
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import queue
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config_gui import BotConfig
from item_database import (
    ITEM_LIST, AVAILABLE_MODS,
    get_item_info, get_default_value_mods,
)

# ----------------------------------------------------------------------
# Позиции и методы
# ----------------------------------------------------------------------

POSITIONS = [
    ("item",         "🎯 Предмет (в stash)",       "Ctrl+1"),
    ("alteration",   "🔵 Orb of Alteration",       "Ctrl+2"),
    ("augmentation", "🟢 Orb of Augmentation",     "Ctrl+3"),
    ("chaos",        "🟣 Chaos Orb",               "Ctrl+4"),
    ("alchemy",      "🔮 Alchemy Orb",             "Ctrl+5"),
    ("vaal",         "🖤 Vaal Orb",                "Ctrl+6"),
    ("chance",       "🎨 Orb of Chance",           "Ctrl+7"),
    ("essence",      "💧 Essence",                 "Ctrl+8"),
    ("stacked_deck", "🃏 Stacked Deck",            "Ctrl+9"),
    ("eldritch",     "🌑 Eldritch Orb",            "Ctrl+0"),
]

# метод (чекбокс во вкладке "Методы") -> позиция
METHOD_TO_POSITION = {
    "augmentation": "augmentation",
    "alteration": "alteration",
    "chaos": "chaos",
    "vaal": "vaal",
    "alchemy_finish": "alchemy",
    "chance": "chance",
    "essence": "essence",
    "stacked_deck": "stacked_deck",
    "eldritch": "eldritch",
}

METHOD_DEFAULTS = {
    "augmentation": True,
    "alteration": True,
    "chaos": False,
    "vaal": False,
    "alchemy_finish": False,
    "eldritch": False,
    "chance": False,
    "stacked_deck": False,
    "essence": False,
}

# (ключ, название, описание, параметры)
# параметр: (ключ_параметра, подпись, тип: "entry"|"int")
METHODS_SPEC = [
    ("augmentation",   "Orb of Augmentation", "добавляет второй мод magic-предмету", []),
    ("alteration",     "Orb of Alteration",   "рероллит один существующий мод", []),
    ("chaos",          "Chaos Orb",           "рероллит ВСЕ аффиксы magic-предмета", []),
    ("vaal",           "Vaal Orb",            "снимает «плохой» мод (из списка «Исключения»)", []),
    ("alchemy_finish", "Alchemy Orb в финале", "делает предмет Rare после достижения целей", []),
    ("eldritch",       "Eldritch Orb",        "рероллит аффиксы Rare (после Alchemy или на готовом рейре)", []),
    ("chance",         "Orb of Chance",       "рероллит цвета соккетов после успеха",
     [("chance_pattern", "Паттерн (напр. RGB, RRG):", "entry"),
      ("chance_max_rolls", "Макс. рероллов:", "int")]),
    ("stacked_deck",   "Stacked Deck",        "рероллит все аффиксы (вероятностно вместо Chaos/Alteration)",
     [("deck_chance", "Вероятность % (0–100):", "int")]),
    ("essence",        "Essence",             "капает на предмет с нужным качеством (сбрасывает аффиксы!)",
     [("essence_quality", "Нужное качество %:", "int"),
      ("max_essence_uses", "Макс. капаний за прогон:", "int")]),
]


class PoECraftGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PoE Craft Bot v3.0 — Path of Craft mode")
        self.root.geometry("900x880")
        self.root.minsize(860, 780)

        self.is_running = False
        self.bot_thread = None
        self.positions = {}
        self.config = BotConfig()
        self.selected_item_key = "boots"

        self.log_queue = queue.Queue()
        self.root.after(100, self._poll_log)

        self.setup_styles()
        self.create_widgets()
        self.load_config()
        self.setup_hotkeys()
        self.setup_position_hotkeys()
        self.update_positions_status()
        self.update_ocr_status()
        self.log("📂 PoE Craft Bot v3.0 готов к работе")

    # ------------------------------------------------------------------
    # Общие элементы
    # ------------------------------------------------------------------

    def setup_styles(self):
        style = ttk.Style()
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Status.TLabel', font=('Arial', 10))
        style.configure('Hotkey.TLabel', font=('Arial', 8, 'bold'), foreground='blue')
        style.configure('Title.TLabel', font=('Arial', 10, 'bold'))
        style.configure('Hint.TLabel', font=('Arial', 8), foreground='gray')

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="12")
        main_frame.pack(fill=tk.BOTH, expand=True)

        header = ttk.Label(main_frame, text="⚙️ PoE Craft Bot v3.0", style='Header.TLabel')
        header.pack(pady=(0, 10))

        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        self.create_item_tab(notebook)
        self.create_methods_tab(notebook)
        self.create_positions_tab(notebook)
        self.create_settings_tab(notebook)
        self.create_hotkeys_tab(notebook)

        # Статус
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        self.status_label = ttk.Label(status_frame, text="⚪ Готов к работе", style='Status.TLabel')
        self.status_label.pack(side=tk.LEFT)

        # Кнопки
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(6, 0))
        self.start_btn = ttk.Button(control_frame, text="▶ Запустить",
                                    command=self.toggle_bot, width=15)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="■ Остановить",
                   command=self.stop_bot, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="💾 Сохранить",
                   command=lambda: (self.save_config(), None), width=15).pack(side=tk.RIGHT, padx=5)

        # Лог
        log_frame = ttk.LabelFrame(main_frame, text="📋 Лог", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
        self.log_text = scrolledtext.ScrolledText(log_frame, height=7, font=('Consolas', 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)

    # ------------------------------------------------------------------
    # Прокручиваемая вкладка
    # ------------------------------------------------------------------

    def make_scrollable(self, parent):
        container = tk.Frame(parent)
        canvas = tk.Canvas(container, highlightthickness=0)
        vsb = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas)
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        win = canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=vsb.set)
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(win, width=e.width))
        canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        def on_wheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind("<MouseWheel>", on_wheel)
        inner.bind("<MouseWheel>", on_wheel)
        return inner

    # ------------------------------------------------------------------
    # ВКЛАДКА 1: ПРЕДМЕТ И МОДЫ
    # ------------------------------------------------------------------

    def create_item_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="📦 Предмет и моды")
        inner = self.make_scrollable(tab)

        # 1. Тип предмета
        f = ttk.LabelFrame(inner, text="1️⃣ Тип предмета", padding="10")
        f.pack(fill=tk.X, pady=6, padx=10)
        self.item_type_var = tk.StringVar()
        self.item_type_combo = ttk.Combobox(
            f, textvariable=self.item_type_var,
            values=[name for _, name in ITEM_LIST], state="readonly", width=38)
        self.item_type_combo.pack(fill=tk.X, pady=4)
        self.item_type_combo.bind('<<ComboboxSelected>>', self.on_item_selected)

        self.item_info_text = tk.Text(f, height=3, font=('Consolas', 9), bg='#f5f5f5')
        self.item_info_text.pack(fill=tk.X)

        # 2. Целевые моды (таблица с весами)
        f = ttk.LabelFrame(inner, text="2️⃣ Целевые моды (как в Path of Craft: мод / значение / вес)",
                           padding="10")
        f.pack(fill=tk.X, pady=6, padx=10)

        cols = ("min", "weight")
        self.targets_tree = ttk.Treeview(f, columns=cols, height=6)
        self.targets_tree.heading('#0', text='Мод (подстрока)')
        self.targets_tree.heading('min', text='Мин. значение (0 = не важно)')
        self.targets_tree.heading('weight', text='Вес')
        self.targets_tree.column('#0', width=280)
        self.targets_tree.column('min', width=170, anchor='center')
        self.targets_tree.column('weight', width=90, anchor='center')
        self.targets_tree.pack(fill=tk.X, pady=(4, 6))

        row = ttk.Frame(f)
        row.pack(fill=tk.X)
        ttk.Label(row, text="Мод:").pack(side=tk.LEFT)
        self.t_name = ttk.Entry(row, width=30)
        self.t_name.pack(side=tk.LEFT, padx=(4, 10))
        ttk.Label(row, text="Мин.:").pack(side=tk.LEFT)
        self.t_min = ttk.Entry(row, width=7)
        self.t_min.pack(side=tk.LEFT, padx=(4, 10))
        ttk.Label(row, text="Вес:").pack(side=tk.LEFT)
        self.t_weight = ttk.Entry(row, width=5)
        self.t_weight.insert(0, "1")
        self.t_weight.pack(side=tk.LEFT, padx=(4, 10))
        self.t_name.bind('<Return>', lambda e: self.add_target())
        ttk.Button(row, text="➕ Добавить", command=self.add_target).pack(side=tk.LEFT, padx=2)
        ttk.Button(row, text="➖ Удалить", command=self.delete_target).pack(side=tk.LEFT, padx=2)
        ttk.Button(row, text="🗑️ Очистить", command=self.clear_targets).pack(side=tk.LEFT, padx=2)

        ttk.Label(f, style='Hint.TLabel',
                  text="Мин. значение: 0 — просто наличие мода; >0 — мод считается найденным при значении >= мин.").pack(anchor=tk.W, pady=(4, 0))

        # 3. Быстрое добавление из базы
        f = ttk.LabelFrame(inner, text="🔍 Быстрое добавление из базы модов", padding="10")
        f.pack(fill=tk.X, pady=6, padx=10)
        srow = ttk.Frame(f)
        srow.pack(fill=tk.X)
        ttk.Label(srow, text="Поиск:").pack(side=tk.LEFT, padx=(0, 5))
        self.mod_search_entry = ttk.Entry(srow, width=28)
        self.mod_search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.mod_search_entry.bind('<KeyRelease>', lambda e: self.filter_available_mods())
        self.mod_search_entry.bind('<Return>', lambda e: self.add_target_from_picker())

        brow = ttk.Frame(f)
        brow.pack(fill=tk.X, pady=(4, 0))
        self.available_mods_listbox = tk.Listbox(brow, height=4, font=('Arial', 9))
        self.available_mods_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb = ttk.Scrollbar(brow, command=self.available_mods_listbox.yview)
        sb.pack(side=tk.LEFT, fill=tk.Y)
        self.available_mods_listbox.configure(yscrollcommand=sb.set)
        ttk.Button(brow, text="➕ Добавить выбранный", command=self.add_target_from_picker).pack(
            side=tk.LEFT, padx=(8, 0))

        # 4. Суммарный вес
        f = ttk.LabelFrame(inner, text="⚖️ Суммарный вес", padding="10")
        f.pack(fill=tk.X, pady=6, padx=10)
        wrow = ttk.Frame(f)
        wrow.pack(fill=tk.X)
        ttk.Label(wrow, text="Крафт останавливается, когда сумма весов найденных модов ≥").pack(
            side=tk.LEFT, padx=(0, 8))
        self.total_weight_var = tk.IntVar(value=0)
        ttk.Spinbox(wrow, from_=0, to=100, textvariable=self.total_weight_var, width=5).pack(side=tk.LEFT)
        ttk.Label(f, style='Hint.TLabel',
                  text="0 = классический режим: останавливаемся, когда найдены ВСЕ целевые моды").pack(anchor=tk.W, pady=(4, 0))

        # 5. Исключения (для Vaal Orb)
        f = ttk.LabelFrame(inner, text="🚫 Исключённые моды (Vaal Orb снимает их)", padding="10")
        f.pack(fill=tk.X, pady=6, padx=10)
        erow = ttk.Frame(f)
        erow.pack(fill=tk.X)
        self.excluded_entry = ttk.Entry(erow, width=30)
        self.excluded_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.excluded_entry.bind('<Return>', lambda e: self.add_excluded())
        ttk.Button(erow, text="➕ Добавить", command=self.add_excluded).pack(side=tk.LEFT, padx=2)
        ttk.Button(erow, text="➖ Удалить", command=self.delete_excluded).pack(side=tk.LEFT, padx=2)
        self.excluded_listbox = tk.Listbox(f, height=3, font=('Arial', 9))
        self.excluded_listbox.pack(fill=tk.X, pady=(5, 0))

        # 6. Действия
        f = ttk.Frame(inner)
        f.pack(fill=tk.X, pady=10, padx=10)
        ttk.Button(f, text="📥 Загрузить настройки предмета",
                   command=self.load_item_defaults).pack(side=tk.LEFT, padx=5)
        ttk.Button(f, text="🔄 Сбросить моды",
                   command=self.reset_mods).pack(side=tk.LEFT, padx=5)

        if ITEM_LIST:
            self.item_type_combo.set(ITEM_LIST[0][1])
            self.on_item_selected(None)
        self.load_available_mods()

    # ------------------------------------------------------------------
    # Методы вкладки "Предмет и моды"
    # ------------------------------------------------------------------

    def load_available_mods(self):
        self.available_mods_listbox.delete(0, tk.END)
        filter_text = self.mod_search_entry.get().strip().lower()
        for mod in sorted(AVAILABLE_MODS):
            if not filter_text or filter_text in mod.lower():
                self.available_mods_listbox.insert(tk.END, mod)

    def filter_available_mods(self, _=None):
        self.load_available_mods()

    def _target_names(self):
        return [self.targets_tree.item(i, "values")[0]
                for i in self.targets_tree.get_children()]

    def add_target(self):
        name = self.t_name.get().strip()
        if not name:
            self.log("⚠️ Введите название мода")
            return
        try:
            min_v = int(self.t_min.get().strip() or 0)
            weight = int(self.t_weight.get().strip() or 1)
        except ValueError:
            self.log("❌ Мин. значение и вес должны быть числами")
            return
        if name in self._target_names():
            self.log(f"⚠️ Мод '{name}' уже есть в списке")
            return
        self.targets_tree.insert('', 'end', values=(name, min_v, weight))
        self.t_name.delete(0, tk.END)
        self.log(f"➕ Целевой мод: {name} (мин {min_v}, вес {weight})")
        self.save_config()

    def add_target_from_picker(self, _=None):
        sel = self.available_mods_listbox.curselection()
        if not sel:
            self.log("⚠️ Выберите мод из списка")
            return
        mod = self.available_mods_listbox.get(sel[0])
        if mod in self._target_names():
            self.log(f"⚠️ Мод '{mod}' уже есть в списке")
            return
        self.targets_tree.insert('', 'end', values=(mod, 0, 1))
        self.log(f"➕ Целевой мод из базы: {mod}")
        self.save_config()

    def delete_target(self):
        sel = self.targets_tree.selection()
        for iid in sel:
            name = self.targets_tree.item(iid, "values")[0]
            self.targets_tree.delete(iid)
            self.log(f"➖ Удалён мод: {name}")
        if sel:
            self.save_config()

    def clear_targets(self):
        self.targets_tree.delete(*self.targets_tree.get_children())
        self.log("🗑️ Целевые моды очищены")
        self.save_config()

    def add_excluded(self, _=None):
        m = self.excluded_entry.get().strip()
        if not m:
            return
        cur = list(self.excluded_listbox.get(0, tk.END))
        if m not in cur:
            self.excluded_listbox.insert(tk.END, m)
            self.excluded_entry.delete(0, tk.END)
            self.save_config()

    def delete_excluded(self):
        sel = self.excluded_listbox.curselection()
        for i in reversed(sel):
            self.excluded_listbox.delete(i)
        if sel:
            self.save_config()

    def on_item_selected(self, _=None):
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
        text = (f"📋 {info.get('icon', '')} {info.get('name', 'Неизвестно')}\n"
                f"   Implicit модов: {info.get('implicit_count', 0)}  |  "
                f"Implicit: {', '.join(info.get('implicit_mods') or []) or 'нет'}")
        self.item_info_text.delete(1.0, tk.END)
        self.item_info_text.insert(1.0, text)

    def load_item_defaults(self):
        """Ставит implicit-счётчик предмета и докачивает его дефолтные моды."""
        info = get_item_info(self.selected_item_key)
        self.implicit_var.set(info.get("implicit_count", 0))
        names = self._target_names()
        added = 0
        for mod in get_default_value_mods(self.selected_item_key):
            if mod["name"] not in names:
                self.targets_tree.insert('', 'end',
                                         values=(mod["name"], mod["min_value"], 1))
                added += 1
        self.log(f"📥 Настройки '{info.get('name')}': implicit={info.get('implicit_count', 0)}, "
                 f"добавлено модов: {added}")
        self.save_config()

    def reset_mods(self):
        self.targets_tree.delete(*self.targets_tree.get_children())
        self.excluded_listbox.delete(0, tk.END)
        self.total_weight_var.set(0)
        self.log("🔄 Целевые моды и исключения сброшены")
        self.save_config()

    # ------------------------------------------------------------------
    # ВКЛАДКА 2: МЕТОДЫ КРАФТА
    # ------------------------------------------------------------------

    def create_methods_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="⚒️ Методы крафта")
        inner = self.make_scrollable(tab)

        hint = ttk.Label(inner, style='Hint.TLabel',
                         text="Отметьте, какие валюты бот имеет право использовать. "
                              "Бот сам решает, когда что применять (см. лог).")
        hint.pack(anchor=tk.W, pady=(6, 2), padx=12)

        self.method_vars = {}
        self.method_param_widgets = {}

        for key, title, desc, params in METHODS_SPEC:
            card = tk.Frame(inner, relief="solid", borderwidth=1, bg="white")
            card.pack(fill=tk.X, pady=4, padx=10)
            innerwin = tk.Frame(card)
            innerwin.pack(fill=tk.X, padx=8, pady=6)

            var = tk.BooleanVar(value=METHOD_DEFAULTS.get(key, False))
            cb = ttk.Checkbutton(innerwin, text=title, variable=var,
                                 command=lambda k=key: self.on_method_toggle(k))
            cb.pack(anchor=tk.W)
            ttk.Label(innerwin, text=desc, style='Hint.TLabel').pack(anchor=tk.W, padx=(24, 0))
            self.method_vars[key] = var

            if params:
                pframe = tk.Frame(innerwin)
                pframe.pack(fill=tk.X, padx=(24, 0), pady=(4, 0))
                for pkey, plabel, ptype in params:
                    prow = ttk.Frame(pframe)
                    prow.pack(fill=tk.X, pady=2)
                    ttk.Label(prow, text=plabel, style='Hint.TLabel').pack(side=tk.LEFT, padx=(0, 8))
                    if ptype == "entry":
                        if pkey == "chance_pattern":
                            pv = tk.StringVar(value="")
                            w = ttk.Entry(prow, textvariable=pv, width=10)
                        else:
                            pv = tk.StringVar()
                            w = ttk.Entry(prow, textvariable=pv, width=10)
                        w.pack(side=tk.LEFT)
                    else:  # int
                        defaults = {
                            "chance_max_rolls": (1, 50, 10),
                            "deck_chance": (0, 100, 25),
                            "essence_quality": (0, 100, 30),
                            "max_essence_uses": (1, 20, 5),
                        }
                        frm, to, dft = defaults.get(pkey, (0, 100, 1))
                        pv = tk.IntVar(value=dft)
                        w = ttk.Spinbox(prow, from_=frm, to=to, textvariable=pv, width=6)
                        w.pack(side=tk.LEFT)
                    self.method_param_widgets[pkey] = (ptype, pv, w)

        # включаем/выключаем параметры по умолчанию
        for key, _, _, params in METHODS_SPEC:
            state = "normal" if self.method_vars[key].get() else "disabled"
            for pkey, _, _ in params:
                self.method_param_widgets[pkey][2].configure(state=state)

    def on_method_toggle(self, _key=None):
        """Включает/выключает строки параметров по чекбоксам их методов."""
        for key, _, _, params in METHODS_SPEC:
            state = "normal" if self.method_vars[key].get() else "disabled"
            for pkey, _, _ in params:
                self.method_param_widgets[pkey][2].configure(state=state)
        self.update_positions_status()
        self.save_config()

    # ------------------------------------------------------------------
    # ВКЛАДКА 3: ПОЗИЦИИ
    # ------------------------------------------------------------------

    def create_positions_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="📌 Позиции")
        inner = self.make_scrollable(tab)

        info = ttk.Label(inner, style='Hint.TLabel',
                         text="Наведите курсор на элемент в игре и нажмите Ctrl+1…Ctrl+0 (или кнопку «Задать»). "
                              "Заданы нужны только для включённых методов.")
        info.pack(anchor=tk.W, pady=(8, 4), padx=12)

        self.pos_labels = {}
        for key, name, hotkey in POSITIONS:
            row = ttk.Frame(inner)
            row.pack(fill=tk.X, pady=3, padx=16)
            ttk.Label(row, text=name, width=32, anchor="w").pack(side=tk.LEFT)
            pos_label = ttk.Label(row, text="не задано", foreground="gray")
            pos_label.pack(side=tk.LEFT, expand=True)
            self.pos_labels[key] = pos_label
            ttk.Button(row, text="Задать",
                       command=lambda k=key: self.capture_position(k)).pack(side=tk.RIGHT, padx=2)
            ttk.Label(row, text=hotkey, style='Hotkey.TLabel').pack(side=tk.RIGHT, padx=2)

        ttk.Button(inner, text="🗑️ Очистить все позиции",
                   command=self.clear_positions).pack(pady=14)

        stat = ttk.LabelFrame(inner, text="📊 Статус", padding="10")
        stat.pack(fill=tk.X, padx=16, pady=(0, 10))
        self.pos_status_label = ttk.Label(stat, text="Позиции не заданы", foreground="gray")
        self.pos_status_label.pack()

    def required_positions(self):
        keys = {"item"}
        for method_key, pos_key in METHOD_TO_POSITION.items():
            if self.method_vars.get(method_key) and self.method_vars[method_key].get():
                keys.add(pos_key)
        return keys

    def setup_position_hotkeys(self):
        try:
            import keyboard
            key_map = {
                "1": "item", "2": "alteration", "3": "augmentation",
                "4": "chaos", "5": "alchemy", "6": "vaal", "7": "chance",
                "8": "essence", "9": "stacked_deck", "0": "eldritch",
            }
            for digit in key_map:
                try:
                    keyboard.remove_hotkey(f"ctrl+{digit}")
                except Exception:
                    pass
            for digit, pos_key in key_map.items():
                keyboard.add_hotkey(
                    f"ctrl+{digit}",
                    lambda k=pos_key: self.capture_position_hotkey(k))
            self.log("⌨️ Хоткеи позиций: Ctrl+1…Ctrl+9, Ctrl+0")
        except Exception as e:
            self.log(f"⚠️ Ошибка хоткеев позиций: {e}")

    def capture_position_hotkey(self, pos_name):
        try:
            import pyautogui
            x, y = pyautogui.position()
        except Exception:
            return
        # callback comes from the keyboard thread -> UI only via root.after
        self.root.after(0, lambda: self._set_position(pos_name, x, y))

    def capture_position(self, pos_name):
        try:
            import pyautogui
            x, y = pyautogui.position()
        except Exception as e:
            self.log(f"❌ Ошибка: {e}")
            return
        self._set_position(pos_name, x, y)

    def _set_position(self, pos_name, x, y):
        self.positions[pos_name] = [x, y]
        label = self.pos_labels.get(pos_name)
        if label:
            label.config(text=f"({x}, {y})", foreground="green")
        try:
            import winsound
            winsound.Beep(1000, 120)
        except Exception:
            pass
        names = dict((k, n) for k, n, _ in POSITIONS)
        self.log(f"🎯 {names.get(pos_name, pos_name)}: ({x}, {y})")
        self.save_config()
        self.update_positions_status()

    def clear_positions(self):
        self.positions = {}
        for label in self.pos_labels.values():
            label.config(text="не задано", foreground="gray")
        self.log("🗑️ Все позиции очищены")
        self.save_config()
        self.update_positions_status()

    def update_positions_status(self):
        required = self.required_positions()
        missing = [k for k in required if k not in self.positions]
        if not missing:
            self.pos_status_label.config(
                text=f"✅ Все нужные позиции заданы ({len(required)})",
                foreground="green")
        else:
            names = dict((k, n) for k, n, _ in POSITIONS)
            self.pos_status_label.config(
                text="⚠️ Не хватает: " + ", ".join(names.get(k, k) for k in missing),
                foreground="orange")

    # ------------------------------------------------------------------
    # ВКЛАДКА 4: НАСТРОЙКИ
    # ------------------------------------------------------------------

    def create_settings_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="⚙️ Настройки")

        f = ttk.LabelFrame(tab, text="Параметры крафта", padding="15")
        f.pack(fill=tk.X, pady=10, padx=10)

        row = ttk.Frame(f)
        row.pack(fill=tk.X, pady=5)
        ttk.Label(row, text="Implicit модов предмета:").pack(side=tk.LEFT, padx=(0, 10))
        self.implicit_var = tk.IntVar(value=1)
        ttk.Spinbox(row, from_=0, to=5, textvariable=self.implicit_var, width=5).pack(side=tk.LEFT)
        ttk.Label(row, style='Hint.TLabel',
                  text="(уменьшается при подсчёте модов — загрузится автоматически при выборе предмета)").pack(
            side=tk.LEFT, padx=(8, 0))

        row = ttk.Frame(f)
        row.pack(fill=tk.X, pady=5)
        ttk.Label(row, text="Задержка клика (сек):").pack(side=tk.LEFT, padx=(0, 10))
        self.click_delay_var = tk.StringVar(value="0.12")
        ttk.Entry(row, textvariable=self.click_delay_var, width=7).pack(side=tk.LEFT)

        row = ttk.Frame(f)
        row.pack(fill=tk.X, pady=5)
        ttk.Label(row, text="Задержка сервера (сек):").pack(side=tk.LEFT, padx=(0, 10))
        self.server_delay_var = tk.StringVar(value="0.25")
        ttk.Entry(row, textvariable=self.server_delay_var, width=7).pack(side=tk.LEFT)
        ttk.Label(row, style='Hint.TLabel',
                  text="+/-15% рандомизации (human-like)").pack(side=tk.LEFT, padx=(8, 0))

        row = ttk.Frame(f)
        row.pack(fill=tk.X, pady=5)
        ttk.Label(row, text="Макс. попыток:").pack(side=tk.LEFT, padx=(0, 10))
        self.max_attempts_var = tk.IntVar(value=2000)
        ttk.Spinbox(row, from_=10, to=100000, textvariable=self.max_attempts_var,
                    width=8).pack(side=tk.LEFT)

        row = ttk.Frame(f)
        row.pack(fill=tk.X, pady=5)
        ttk.Label(row, text="Лимит валюты (пауза):").pack(side=tk.LEFT, padx=(0, 10))
        self.max_uses_var = tk.IntVar(value=0)
        ttk.Spinbox(row, from_=0, to=100000, textvariable=self.max_uses_var,
                    width=8).pack(side=tk.LEFT)
        ttk.Label(row, style='Hint.TLabel',
                  text="0 = без лимита. Достигнув лимита, бот делает ПАУЗУ (перезапуск — счётчик с нуля)").pack(
            side=tk.LEFT, padx=(8, 0))

        row = ttk.Frame(f)
        row.pack(fill=tk.X, pady=5)
        self.use_ocr_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(row, text="Использовать OCR (без Ctrl+C)",
                        variable=self.use_ocr_var,
                        command=self.toggle_ocr).pack(side=tk.LEFT)
        self.ocr_status_label = ttk.Label(f, text="", font=('Arial', 9))
        self.ocr_status_label.pack(anchor=tk.W, pady=(6, 0))

    def toggle_ocr(self):
        import config
        config.USE_OCR = self.use_ocr_var.get()
        self.update_ocr_status()
        self.log(f"OCR {'включен' if config.USE_OCR else 'выключен'}")
        self.save_config()

    def update_ocr_status(self):
        try:
            from ocr_reader import TESSERACT_PATH
            if TESSERACT_PATH:
                status = "✅ OCR доступен" if self.use_ocr_var.get() else "⏹️ OCR отключен"
                self.ocr_status_label.config(
                    text=f"{status} (Tesseract: {TESSERACT_PATH})", foreground="green")
            else:
                self.ocr_status_label.config(
                    text="❌ OCR не доступен (установите Tesseract)", foreground="red")
        except Exception:
            self.ocr_status_label.config(text="❌ OCR не доступен", foreground="red")

    # ------------------------------------------------------------------
    # ВКЛАДКА 5: ХОТКЕИ
    # ------------------------------------------------------------------

    def create_hotkeys_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="⌨️ Хоткеи")

        info = ttk.Label(tab, text="Глобальные горячие клавиши (работают, когда PoE в фокусе)",
                         font=('Arial', 10))
        info.pack(pady=12)

        f1 = ttk.Frame(tab)
        f1.pack(fill=tk.X, pady=10, padx=40)
        ttk.Label(f1, text="Старт/Пауза:").pack(side=tk.LEFT, padx=(0, 10))
        self.toggle_hotkey_var = tk.StringVar(value="F8")
        ttk.Entry(f1, textvariable=self.toggle_hotkey_var, width=10).pack(side=tk.LEFT)

        f2 = ttk.Frame(tab)
        f2.pack(fill=tk.X, pady=10, padx=40)
        ttk.Label(f2, text="Аварийный выход:").pack(side=tk.LEFT, padx=(0, 10))
        self.quit_hotkey_var = tk.StringVar(value="F9")
        ttk.Entry(f2, textvariable=self.quit_hotkey_var, width=10).pack(side=tk.LEFT)

        f3 = ttk.LabelFrame(tab, text="Позиции (захват)", padding="10")
        f3.pack(fill=tk.X, padx=40, pady=12)
        keys_text = ("Ctrl+1 — предмет    Ctrl+2 — Alteration    Ctrl+3 — Augmentation\n"
                     "Ctrl+4 — Chaos      Ctrl+5 — Alchemy       Ctrl+6 — Vaal\n"
                     "Ctrl+7 — Chance     Ctrl+8 — Essence       Ctrl+9 — Stacked Deck\n"
                     "Ctrl+0 — Eldritch")
        ttk.Label(f3, text=keys_text, font=('Consolas', 9)).pack(anchor=tk.W)

        ttk.Label(tab, text="⚠️ Если хоткеи не срабатывают — проверьте, нет ли "
                            "конфликта с другими программами (AMD Adrenalin и т.п.)",
                  style='Hint.TLabel', wraplength=500, justify=tk.LEFT).pack(pady=10)

    def setup_hotkeys(self):
        try:
            import keyboard
            keyboard.unhook_all()
            toggle_key = self.toggle_hotkey_var.get().lower()
            quit_key = self.quit_hotkey_var.get().lower()
            # callback comes from the keyboard thread -> UI only via root.after
            keyboard.add_hotkey(toggle_key,
                                lambda: self.root.after(0, self.toggle_bot))
            keyboard.add_hotkey(quit_key,
                                lambda: self.root.after(0, self.emergency_stop))
            self.log(f"⌨️ Хоткеи: {toggle_key} — старт/пауза, {quit_key} — аварийный выход")
        except Exception as e:
            self.log(f"⚠️ Ошибка хоткеев: {e}")

    def emergency_stop(self):
        self.stop_bot()
        self.log("🛑 Аварийная остановка!")
        self.root.after(100, self.root.destroy)

    # ------------------------------------------------------------------
    # Сборка recipe / запуск
    # ------------------------------------------------------------------

    def _safe_int(self, var, default):
        try:
            return int(var.get())
        except Exception:
            return default

    def _safe_float(self, var, default):
        try:
            return float(var.get())
        except Exception:
            return default

    def build_recipe(self):
        targets = []
        for iid in self.targets_tree.get_children():
            v = self.targets_tree.item(iid, "values")
            targets.append({
                "name": v[0],
                "min_value": int(v[1] or 0),
                "weight": int(v[2] or 1),
            })

        methods = {key: bool(self.method_vars[key].get())
                   for key, _, _, _ in METHODS_SPEC}
        pv = lambda k: self.method_param_widgets[k][1]  # noqa: E731
        methods["chance_pattern"] = pv("chance_pattern").get().strip()
        methods["chance_max_rolls"] = self._safe_int(pv("chance_max_rolls"), 10)
        methods["deck_chance"] = self._safe_int(pv("deck_chance"), 25)
        methods["essence_quality"] = self._safe_int(pv("essence_quality"), 30)
        methods["max_essence_uses"] = self._safe_int(pv("max_essence_uses"), 5)

        return {
            "targets": targets,
            "total_weight": self._safe_int(self.total_weight_var, 0),
            "excluded_mods": list(self.excluded_listbox.get(0, tk.END)),
            "methods": methods,
            "implicit_count": self._safe_int(self.implicit_var, 1),
            "click_delay": self._safe_float(self.click_delay_var, 0.12),
            "server_delay": self._safe_float(self.server_delay_var, 0.25),
            "max_attempts": self._safe_int(self.max_attempts_var, 2000),
            "max_currency_uses": self._safe_int(self.max_uses_var, 0),
        }

    def toggle_bot(self):
        if self.is_running:
            self.stop_bot()
        else:
            self.start_bot()

    def start_bot(self):
        if self.is_running:
            return

        recipe = self.build_recipe()

        if not recipe["targets"]:
            messagebox.showwarning("Ошибка", "Не заданы целевые моды! (вкладка «Предмет и моды»)")
            return
        magic_methods = ("augmentation", "alteration", "chaos", "stacked_deck")
        if not any(recipe["methods"].get(k) for k in magic_methods) \
                and not recipe["methods"].get("eldritch"):
            messagebox.showwarning(
                "Ошибка",
                "Включите хотя бы один метод: Augmentation, Alteration, Chaos, "
                "Stacked Deck (или Eldritch для готового рейра)")
            return

        required = self.required_positions()
        names = dict((k, n) for k, n, _ in POSITIONS)
        missing = [names.get(k, k) for k in required if k not in self.positions]
        if missing:
            messagebox.showwarning("Ошибка", "Не заданы позиции: " + ", ".join(missing))
            return

        self.save_config()

        self.is_running = True
        self.start_btn.config(text="⏸ Пауза")
        self.status_label.config(text="🟢 Бот запущен", foreground="green")
        self.log("🚀 Запуск бота...")

        self.bot_thread = threading.Thread(target=self.run_bot, daemon=True)
        self.bot_thread.start()

    def stop_bot(self):
        if not self.is_running:
            return
        self.is_running = False
        self.start_btn.config(text="▶ Запустить")
        self.status_label.config(text="🔴 Остановка...", foreground="red")
        self.log("⏹ Остановка по запросу...")

    def run_bot(self):
        try:
            import config as bot_config
            from crafting_bot import run

            recipe = self.build_recipe()
            bot_config.USE_OCR = self.use_ocr_var.get()
            positions = self.positions.copy()

            def should_stop():
                return not self.is_running

            status, message = run(positions, recipe, should_stop, log=self.log)
            self.root.after(0, lambda: self._finish_run(status, message))
        except Exception as e:
            import traceback
            self.log(f"❌ Ошибка в боте: {e}")
            self.log(traceback.format_exc())
            self.root.after(0, lambda: self._finish_run("error", str(e)))

    def _finish_run(self, status, message):
        self.is_running = False
        self.start_btn.config(text="▶ Запустить")
        if status in ("success", "success_rare"):
            self.status_label.config(text=f"✅ {message}", foreground="green")
            self.log(f"✅ Готово: {message}")
        elif status == "limit":
            self.status_label.config(text=f"⏸️ Пауза: {message}", foreground="orange")
            self.log(f"⏸️ Пауза: {message}. Перезапустите, чтобы продолжить.")
        elif status == "stopped":
            self.status_label.config(text="⚪ Остановлено", foreground="gray")
        else:
            self.status_label.config(text=f"❌ {message}", foreground="red")
            self.log(f"❌ {message}")

    # ------------------------------------------------------------------
    # Лог (thread-safe)
    # ------------------------------------------------------------------

    def log(self, message):
        self.log_queue.put(str(message))

    def _poll_log(self):
        try:
            while True:
                msg = self.log_queue.get_nowait()
                ts = time.strftime("%H:%M:%S")
                self.log_text.insert(tk.END, f"[{ts}] {msg}\n")
                self.log_text.see(tk.END)
        except queue.Empty:
            pass
        self.root.after(100, self._poll_log)

    # ------------------------------------------------------------------
    # Сохранение / загрузка (v2)
    # ------------------------------------------------------------------

    def load_config(self):
        try:
            cfg = self.config.config  # уже v2 (миграция внутри BotConfig)

            for t in cfg.get("targets", []):
                self.targets_tree.insert('', 'end',
                                         values=(t.get("name", ""),
                                                 int(t.get("min_value") or 0),
                                                 int(t.get("weight") or 1)))
            self.total_weight_var.set(int(cfg.get("total_weight", 0) or 0))
            for x in cfg.get("excluded_mods", []):
                self.excluded_listbox.insert(tk.END, x)

            m = cfg.get("methods", {}) or {}
            for key in self.method_vars:
                self.method_vars[key].set(bool(m.get(key, METHOD_DEFAULTS.get(key, False))))
            pv = lambda k: self.method_param_widgets[k][1]  # noqa: E731
            pv("chance_pattern").set(m.get("chance_pattern", "") or "")
            pv("chance_max_rolls").set(int(m.get("chance_max_rolls", 10) or 10))
            pv("deck_chance").set(int(m.get("deck_chance", 25) or 25))
            pv("essence_quality").set(int(m.get("essence_quality", 30) or 30))
            pv("max_essence_uses").set(int(m.get("max_essence_uses", 5) or 5))
            for key, _, _, params in METHODS_SPEC:
                state = "normal" if self.method_vars[key].get() else "disabled"
                for pkey, _, _ in params:
                    self.method_param_widgets[pkey][2].configure(state=state)

            self.positions = cfg.get("positions", {}) or {}
            for key, coords in self.positions.items():
                label = self.pos_labels.get(key)
                if label and coords:
                    label.config(text=f"({coords[0]}, {coords[1]})", foreground="green")

            s = cfg.get("settings", {}) or {}
            self.implicit_var.set(int(s.get("implicit_mod_count", 1) or 0))
            self.click_delay_var.set(str(s.get("click_delay", 0.12)))
            self.server_delay_var.set(str(s.get("server_response_delay", 0.25)))
            self.max_attempts_var.set(int(s.get("max_attempts", 2000) or 2000))
            self.max_uses_var.set(int(s.get("max_currency_uses", 0) or 0))
            self.use_ocr_var.set(bool(s.get("use_ocr", False)))

            h = cfg.get("hotkeys", {}) or {}
            self.toggle_hotkey_var.set(h.get("toggle", "F8"))
            self.quit_hotkey_var.set(h.get("quit", "F9"))

            selected = cfg.get("selected_item", "boots")
            for key, name in ITEM_LIST:
                if key == selected:
                    self.item_type_combo.set(name)
                    self.selected_item_key = key
                    self.on_item_selected(None)
                    break

            self.update_positions_status()
            self.update_ocr_status()
            self.log("📂 Конфигурация загружена (v2)")
        except Exception as e:
            self.log(f"Ошибка загрузки: {e}")

    def save_config(self):
        try:
            recipe = self.build_recipe()
            data = {
                "version": 2,
                "selected_item": getattr(self, "selected_item_key", "boots"),
                "targets": recipe["targets"],
                "total_weight": recipe["total_weight"],
                "excluded_mods": recipe["excluded_mods"],
                "methods": recipe["methods"],
                "positions": self.positions,
                "settings": {
                    "implicit_mod_count": self._safe_int(self.implicit_var, 1),
                    "click_delay": self._safe_float(self.click_delay_var, 0.12),
                    "server_response_delay": self._safe_float(self.server_delay_var, 0.25),
                    "max_attempts": self._safe_int(self.max_attempts_var, 2000),
                    "max_currency_uses": self._safe_int(self.max_uses_var, 0),
                    "use_ocr": self.use_ocr_var.get(),
                },
                "hotkeys": {
                    "toggle": self.toggle_hotkey_var.get(),
                    "quit": self.quit_hotkey_var.get(),
                },
            }
            self.config.config = data
            self.config.save()
            self.log("💾 Конфигурация сохранена")
        except Exception as e:
            self.log(f"Ошибка сохранения: {e}")
