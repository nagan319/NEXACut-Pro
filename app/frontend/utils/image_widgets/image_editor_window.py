from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout

from backend.utils.image_conversion.image_converter import ImageConverter

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

        self.__init_gui__()
    
    def __init_gui__(self):
        self.__layout = QVBoxLayout()
        self.__layout.setContentsMargins(0, 0, 0, 0) 
        self.__layout.setSpacing(0)
        self.image_editor = ImageEditorWidget(self.app, self.image_converter)
        self.__layout.addWidget(self.image_editor)
        self.__widget = QWidget()
        self.__widget.setLayout(self.__layout)
        self.setCentralWidget(self.__widget)
        self.show()

    def closeEvent(self, event):
        print()
        self.imageEditorClosed.emit()