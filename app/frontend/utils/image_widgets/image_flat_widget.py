from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSlider
from PyQt6.QtGui import QPixmap

from ..style import apply_stylesheet

from ....backend.utils.image_conversion.image_converter import ImageConverter

class ImageFlatWidget(QWidget):

    saveImage = pyqtSignal()

    def __init__(self, image_converter_instance: ImageConverter, pixmap_height: int):
        super().__init__()

        self.image_converter = image_converter_instance
        self.pixmap_height = pixmap_height

        self.__init_gui__()

    def __init_gui__(self):
        self.layout_with_margins = QHBoxLayout()

        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout()

        self.preview_widget = QLabel()
        self.preview_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.save_button_widget = self._get_save_button_widget()

        self.main_layout.addWidget(self.preview_widget, 3)
        self.main_layout.addWidget(self.save_button_widget, 0)
        self.main_widget.setLayout(self.main_layout)

        self.layout_with_margins.addStretch(1)
        self.layout_with_margins.addWidget(self.main_widget, 5)
        self.layout_with_margins.addStretch(1)

        self.setLayout(self.layout_with_margins)

    def _get_save_button_widget(self) -> QWidget:
        save_button_wrapper = QWidget()
        save_button_wrapper_layout = QHBoxLayout()
        save_button = QPushButton("Save Image")
        save_button.pressed.connect(self.on_save_button_pressed)
        apply_stylesheet(save_button, 'small-button.css')

        save_button_wrapper_layout.addStretch(2)
        save_button_wrapper_layout.addWidget(save_button, 1)
        save_button_wrapper_layout.addStretch(2)
        save_button_wrapper.setLayout(save_button_wrapper_layout)
        return save_button_wrapper
    
    def update(self):
        pixmap = QPixmap(self.image_converter.flat_path)
        scaled_pixmap = pixmap.scaledToHeight(self.pixmap_height)
        self.preview_widget.setPixmap(scaled_pixmap)

    def on_save_button_pressed(self):
        self.saveImage.emit()