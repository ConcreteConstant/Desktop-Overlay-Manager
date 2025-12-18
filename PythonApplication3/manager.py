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

    # ======================
    # LIVE CONFIG SETTERS
    # ======================

    # -------- Opacity --------
    def set_opacity(self, value: float):
        self.config["opacity"] = value
        for overlay in self.overlays:
            overlay.setWindowOpacity(value)

    # -------- Is Interactive --------
    def set_interactive(self, is_iteractive: bool):
        self.config["interactive"] = is_iteractive
        for overlay in self.overlays:
            overlay.set_interactive(is_iteractive)

    # -------- Spawn Interval --------
    def set_spawn_interval(self, min_ms: int, max_ms: int):
        if min_ms > max_ms:
            return  # guardrail

        self.config["spawn"]["interval_min_ms"] = min_ms
        self.config["spawn"]["interval_max_ms"] = max_ms
        self._reset_timer()

    # -------- Spawn Chance --------
    def set_spawn_chance(self, chance: float):
        self.config["spawn"]["chance"] = max(0.0, min(1.0, chance))

    # -------- Enable Media --------
    def set_media_enabled(self, media_type: str, enabled: bool):
        self.config["media"][media_type]["enabled"] = enabled

    # -------- Audio Volume --------
    def set_audio_volume(self, value: float):
        value = max(0.0, min(1.0, value))
        self.config["audio_volume"] = value

        for overlay in self.overlays:
            if overlay.media_type == "audio" and overlay.player:
                overlay.player.audioOutput().setVolume(value)

    # -------- Video Volume --------
    def set_video_volume(self, value: float):
        value = max(0.0, min(1.0, value))
        self.config["video_volume"] = value

        for overlay in self.overlays:
            if overlay.media_type == "video" and overlay.player:
                overlay.player.audioOutput().setVolume(value)
    
    # -------- Media Weights --------
    def set_media_weight(self, media_type: str, value: float):
        value = max(0.0, value)
        self.config["media"][media_type]["weight"] = value

    # -------- Media Lifetime --------
    def set_media_lifetime(self, media_type: str, min_ms: int, max_ms: int):
        if min_ms > max_ms:
            return

        config = self.config["media"][media_type]
        config["lifetime_min"] = min_ms
        config["lifetime_max"] = max_ms

    # ======================
    # EXPLICIT ACCESSORS PER CONCEPT
    # ======================

    def spawn_interval_accessors(self):
        def get_min():
            return self.config["spawn"]["interval_min_ms"]

        def get_max():
            return self.config["spawn"]["interval_max_ms"]

        def set_min(v):
            self.set_spawn_interval(v, get_max())

        def set_max(v):
            self.set_spawn_interval(get_min(), v)

        return get_min, get_max, set_min, set_max

    def scale_accessors(self):
        return (
            lambda: self.config["scale"]["min"],
            lambda: self.config["scale"]["max"],
            lambda v: self.set_scale_min(v),
            lambda v: self.set_scale_max(v),
        )

    def media_lifetime_accessors(self, media_type: str):
        def get_min():
            return self.config["media"][media_type]["lifetime_min"]

        def get_max():
            return self.config["media"][media_type]["lifetime_max"]

        def set_min(v):
            self.set_media_lifetime(media_type, v, get_max())

        def set_max(v):
            self.set_media_lifetime(media_type, get_min(), v)

        return get_min, get_max, set_min, set_max