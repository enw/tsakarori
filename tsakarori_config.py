import json
import os
from pathlib import Path
import curses

DEFAULT_CONFIG = {
    "color_scheme": "default",
    "color_schemes": {
        "default": {
            "header": (curses.COLOR_BLACK, curses.COLOR_WHITE),
            "footer": (curses.COLOR_BLACK, curses.COLOR_WHITE),
            "selected": (curses.COLOR_BLACK, curses.COLOR_CYAN),
            "normal": (curses.COLOR_WHITE, curses.COLOR_BLACK),
            "highlight": (curses.COLOR_YELLOW, curses.COLOR_BLACK),
        },
        "night": {
            "header": (curses.COLOR_GREEN, curses.COLOR_BLACK),
            "footer": (curses.COLOR_GREEN, curses.COLOR_BLACK),
            "selected": (curses.COLOR_BLACK, curses.COLOR_GREEN),
            "normal": (curses.COLOR_GREEN, curses.COLOR_BLACK),
            "highlight": (curses.COLOR_YELLOW, curses.COLOR_BLACK),
        },
        "day": {
            "header": (curses.COLOR_BLUE, curses.COLOR_WHITE),
            "footer": (curses.COLOR_BLUE, curses.COLOR_WHITE),
            "selected": (curses.COLOR_WHITE, curses.COLOR_BLUE),
            "normal": (curses.COLOR_BLACK, curses.COLOR_WHITE),
            "highlight": (curses.COLOR_RED, curses.COLOR_WHITE),
        },
        "matrix": {
            "header": (curses.COLOR_GREEN, curses.COLOR_BLACK),
            "footer": (curses.COLOR_GREEN, curses.COLOR_BLACK),
            "selected": (curses.COLOR_BLACK, curses.COLOR_GREEN),
            "normal": (curses.COLOR_GREEN, curses.COLOR_BLACK),
            "highlight": (curses.COLOR_WHITE, curses.COLOR_BLACK),
        }
    }
}

class Config:
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "taskwarrior-tui"
        self.config_file = self.config_dir / "config.json"
        self.config = DEFAULT_CONFIG.copy()
        self.load_config()
        
    def load_config(self):
        if self.config_file.exists():
            with open(self.config_file) as f:
                saved_config = json.load(f)
                self.config.update(saved_config)

    def save_config(self):
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def get_color_pairs(self):
        scheme = self.config["color_schemes"][self.config["color_scheme"]]
        return scheme 