from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtGui import QPixmap

from utils.style import Style

from backend.utils.image_conversion.image_converter import ImageConverter

class ImageFeatureWidget(QWidget):

    featuresFinalized = pyqtSignal()

    def __init__(self, image_converter_instance: ImageConverter):
        super().__init__()

        self.image_converter = image_converter_instance

        self.__init_gui__()
    
    def __init_gui__(self):
        
        self.layout_with_margins = QHBoxLayout()

        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout()

        self.preview_widget = QLabel()
        self.preview_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.save_button_wrapper = QWidget()
        self.save_button_wrapper_layout = QHBoxLayout()
        self.save_button = QPushButton("Save Features")
        self.save_button.pressed.connect(self.on_save_button_pressed)
        self.app.apply_stylesheet(self.save_button, 'small-button.css')

        self.save_button_wrapper_layout.addStretch(2)
        self.save_button_wrapper_layout.addWidget(self.save_button, 1)
        self.save_button_wrapper_layout.addStretch(2)
        self.save_button_wrapper.setLayout(self.save_button_wrapper_layout)

        self.main_layout.addWidget(self.preview_widget, 3)
        self.main_layout.addWidget(self.save_button_wrapper, 0)
        self.main_widget.setLayout(self.main_layout)

        self.layout_with_margins.addStretch(1)
        self.layout_with_margins.addWidget(self.main_widget, 5)
        self.layout_with_margins.addStretch(1)

        self.setLayout(self.layout_with_margins)

    def _generate_contour_img(self):
        self.image_converter.save_contour_image()

    def update_preview(self):
        self._generate_contour_img()
        contour_path = os.path.join(IMAGE_PREVIEW_DATA_PATH, CONTOUR_EXTENSION)
        pixmap = QPixmap(contour_path)
        scaled_pixmap = pixmap.scaledToHeight(600)
        self.preview_widget.setPixmap(scaled_pixmap)

    def on_save_button_pressed(self):
        self.featuresFinalized.emit()