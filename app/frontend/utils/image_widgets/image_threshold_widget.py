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
        self.slider_label = self._get_slider_label()
        self.slider = self._get_slider()
        self.save_button_widget = self._get_save_button_widget()

        self.main_layout.addWidget(self.preview_widget, 3)
        self.main_layout.addWidget(self.slider_label, 0)
        self.main_layout.addWidget(self.slider, 1)
        self.main_layout.addWidget(self.save_button_widget, 0)
        self.main_widget.setLayout(self.main_layout)

        self.layout_with_margins.addStretch(1)
        self.layout_with_margins.addWidget(self.main_widget, 5)
        self.layout_with_margins.addStretch(1)

        self.setLayout(self.layout_with_margins)

    def _get_slider_label(self) -> QWidget:
        slider_label = QLabel("Adjust Threshold Value")
        slider_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        apply_stylesheet(slider_label, 'small-text.css')
        return slider_label

    def _get_slider(self) -> QWidget:
        slider = QSlider()
        slider.setOrientation(Qt.Orientation.Horizontal) 
        slider.setMinimum(self.COLOR_MIN)
        slider.setMaximum(self.COLOR_MAX)
        slider.setValue(self.COLOR_MID)
        slider.setTickPosition(QSlider.TickPosition.TicksBelow)  
        slider.setTickInterval
        slider.valueChanged.connect(self.on_threshold_parameter_edited)
        return slider

    def _get_save_button_widget(self) -> QWidget:
        save_button_wrapper = QWidget()
        save_button_wrapper_layout = QHBoxLayout()
        save_button = QPushButton("Save Binary")
        save_button.pressed.connect(self.on_save_button_pressed)
        apply_stylesheet(save_button, 'small-button.css')

        save_button_wrapper_layout.addStretch(2)
        save_button_wrapper_layout.addWidget(save_button, 1)
        save_button_wrapper_layout.addStretch(2)
        save_button_wrapper.setLayout(save_button_wrapper_layout)
        return save_button_wrapper

    def update_preview(self):
        self.image_converter.save_binary(self.threshold)
        pixmap = QPixmap(self.image_converter.bin_path)
        scaled_pixmap = pixmap.scaledToHeight(600)
        self.preview_widget.setPixmap(scaled_pixmap)
    
    def on_threshold_parameter_edited(self, value: int):
        self.threshold = value
        self.update_preview()

    def on_save_button_pressed(self):
        self.binaryFinalized.emit()