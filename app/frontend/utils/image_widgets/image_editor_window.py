from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout

from .image_editor_widget import ImageEditorWidget
from ....backend.utils.image_conversion.image_converter import ImageConverter

class ImageEditorWindow(QMainWindow):
    
    MIN_HEIGHT = 800
    MIN_WIDTH = 800
    WINDOW_TITLE = 'Attach Image File'

    imageEditorClosed = pyqtSignal()

    def __init__(self, image_converter_instance: ImageConverter):
        super().__init__()

        self.image_converter = image_converter_instance

        self.setMinimumSize(self.MIN_WIDTH, self.MIN_HEIGHT)
        self.setWindowTitle(self.WINDOW_TITLE)

        self.__layout = QVBoxLayout()
        self.__layout.setContentsMargins(0, 0, 0, 0) 
        self.__layout.setSpacing(0)

        self.image_editor = ImageEditorWidget(self.image_converter)
        self.__layout.addWidget(self.image_editor)
        self.__main_widget = QWidget()
        self.__main_widget.setLayout(self.__layout)
        self.setCentralWidget(self.__main_widget)
        self.show()

    def closeEvent(self, event):
        print()
        self.imageEditorClosed.emit()