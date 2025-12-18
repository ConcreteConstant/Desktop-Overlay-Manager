# main.py
import sys
from PySide6.QtWidgets import QApplication

from config import load_config
from media import MediaLibrary
from manager import OverlayManager
from gui import ControlPanel


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    config = load_config()
    media = MediaLibrary(config)
    manager = OverlayManager(config, media)
    
    panel = ControlPanel(manager)
    # panel.config_applied.connect(manager.apply_config)
    panel.show()

    sys.exit(app.exec())
