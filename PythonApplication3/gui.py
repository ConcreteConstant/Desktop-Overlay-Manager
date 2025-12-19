from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSlider, QSpinBox, QDoubleSpinBox,
    QCheckBox, QPushButton,
    QListWidget, QFileDialog
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
        # self.setFixedWidth(320)

        layout = QVBoxLayout(self)

        # ======================
        # LIVE SETTINGS - (live_config)
        # ======================

        # -------- Opacity --------
        layout.addWidget(QLabel("Overlay Opacity"))
        self.opacity = QSlider(Qt.Horizontal)
        self.opacity.setRange(10, 100)
        self.opacity.setValue(int(self.live_config["opacity"] * 100))
        self.opacity.valueChanged.connect(lambda v: self.manager.set_opacity(v / 100))
        layout.addWidget(self.opacity)

        # -------- Scale --------
        layout.addWidget(QLabel("Overlay Scale"))

        get_min, get_max, set_min, set_max = self.manager.scale_accessors()

        layout.addLayout(
            self._range_spinboxes(
                "Scale",
                get_min,
                get_max,
                set_min,
                set_max,
                min_value=0.1,
                max_value=5.0,
                step=0.05,
                decimals=2,
            )
        )

        # -------- Spawn Interval Control --------
        get_min, get_max, set_min, set_max = self.manager.spawn_interval_accessors()

        layout.addLayout(
            self._range_spinboxes(
                "Spawn Interval (ms)",
                get_min, get_max, set_min, set_max,
                min_value=500,
                max_value=60000,
                step=100,
            )
        )

        # -------- Spawn Chance --------
        layout.addWidget(QLabel("Spawn Chance"))

        layout.addLayout(self._percent_slider_w_label("Spawn Chance",self.working_config["spawn"]["chance"],self.manager.set_spawn_chance))

        # -------- Lifetime Control --------
        for media in ("image", "audio", "video"):
            get_min, get_max, set_min, set_max = self.manager.media_lifetime_accessors(media)

            layout.addLayout(
                self._range_spinboxes(
                    f"{media.capitalize()} Lifetime (ms)",
                    get_min, get_max, set_min, set_max,
                    min_value=1000,
                    max_value=60000,
                    step=500,
                )
            )

        # -------- Volume Control --------
        layout.addWidget(QLabel("Volume"))

        layout.addLayout(self._percent_slider_w_label("Audio",self.working_config["audio_volume"],self.manager.set_audio_volume))
        layout.addLayout(self._percent_slider_w_label("Video",self.working_config["video_volume"],self.manager.set_video_volume))

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
        self.chk_interactive = QCheckBox("Interactive Overlays (disable click-through) (does not work for videos)")
        self.chk_interactive.setChecked(self.live_config["interactive"])

        self.chk_interactive.toggled.connect(self.manager.set_interactive)

        layout.addWidget(self.chk_interactive)

        # ======================
        # STRUCTURAL (APPLY-ONLY) - (working_config)
        # ======================

        # -------- Media Weights --------
        layout.addWidget(QLabel("Media Weights"))

        layout.addLayout(self._percent_slider_w_label("Image Weight",self.working_config["media"]["image"]["weight"],lambda v: self.manager.set_media_weight("image", v)))
        layout.addLayout(self._percent_slider_w_label("Audio Weight",self.working_config["media"]["audio"]["weight"],lambda v: self.manager.set_media_weight("audio", v)))
        layout.addLayout(self._percent_slider_w_label("Video Weight",self.working_config["media"]["video"]["weight"],lambda v: self.manager.set_media_weight("video", v)))

        # -------- Media Folders --------
        layout.addWidget(QLabel("Media Folders"))

        self.folder_list = QListWidget()
        self.folder_list.addItems(self.working_config["media_folders"])
        layout.addWidget(self.folder_list)

        folder_btn_row = QHBoxLayout()
        add_folder_btn = QPushButton("Add Folder")
        remove_folder_btn = QPushButton("Remove Selected")

        folder_btn_row.addWidget(add_folder_btn)
        folder_btn_row.addWidget(remove_folder_btn)
        layout.addLayout(folder_btn_row)

        add_folder_btn.clicked.connect(self._add_folder)
        remove_folder_btn.clicked.connect(self._remove_folder)

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

        # ======================
        # FEEDBACK
        # ======================
        # -------- Pending Changes Label --------
        self.pending_label = QLabel("Pending Changes - Click Apply")
        self.pending_label.setStyleSheet("color: orange;")
        self.pending_label.hide()
        layout.addWidget(self.pending_label)

    def _apply_structural(self):
        """
        Apply ONLY settings that are not safe to change live.
        Currently none are exposed, but this is future-proof.
        """
        self.manager.apply_structural_config(self.working_config)
        self.pending_label.hide()

    def _mark_dirty(self):
        self.pending_label.show()

    def _add_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Media Folder"
        )
        if not folder:
            return

        if folder in self.working_config["media_folders"]:
            return  # avoid duplicates

        self.working_config["media_folders"].append(folder)
        self.folder_list.addItem(folder)
        self._mark_dirty()

    def _remove_folder(self):
        item = self.folder_list.currentItem()
        if not item:
            return

        folder = item.text()
        self.working_config["media_folders"].remove(folder)
        self.folder_list.takeItem(self.folder_list.row(item))
        self._mark_dirty()

    # ======================
    # REUSABLE UI FUNCTIONS
    # ======================

    def _percent_slider_w_label(self, label_text, initial_value, on_change):
        row = QHBoxLayout()

        label = QLabel(label_text)
        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(int(initial_value * 100))

        spin = QSpinBox()
        spin.setRange(0, 100)
        spin.setSuffix("%")
        spin.setValue(int(initial_value * 100))

        slider.valueChanged.connect(spin.setValue)
        spin.valueChanged.connect(slider.setValue)

        slider.valueChanged.connect(lambda v: on_change(v / 100))

        row.addWidget(label)
        row.addWidget(slider)
        row.addWidget(spin)

        return row

    def _range_spinboxes(self,label: str, get_min, get_max, set_min, set_max, *, min_value=0, max_value=1_000_000, step=1, decimals=0, suffix=""):

        row = QHBoxLayout()
        row.addWidget(QLabel(label))

        min_box = QDoubleSpinBox() if decimals else QSpinBox()
        max_box = QDoubleSpinBox() if decimals else QSpinBox()

        for box in (min_box, max_box):
            box.setRange(min_value, max_value)
            box.setSingleStep(step)
            box.setSuffix(suffix)

            if isinstance(box, QDoubleSpinBox):
                box.setDecimals(decimals)

        min_box.setValue(get_min())
        max_box.setValue(get_max())

        def on_min_changed(v):
            if v > max_box.value():
                v = max_box.value()
            min_box.setValue(v)
            set_min(v)

        def on_max_changed(v):
            if v < min_box.value():
                v = min_box.value()
            max_box.setValue(v)
            set_max(v)

        min_box.valueChanged.connect(on_min_changed)
        max_box.valueChanged.connect(on_max_changed)

        row.addWidget(QLabel("Min"))
        row.addWidget(min_box)
        row.addWidget(QLabel("Max"))
        row.addWidget(max_box)

        return row

    



