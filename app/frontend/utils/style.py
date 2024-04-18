import os
from PyQt6.QtWidgets import QWidget

class Style:

    def apply_stylesheet(self, widget: QWidget, stylesheet_file: str):

        if not os.path.exists(stylesheet_file):
            raise FileNotFoundError(f"Stylesheet file {stylesheet_file} does not exist")

        with open(stylesheet_file, 'r') as f:
            stylesheet = f.read()
            widget.setStyleSheet(stylesheet)