from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout

from .image_editor_widget import ImageEditorWidget
from ....backend.utils.image_conversion.image_converter import ImageConverter

from ....config import IMAGE_PREVIEW_DATA_PATH

class ImageEditorWindow(QMainWindow):
    
    MIN_HEIGHT = 800
    MIN_WIDTH = 800
    WINDOW_TITLE = 'Attach Image File'
 
    PIXMAP_HEIGHT = 600

    imageEditorClosed = pyqtSignal(int, list)

    def __init__(self, plate_index: int, plate_w: float, plate_h: float):
        super().__init__()

        self.plate_index = plate_index
        self.filename = str(plate_index)+'.png'
        self.image_converter = ImageConverter(IMAGE_PREVIEW_DATA_PATH, plate_w, plate_h, self.PIXMAP_HEIGHT)

        self.setMinimumSize(self.MIN_WIDTH, self.MIN_HEIGHT)
        self.setWindowTitle(self.WINDOW_TITLE)

        self.__layout = QVBoxLayout()
        self.__layout.setContentsMargins(0, 0, 0, 0) 
        self.__layout.setSpacing(0)

        self.image_editor = ImageEditorWidget(self.image_converter, self.PIXMAP_HEIGHT)
        self.image_editor.editingFinished.connect(self.close)

        self.__layout.addWidget(self.image_editor)
        self.__main_widget = QWidget()
        self.__main_widget.setLayout(self.__layout)
        self.setCentralWidget(self.__main_widget)
        self.show()

    def closeEvent(self, event):
        contours = self.image_converter.get_finalized_contours()
        self.imageEditorClosed.emit(self.plate_index, contours)