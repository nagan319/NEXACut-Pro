import os
from PyQt6.QtWidgets import QWidget

from ...config import STYLESHEET_FOLDER_PATH

class Style:

    """
    Functional class for applying styling to widgets.
    """

    @staticmethod
    def apply_stylesheet(widget: QWidget, stylesheet_file: str):
        """
        Applies stylesheet from specified path to input widget.

        Arguments:
        - widget: Any QWidget.
        - stylesheet_file: Path of stylesheet file.

        Raises:
        - FileNotFoundError if stylesheet filepath is invalid.
        - Exception if stylesheet file is invalid.
        """

        stylesheet_path = os.path.join(STYLESHEET_FOLDER_PATH, stylesheet_file)

        if not os.path.exists(stylesheet_path):
            raise FileNotFoundError(f"Stylesheet file {stylesheet_path} does not exist")
        
        try:
            with open(stylesheet_path, 'r') as f:
                stylesheet = f.read()
                widget.setStyleSheet(stylesheet)
        except Exception as e:
            print(f"Encountered error while attempting to apply stylesheet from file {stylesheet_path}")