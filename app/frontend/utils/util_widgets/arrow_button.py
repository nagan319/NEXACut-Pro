from style import Style

from PyQt6.QtWidgets import QPushButton

class ArrowButton(QPushButton):

    def __init__(self, left_right: bool):
        super().__init__()
        if left_right:
            self.setText('>')
        else:
            self.setText('<')
        Style.apply_stylesheet(self, 'small-button.css')