import os

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QPixmap

from utils.style import Style

class HomeWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.__layout = QVBoxLayout()

        self.__logo_label = QLabel()
        script_path = os.path.dirname(__file__)
        logo_path = os.path.join(script_path, 'graphics', 'NEXACut Logo.png')
        pixmap = QPixmap(logo_path)
        scaled_pixmap = pixmap.scaled(1000, 500)
        self.__logo_label.setPixmap(scaled_pixmap)
        self.__logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.__app_description_label = QLabel("Version 0.0.0   Created by nagan__319")
        Style.apply_stylesheet(self.__app_description_label, "small-text.css")

        self.__layout.addStretch()
        self.__layout.addWidget(self.__logo_label)
        self.__layout.addStretch()
        self.__layout.addWidget(self.__app_description_label)

        self.setLayout(self.__layout)