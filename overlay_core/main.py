# main.py
import sys
from PySide6.QtWidgets import QApplication

from config import load_config
from config import save_config

from media import MediaLibrary
from manager import OverlayManager
from gui import ControlPanel
from ipc import IPCServer


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    config = load_config()
    media = MediaLibrary(config)
    manager = OverlayManager(config, media)

    # panel = ControlPanel(manager)
    # panel.show()
    ipc_server = IPCServer(manager)
    ipc_server.start()

    app.aboutToQuit.connect(lambda: save_config(manager.config))
    sys.exit(app.exec())
