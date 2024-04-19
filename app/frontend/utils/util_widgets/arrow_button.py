from PyQt6.QtWidgets import QPushButton

from ..style import apply_stylesheet

class ArrowButton(QPushButton):

    def __init__(self, left_right: bool):
        super().__init__()
        if left_right:
            self.setText('>')
        else:
            self.setText('<')
        apply_stylesheet(self, 'small-button.css')