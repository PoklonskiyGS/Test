"""
Конфигурация бота (файл bot_config.json), схема v2.

v2: единая таблица целевых модов с весами (targets), методы крафта (methods),
позиции 10 валют, лимит использований валюты.

Старые конфиги v1 (target_mods / target_mods_with_values) автоматически
миграцируются в v2.
"""
import json
import os
import copy

DEFAULT_CONFIG = {
    "version": 2,
    "selected_item": "boots",

    # Целевые моды: name, min_value (0 = не важно), weight
    "targets": [],
    # Суммарный вес: 0 = остановить, когда найдены ВСЕ моды
    "total_weight": 0,
    # "Плохие" моды для Vaal Orb (подстрока)
    "excluded_mods": [],

    # Методы крафта (Path of Craft Basic)
    "methods": {
        "augmentation": True,
        "alteration": True,
        "chaos": False,
        "vaal": False,
        "alchemy_finish": False,
        "eldritch": False,
        "chance": False,
        "chance_pattern": "",
        "chance_max_rolls": 10,
        "stacked_deck": False,
        "deck_chance": 25,
        "essence": False,
        "essence_quality": 30,
        "max_essence_uses": 5,
    },

    # Позиции: item, alteration, augmentation, chaos, alchemy,
    #           vaal, chance, essence, stacked_deck, eldritch
    "positions": {},

    "settings": {
        "implicit_mod_count": 1,
        "click_delay": 0.12,
        "server_response_delay": 0.25,
        "max_attempts": 2000,
        "max_currency_uses": 0,   # 0 = без лимита
        "use_ocr": False,
    },

    "hotkeys": {
        "toggle": "F8",
        "quit": "F9",
    },
}


class BotConfig:
    def __init__(self, config_file="bot_config.json"):
        self.config_file = config_file
        self.config = self.load()

    def default_config(self):
        return copy.deepcopy(DEFAULT_CONFIG)

    def load(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return self.migrate(data)
            except Exception:
                return self.default_config()
        return self.default_config()

    @staticmethod
    def _deep_merge(base, override):
        out = copy.deepcopy(base)
        for k, v in (override or {}).items():
            if isinstance(v, dict) and isinstance(out.get(k), dict):
                out[k] = BotConfig._deep_merge(out[k], v)
            else:
                out[k] = v
        return out

    def migrate(self, data):
        """Миграция любого найденного конфига в схему v2."""
        if not isinstance(data, dict):
            return self.default_config()

        if data.get("version") == 2:
            # добираем отсутствующие ключи
            return self._deep_merge(self.default_config(), data)

        # ---- v1 -> v2 ----
        v2 = self.default_config()
        targets = []
        for m in data.get("target_mods", []) or []:
            if m:
                targets.append({"name": m, "min_value": 0, "weight": 1})
        for m in data.get("target_mods_with_values", []) or []:
            if isinstance(m, dict) and m.get("name"):
                targets.append({
                    "name": m["name"],
                    "min_value": int(m.get("min_value") or 0),
                    "weight": 1,
                })
        v2["targets"] = targets
        # старые ключи позиций -> новые
        positions = dict(data.get("positions", {}) or {})
        for old_key, new_key in (("alteration_orb", "alteration"),
                                 ("augmentation_orb", "augmentation")):
            if old_key in positions:
                if new_key not in positions:
                    positions[new_key] = positions.pop(old_key)
                else:
                    positions.pop(old_key)
        v2["positions"] = positions
        v2["selected_item"] = data.get("selected_item", "boots")
        v2["settings"] = self._deep_merge(v2["settings"], data.get("settings", {}))
        v2["hotkeys"] = self._deep_merge(v2["hotkeys"], data.get("hotkeys", {}))
        return v2

    def save(self):
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save()
