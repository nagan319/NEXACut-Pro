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
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(logging.StreamHandler())
        self.logger.info(f"@{self.__class__.__name__}: Initializing home widget...")
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
        self.logger.info(f"@{self.__class__.__name__}: Initialization complete.")
