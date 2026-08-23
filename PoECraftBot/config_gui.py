"""
Настройки для GUI
"""
import json
import os

class BotConfig:
    def __init__(self, config_file="bot_config.json"):
        self.config_file = config_file
        self.config = self.load()
    
    def load(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self.default_config()
        return self.default_config()
    
    def save(self):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def default_config(self):
        return {
            "target_mods": [],
            "target_mods_with_values": [],
            "positions": {},
            "selected_item": "boots",
            "settings": {
                "implicit_mod_count": 1,
                "stop_after_mod_count": 2,
                "click_delay": 0.12,
                "server_response_delay": 0.25,
                "max_attempts": 2000,
                "use_ocr": True,
                "async_mode": True
            },
            "hotkeys": {
                "toggle": "f8",
                "quit": "f9"
            }
        }
    
    def get(self, key, default=None):
        return self.config.get(key, default)
    
    def set(self, key, value):
        self.config[key] = value
        self.save()