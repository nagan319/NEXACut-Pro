from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtGui import QPixmap

from ..style import apply_stylesheet

from ..util_widgets.interactive_preview import InteractivePreview

from ....backend.utils.image_conversion.image_converter import ImageConverter

class ImageFeatureWidget(QWidget):

    featuresFinalized = pyqtSignal()

    def __init__(self, image_converter_instance: ImageConverter, pixmap_height: int):
        super().__init__()

        self.image_converter = image_converter_instance
        self.pixmap_height = pixmap_height

        self.mode = None

        self.__init_gui__()
    
    def __init_gui__(self):
        
        self.layout_with_margins = QHBoxLayout()

        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout()

        self.corner_counter = self._get_corner_counter()

        self.preview_widget = InteractivePreview()
        self.preview_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_widget.mousePressed.connect(self.on_mouse_clicked)

        self.mode_label = self._get_mode_label()
        self.save_button_widget = self._get_save_button_widget()

        self.main_layout.addWidget(self.corner_counter, 0)
        self.main_layout.addWidget(self.preview_widget, 3)
        self.main_layout.addWidget(self.mode_label, 0)
        self.main_layout.addWidget(self.save_button_widget, 0)
        self.main_widget.setLayout(self.main_layout)

        self.layout_with_margins.addStretch(1)
        self.layout_with_margins.addWidget(self.main_widget, 5)
        self.layout_with_margins.addStretch(1)

        self.setLayout(self.layout_with_margins)

    def _get_corner_counter(self) -> QLabel:
        corner_counter = QLabel()
        apply_stylesheet(corner_counter, 'generic-text.css')
        corner_counter.setAlignment(Qt.AlignmentFlag.AlignLeft)
        return corner_counter

    def _get_mode_label(self) -> QLabel:
        mode_label = QLabel()
        apply_stylesheet(mode_label, 'generic-text.css')
        mode_label.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        return mode_label      

    def _get_save_button_widget(self) -> QWidget:
        save_button_wrapper = QWidget()
        save_button_wrapper_layout = QHBoxLayout()
        save_button = QPushButton("Save Features")
        save_button.pressed.connect(self.on_save_button_pressed)
        apply_stylesheet(save_button, 'small-button.css')

        save_button_wrapper_layout.addStretch(2)
        save_button_wrapper_layout.addWidget(save_button, 1)
        save_button_wrapper_layout.addStretch(2)
        save_button_wrapper.setLayout(save_button_wrapper_layout)

        return save_button_wrapper

    def _update_mode(self):
        if len(self.image_converter.features.corners) < 4:
            self.mode = 'Add Missing Corners'
        else:
            self.mode = 'Remove Excess Features'
        self._update_mode_label()

    def _update_mode_label(self):
        self.mode_label.setText(f"Mode: {self.mode}")

    def _update_corner_counter(self):
        amt_corners = len(self.image_converter.features.corners)
        self.corner_counter.setText(f"Corners: {amt_corners}/4")
        if amt_corners == 4:
            apply_stylesheet(self.corner_counter, "generic-text.css")
        else:
            apply_stylesheet(self.corner_counter, "generic-text-red.css")

    def _update_preview_widget(self):
        pixmap = QPixmap(self.image_converter.feat_path)
        scaled_pixmap = pixmap.scaledToHeight(self.pixmap_height)
        self.preview_widget.setPixmap(scaled_pixmap)

    def update_preview(self):
        self.image_converter.save_features()
        self._update_corner_counter()
        self._update_preview_widget()
        self._update_mode()

    def on_save_button_pressed(self):
        self.featuresFinalized.emit()
    
    def on_mouse_clicked(self, pos: tuple): # refactor this junk fs
        add_mode = self.mode == 'Add Missing Corners'
        if self.image_converter.on_mouse_clicked(pos, add_mode):
            self.update_preview()