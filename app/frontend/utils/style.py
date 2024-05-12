import os
from PyQt6.QtWidgets import QWidget

from ...config import STYLESHEET_FOLDER_PATH

class Style:

    @staticmethod
    def apply_stylesheet(widget: QWidget, stylesheet_file: str):
        stylesheet_path = os.path.join(STYLESHEET_FOLDER_PATH, stylesheet_file)

        if not os.path.exists(stylesheet_path):
            raise FileNotFoundError(f"Stylesheet file {stylesheet_path} does not exist")
        
        with open(stylesheet_path, 'r') as f:
            stylesheet = f.read()
            widget.setStyleSheet(stylesheet)