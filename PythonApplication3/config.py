# config.py
import json
from pathlib import Path

CONFIG_FILE = Path("config.json")

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
        "screen_takeover_chance": 0.05,
    },

    "media": {
        "image": {
            "enabled": True,
            "weight": 0.5,
            "lifetime_min": 8000,
            "lifetime_max": 8000,
        },
        "audio": {
            "enabled": True,
            "weight": 0.25,
            "lifetime_min": 6000,
            "lifetime_max": 14000,
        },
        "video": {
            "enabled": True,
            "weight": 0.25,
            "lifetime_min": 6000,
            "lifetime_max": 18000,
        },
    },

    "scale": {
        "min": 0.4,
        "max": 2.0,
    },

    "media_folders": [
        r"D:/zzz/2",
        r"D:/zzz/3",
    ]

}


def load_config():
    config = DEFAULT_CONFIG.copy()

    if CONFIG_FILE.exists():
        config.update(json.loads(CONFIG_FILE.read_text()))

    return config


def save_config(config):
    CONFIG_FILE.write_text(
        json.dumps(config, indent=4)
    )
