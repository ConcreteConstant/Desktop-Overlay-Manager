# config.py
import json
from pathlib import Path
from copy import deepcopy
import os

def get_config_path():
    if os.name == "nt":
        base = Path(os.getenv("APPDATA", Path.home()))
    else:
        base = Path.home() / ".config"

    config_dir = base / "DesktopOverlayManager"
    config_dir.mkdir(parents=True, exist_ok=True)

    return config_dir / "config.json"

CONFIG_FILE = get_config_path()

DEFAULT_CONFIG = {
    "opacity": 0.5,
    "interactive": True,
    "size_lifetime_bias": 0.6,
    "audio_volume": 0.45,
    "video_volume": 0.30,
    
    "spawn": {
        "interval_min_ms": 3000,
        "interval_max_ms": 7000,
        "chance": 0.8,
        "fullscreen_chance": 1,
    },

    "media": {
        "image": {
            "enabled": True,
            "weight": 0.5,

            "lifetime": {
                "random": {
                    "min": 8000,
                    "max": 8000,
                },
                "fullscreen": {
                    "min": 2000,
                    "max": 2000,
                }
            }
        },

        "audio": {
            "enabled": True,
            "weight": 0.25,

            "lifetime": {
                "random": {
                    "min": 6000,
                    "max": 14000,
                }
            }
        },

        "video": {
            "enabled": True,
            "weight": 0.25,

            "lifetime": {
                "random": {
                    "min": 6000,
                    "max": 18000,
                },
                "fullscreen": {
                    "min": 2000,
                    "max": 2000,
                }
            }
        },
    },

    "scale": {
        "min": 0.4,
        "max": 2.0,
    },

    "media_folders": []

}

def load_config():
    config = deepcopy(DEFAULT_CONFIG)

    if CONFIG_FILE.exists():
        loaded = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        config.update(loaded)

    return config


def save_config(config):
    CONFIG_FILE.write_text(
        json.dumps(config, indent=4), encoding="utf-8"
    )
    print("Saving config to:", CONFIG_FILE.resolve())
