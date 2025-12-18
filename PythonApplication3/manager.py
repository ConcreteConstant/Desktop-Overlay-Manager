# manager.py
import random
from PySide6.QtCore import QTimer
from PySide6.QtGui import QGuiApplication
from copy import deepcopy

from overlays import MediaOverlay

class OverlayManager:
    def __init__(self, config, media_library):
        self.config = config
        self.media = media_library

        self.overlays = []
        self.active = {"image":0, "audio": 0, "video": 0}

        self.timer = QTimer()
        self.timer.timeout.connect(self._on_tick)
        self._reset_timer()

    def _reset_timer(self):
        interval = random.randint(
            self.config["spawn"]["interval_min_ms"],
            self.config["spawn"]["interval_max_ms"]
        )
        self.timer.start(interval)

    def _on_tick(self):
        self._reset_timer()

        if random.random() > self.config["spawn"]["chance"]:
            return

        self.spawn()

    def spawn(self):
        allowed = []

        for t, cfg in self.config["media"].items():
            if not cfg["enabled"]:
                continue
            if t in ("audio", "video") and self.active[t] > 0:
                continue
            allowed.append(t)

        path, media_type = self.media.choose(allowed)
        if not path:
            return

        overlay = MediaOverlay(path, media_type, self.config)
        overlay.closed.connect(self._on_closed)

        overlay.set_interactive(self.config["interactive"])
        overlay.setWindowOpacity(self.config["opacity"])

        screen = random.choice(QGuiApplication.screens()).availableGeometry()
        overlay.move(
            random.randint(screen.x(), screen.right() - overlay.width()),
            random.randint(screen.y(), screen.bottom() - overlay.height())
        )

        self.overlays.append(overlay)
        if media_type in self.active:
            self.active[media_type] += 1


    def _on_closed(self, overlay):
        if overlay in self.overlays:
            self.overlays.remove(overlay)

        if overlay.media_type in self.active:
            self.active[overlay.media_type] -= 1

    def apply_structural_config(self, new_config):
        """
        Apply configuration changes that are NOT safe to mutate live.

        Examples:
        - media folders
        - library rebuilds
        - file weights
        - lifetime rules
        """
        # replace contents, keep reference
        self.config.clear()
        self.config.update(deepcopy(new_config))

        # rebuild subsystems
        self.media.rescan()

        # reset timer if needed
        self._reset_timer()

    # -------- Live config setters --------

    def set_opacity(self, value: float):
        self.config["opacity"] = value
        for overlay in self.overlays:
            overlay.setWindowOpacity(value)

    def set_interactive(self, enabled: bool):
        self.config["interactive"] = enabled
        for overlay in self.overlays:
            overlay.set_interactive(enabled)

    def set_spawn_interval(self, min_ms: int, max_ms: int):
        if min_ms > max_ms:
            return  # guardrail

        self.config["spawn"]["interval_min_ms"] = min_ms
        self.config["spawn"]["interval_max_ms"] = max_ms
        self._reset_timer()

    def set_spawn_chance(self, chance: float):
        self.config["spawn"]["chance"] = max(0.0, min(1.0, chance))

    def set_media_enabled(self, media_type: str, enabled: bool):
        self.config["media"][media_type]["enabled"] = enabled