from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QPixmap

import logging

from ..utils.style import Style

from ...config import LOGO_PATH

class HomeWidget(QWidget):
    """
    Home tab containing app logo and version information.
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        if not self.logger.hasHandlers():
            self.logger.setLevel(logging.DEBUG)
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            
        self.logger.debug(f"Initializing home widget...")
        super().__init__()

        layout = QVBoxLayout()

        logo_label = QLabel()
        pixmap = QPixmap(LOGO_PATH)
        scaled_pixmap = pixmap.scaledToWidth(1000)
        logo_label.setPixmap(scaled_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        app_description_label = QLabel("Version 0.0.0   Created by nagan__319")
        Style.apply_stylesheet(app_description_label, "small-text.css")

        layout.addStretch()
        layout.addWidget(logo_label)
        layout.addStretch()
        layout.addWidget(app_description_label)

        self.setLayout(layout)
        self.logger.debug(f"Initialization complete.")
