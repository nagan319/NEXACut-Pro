from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton

from ..style import apply_stylesheet

class Menu(QWidget):

    button_clicked = pyqtSignal(int)

    def __init__(self, buttons: list):
        super().__init__()

        apply_stylesheet(self, "window.css")
        self.__layout = QVBoxLayout()
        self.__layout.setContentsMargins(0, 0, 0, 0)
        self.__layout.setSpacing(0)

        for i, button_text in enumerate(buttons):
            button = QPushButton(button_text)
            apply_stylesheet(button, "generic-button.css")
            button.clicked.connect(lambda _, index=i: self.button_clicked.emit(index)) # button clicked boolean signal is ignored, sends button index
            self.__layout.addWidget(button, 1)

        self.__bottom_widget = QWidget() # purely for background
        apply_stylesheet(self.__bottom_widget, "light.css")

        self.__layout.addWidget(self.__bottom_widget, 10)
        self.setLayout(self.__layout)