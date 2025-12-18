# overlays.py
import os
import random

from PySide6.QtWidgets import QWidget, QLabel, QPushButton
from PySide6.QtCore import Qt, QTimer, QUrl, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget


# =========================
# Base overlay
# =========================

class OverlayWidget(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.interactive = True

        self._apply_flags()

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(config["opacity"])

        self._dragging = False
        self._drag_offset = None

    def _apply_flags(self):
        flags = (
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )

        if not self.interactive:
            flags |= Qt.WindowTransparentForInput

        self.setWindowFlags(flags)

    def set_interactive(self, toggled: bool):
        if self.interactive == toggled:
            return

        self.interactive = toggled
        self.hide()
        self._apply_flags()
        self.show()

    # Dragging only works in interactive mode (naturally)
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._dragging = True
            self._drag_offset = e.globalPosition().toPoint() - self.pos()

    def mouseMoveEvent(self, e):
        if self._dragging:
            self.move(e.globalPosition().toPoint() - self._drag_offset)

    def mouseReleaseEvent(self, e):
        self._dragging = False


# =========================
# Media overlay
# =========================

class MediaOverlay(OverlayWidget):
    closed = Signal(object)

    def __init__(self, path, media_type, config):
        super().__init__(config)

        self.path = path
        self.media_type = media_type
        self.player = None
        self.config = config

        self.scale = random.uniform(config["scale"]["min"], config["scale"]["max"])

        self._close_btn = None
        self.setMouseTracking(True)

        # self._init_window()
        self._build()

    def enterEvent(self, event):
        if self._close_btn and self.interactive:
            self._close_btn.show()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self._close_btn:
            self._close_btn.hide()
        super().leaveEvent(event)

    def _add_close_button(self):
        self._close_btn = QPushButton("✕", self)
        self._close_btn.setFixedSize(24, 24)
        self._close_btn.clicked.connect(self._safe_close)
        self._close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(0, 0, 0, 160);
                color: white;
                border: none;
                border-radius: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(200, 50, 50, 200);
            }
        """)
        self._close_btn.hide()

    def _position_close_button(self):
        self._close_btn.move(self.width() - self._close_btn.width() - 4, 4)

    def _start_timer(self):
        cfg = self.config["media"][self.media_type]
        min_ms = cfg["lifetime_min"]
        max_ms = cfg["lifetime_max"]

        lifetime = random.randint(min_ms, max_ms)
        bias = 1 + (self.scale - 1) * self.config["size_lifetime_bias"]
        QTimer.singleShot(max(1500, int(lifetime / bias)), self._safe_close)

    def _safe_close(self):
        if self.player:
            self.player.stop()
        self.closed.emit(self)
        self.deleteLater()

    def _build(self):
        config = self.config

        if self.media_type == "image":
            label = QLabel(self)
            pix = QPixmap(self.path).scaled(
                int(500 * self.scale),
                int(500 * self.scale),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            label.setPixmap(pix)
            self.resize(pix.size())
            # self._start_timer(c["image_lifetime_ms"], c["image_lifetime_ms"])

        else:
            widget = (
                QVideoWidget(self)
                if self.media_type == "video"
                else QLabel(os.path.basename(self.path), self)
            )
            
            widget.resize(int(500 * self.scale), int(300 * self.scale))
            self.resize(widget.size())

            self.player = QMediaPlayer(self)
            audio = QAudioOutput(self)
            audio.setVolume(
                config["video_volume"]
                if self.media_type == "video" else config["audio_volume"]
            )

            self.player.setAudioOutput(audio)
            if self.media_type == "video":
                self.player.setVideoOutput(widget)

            self.player.setSource(QUrl.fromLocalFile(self.path))
            self.player.mediaStatusChanged.connect(
                lambda st: self.player.play() if st == QMediaPlayer.LoadedMedia else None
            )
            self.player.mediaStatusChanged.connect(
                lambda st: self._safe_close() if st == QMediaPlayer.EndOfMedia else None
            )

        self._add_close_button()
        self._position_close_button()
        self._start_timer()
        self.show()

