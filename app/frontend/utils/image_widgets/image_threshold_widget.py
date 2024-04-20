from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSlider
from PyQt6.QtGui import QPixmap

from ..style import apply_stylesheet

from ....backend.utils.image_conversion.image_converter import ImageConverter


class ImageThresholdWidget(QWidget):

    binaryFinalized = pyqtSignal()

    COLOR_MIN = 0
    COLOR_MAX = 255
    COLOR_MID = (COLOR_MIN + COLOR_MAX)//2

    def __init__(self, image_converter_instance: ImageConverter):
        super().__init__()

        self.image_converter = image_converter_instance
        
        self.threshold = self.COLOR_MID

        self.__init_gui__()

    def __init_gui__(self):
        self.layout_with_margins = QHBoxLayout()

        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout()

        self.preview_widget = QLabel()
        self.preview_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.slider_label = QLabel("Adjust Threshold Value")
        self.slider_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        apply_stylesheet(self.slider_label, 'small-text.css')

        self.slider = QSlider()
        self.slider.setOrientation(Qt.Orientation.Horizontal) 
        self.slider.setMinimum(self.COLOR_MIN)
        self.slider.setMaximum(self.COLOR_MAX)
        self.slider.setValue(self.COLOR_MID)

        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)  
        self.slider.setTickInterval(16)

        self.slider.valueChanged.connect(self.on_threshold_parameter_edited)

        self.save_button_wrapper = QWidget()
        self.save_button_wrapper_layout = QHBoxLayout()
        self.save_button = QPushButton("Save Binary")
        self.save_button.pressed.connect(self.on_save_button_pressed)
        apply_stylesheet(self.save_button, 'small-button.css')

        self.save_button_wrapper_layout.addStretch(2)
        self.save_button_wrapper_layout.addWidget(self.save_button, 1)
        self.save_button_wrapper_layout.addStretch(2)
        self.save_button_wrapper.setLayout(self.save_button_wrapper_layout)

        self.main_layout.addWidget(self.preview_widget, 3)
        self.main_layout.addWidget(self.slider_label, 0)
        self.main_layout.addWidget(self.slider, 1)
        self.main_layout.addWidget(self.save_button_wrapper, 0)
        self.main_widget.setLayout(self.main_layout)

        self.layout_with_margins.addStretch(1)
        self.layout_with_margins.addWidget(self.main_widget, 5)
        self.layout_with_margins.addStretch(1)

        self.setLayout(self.layout_with_margins)

    def _generate_binary(self):
        self.image_converter.save_binary(self.threshold)

    def update_preview(self):
        self._generate_binary()
        pixmap = QPixmap(self.image_converter.bin_path)
        scaled_pixmap = pixmap.scaledToHeight(600)
        self.preview_widget.setPixmap(scaled_pixmap)
    
    def on_threshold_parameter_edited(self, value: int):
        self.threshold = value
        self.update_preview()

    def on_save_button_pressed(self):
        self.binaryFinalized.emit()