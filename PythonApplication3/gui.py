from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSlider, QSpinBox,
    QCheckBox, QPushButton
)
from PySide6.QtCore import Qt, Signal
from copy import deepcopy

class ControlPanel(QWidget):
    config_applied = Signal(dict)

    def __init__(self, manager):
        super().__init__()
        self.manager = manager

        self.live_config = manager.config
        self.working_config = deepcopy(manager.config)  # STRUCTURAL config (only used for Apply-only settings)

        self.setWindowTitle("Overlay Control Panel")
        self.setFixedWidth(320)

        layout = QVBoxLayout(self)

        # ======================
        # LIVE SETTINGS
        # ======================

        # -------- Opacity --------
        layout.addWidget(QLabel("Overlay Opacity"))
        self.opacity = QSlider(Qt.Horizontal)
        self.opacity.setRange(10, 100)
        self.opacity.setValue(int(self.live_config["opacity"] * 100))
        self.opacity.valueChanged.connect(lambda v: self.manager.set_opacity(v / 100))
        layout.addWidget(self.opacity)

        # -------- Spawn Controls --------
        layout.addWidget(QLabel("Spawn Interval (ms)"))

        row = QHBoxLayout()
        self.spawn_min = QSpinBox()
        self.spawn_min.setRange(500, 60000)
        self.spawn_min.setValue(self.live_config["spawn"]["interval_min_ms"])

        self.spawn_max = QSpinBox()
        self.spawn_max.setRange(500, 60000)
        self.spawn_max.setValue(self.live_config["spawn"]["interval_max_ms"])

        row.addWidget(QLabel("Min"))
        row.addWidget(self.spawn_min)
        row.addWidget(QLabel("Max"))
        row.addWidget(self.spawn_max)

        self.spawn_min.valueChanged.connect(self._update_spawn_interval)
        self.spawn_max.valueChanged.connect(self._update_spawn_interval)

        layout.addLayout(row)

        # -------- Spawn Chance --------
        layout.addWidget(QLabel("Spawn Chance"))
        self.spawn_chance = QSlider(Qt.Horizontal)
        self.spawn_chance.setRange(0, 100)
        self.spawn_chance.setValue(int(self.live_config["spawn"]["chance"] * 100))

        self.spawn_chance.valueChanged.connect(lambda v: self.manager.set_spawn_chance(v / 100))
        layout.addWidget(self.spawn_chance)

        # -------- Media Toggles --------
        layout.addWidget(QLabel("Allowed Media Types"))

        self.chk_image = QCheckBox("Images")
        self.chk_audio = QCheckBox("Audio")
        self.chk_video = QCheckBox("Video")

        self.chk_image.setChecked(self.live_config["media"]["image"]["enabled"])
        self.chk_audio.setChecked(self.live_config["media"]["audio"]["enabled"])
        self.chk_video.setChecked(self.live_config["media"]["video"]["enabled"])

        self.chk_image.toggled.connect(lambda v: self.manager.set_media_enabled("image", v))
        self.chk_audio.toggled.connect(lambda v: self.manager.set_media_enabled("audio", v))
        self.chk_video.toggled.connect(lambda v: self.manager.set_media_enabled("video", v))

        layout.addWidget(self.chk_image)
        layout.addWidget(self.chk_audio)
        layout.addWidget(self.chk_video)

        # -------- Toggle Interactive --------
        self.chk_interactive = QCheckBox("Interactive Overlays (disable click-through)")
        self.chk_interactive.setChecked(self.live_config["interactive"])

        self.chk_interactive.toggled.connect(self.manager.set_interactive)

        layout.addWidget(self.chk_interactive)

        # ======================
        # STRUCTURAL (APPLY-ONLY)
        # ======================
        # (Nothing here yet)


        # ======================
        # APPLY / CLOSE
        # ======================

        # -------- Apply/Close Buttons --------
        btn_row = QHBoxLayout()
        apply_btn = QPushButton("Apply")
        close_btn = QPushButton("Close")

        btn_row.addWidget(apply_btn)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

        apply_btn.clicked.connect(self._apply_structural)
        close_btn.clicked.connect(self.close)

    def _apply_structural(self):
        """
        Apply ONLY settings that are not safe to change live.
        Currently none are exposed, but this is future-proof.
        """
        self.manager.apply_structural_config(self.working_config)

    def _update_spawn_interval(self):
        self.manager.set_spawn_interval(self.spawn_min.value(), self.spawn_max.value())

