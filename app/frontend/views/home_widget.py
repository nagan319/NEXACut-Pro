from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QPixmap

from ..utils.style import apply_stylesheet

from ...config import LOGO_PATH

class HomeWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        logo_label = QLabel()
        pixmap = QPixmap(LOGO_PATH)
        scaled_pixmap = pixmap.scaledToWidth(1000)
        logo_label.setPixmap(scaled_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        app_description_label = QLabel("Version 0.0.0   Created by nagan__319")
        apply_stylesheet(app_description_label, "small-text.css")

        layout.addStretch()
        layout.addWidget(logo_label)
        layout.addStretch()
        layout.addWidget(app_description_label)

        self.setLayout(layout)
