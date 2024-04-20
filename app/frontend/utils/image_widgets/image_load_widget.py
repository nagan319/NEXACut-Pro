from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog

from ..style import apply_stylesheet

from ....backend.utils.image_conversion.image_converter import ImageConverter

class ImageLoadWidget(QWidget):

    SUPPORTED_IMAGE_FORMATS = "Image Files (*.bmp *.dib *.jpeg *.jpg *.jp2 *.png *.webp *.avif)" 

    imageImported = pyqtSignal()

    def __init__(self, image_converter_instance: ImageConverter):
        super().__init__()
        self.image_converter = image_converter_instance
        self.__init_gui__()
    
    def __init_gui__(self):
        self.main_layout = QVBoxLayout()

        self.button_frame = QWidget()
        self.button_frame_layout = QHBoxLayout()
        self.import_button = QPushButton("Import Image File")
        apply_stylesheet(self.import_button, 'generic-button.css')
        self.import_button.pressed.connect(self.import_image_file)

        self.button_frame_layout.addStretch(2)
        self.button_frame_layout.addWidget(self.import_button, 1)
        self.button_frame_layout.addStretch(2)
        self.button_frame.setLayout(self.button_frame_layout)

        self.main_layout.addStretch(3)
        self.main_layout.addWidget(self.button_frame, 1)
        self.main_layout.addStretch(3)

        self.setLayout(self.main_layout)

    def import_image_file(self):
 
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", self.SUPPORTED_IMAGE_FORMATS)
        self.image_converter.__init_src_path__(file_path)
        self.imageImported.emit()