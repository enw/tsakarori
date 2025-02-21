#!/usr/bin/env python3
import json
import os
import curses

class Config:
    def __init__(self):
        self.config_file = os.path.expanduser("~/.config/tsakarori/config.json")
        self.config = self.load_config()

    def load_config(self):
        default_config = {
            "color_scheme": "default",
            "color_schemes": {
                "default": {
                    "header": [-1, curses.COLOR_BLUE],
                    "footer": [-1, curses.COLOR_BLUE],
                    "selected": [curses.COLOR_BLACK, curses.COLOR_WHITE],
                    "normal": [-1, -1],
                    "highlight": [curses.COLOR_YELLOW, -1]
                },
                "dark": {
                    "header": [curses.COLOR_WHITE, curses.COLOR_BLUE],
                    "footer": [curses.COLOR_WHITE, curses.COLOR_BLUE],
                    "selected": [curses.COLOR_BLACK, curses.COLOR_WHITE],
                    "normal": [-1, -1],
                    "highlight": [curses.COLOR_YELLOW, -1]
                }
            }
        }

        if not os.path.exists(self.config_file):
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, "w") as f:
                json.dump(default_config, f, indent=4)
            return default_config

        with open(self.config_file, "r") as f:
            return json.load(f)

    def save_config(self):
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=4)

    def get_color_pairs(self):
        return self.config["color_schemes"][self.config["color_scheme"]]
