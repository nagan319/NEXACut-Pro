from enum import Enum

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtGui import QPixmap

from ..style import apply_stylesheet

from ..util_widgets.interactive_preview import InteractivePreview

from ....backend.utils.image_conversion.image_converter import ImageConverter

class Mode(Enum):
    ADD_MISSING_CORNERS = 0
    REMOVE_EXCESS_FEATURES = 1

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

        top_bar = QWidget()
        top_layout = QHBoxLayout()
        self.corner_counter = self._get_corner_counter()
        self.delete_button = self._get_delete_button()
        top_layout.addWidget(self.corner_counter, 1)
        top_layout.addStretch(2)
        top_layout.addWidget(self.delete_button, 1)
        top_bar.setLayout(top_layout)
        
        self.preview_widget = InteractivePreview()
        self.preview_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_widget.mousePressed.connect(self.on_mouse_clicked)

        self.mode_label = self._get_mode_label()
        self.save_button_widget = self._get_save_button_widget()

        self.main_layout.addWidget(top_bar, 0)
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
        corner_counter.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return corner_counter

    def _get_delete_button(self) -> QPushButton:
        delete_button = QPushButton("Delete Selected")
        delete_button.pressed.connect(self.on_delete_button_pressed)
        apply_stylesheet(delete_button, 'small-button-inactive.css') 
        return delete_button

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

    def _unselect_features(self):
        self.image_converter.features.selected_corner = None
        self.image_converter.features.selected_contour = None

    def _selection_active(self):
        return (self.image_converter.features.selected_corner is not None) \
            or (self.image_converter.features.selected_contour is not None)

    def _update_mode(self):
        if len(self.image_converter.features.corners) < 4:
            self.mode = Mode.ADD_MISSING_CORNERS
            self._unselect_features()
        else:
            self.mode = Mode.REMOVE_EXCESS_FEATURES

    def _update_corner_counter(self):
        amt_corners = len(self.image_converter.features.corners)
        self.corner_counter.setText(f"Corners: {amt_corners}/4")
        stylesheet = "generic-text.css" if amt_corners == 4 else "generic-text-red.css"
        apply_stylesheet(self.corner_counter, stylesheet)

    def _update_preview_widget(self):
        pixmap = QPixmap(self.image_converter.feat_path)
        scaled_pixmap = pixmap.scaledToHeight(self.pixmap_height)
        self.preview_widget.setPixmap(scaled_pixmap)

    def _update_delete_button_widget(self):
        if self.mode == Mode.REMOVE_EXCESS_FEATURES and self._selection_active():
            apply_stylesheet(self.delete_button, 'small-button.css')
        else:
            apply_stylesheet(self.delete_button, 'small-button-inactive.css')

    def _update_mode_label(self):
        mode_text = "Add Missing Corners" if self.mode == Mode.ADD_MISSING_CORNERS else "Remove Excess Features"
        self.mode_label.setText(mode_text)

    def update(self):
        self.image_converter.save_features()
        self._update_mode()
        self._update_corner_counter()
        self._update_preview_widget()
        self._update_delete_button_widget()
        self._update_mode_label()

    def on_save_button_pressed(self):
        self.featuresFinalized.emit()
    
    def on_delete_button_pressed(self):

        corner = self.image_converter.features.selected_corner
        contour = self.image_converter.features.selected_contour

        if corner is None and contour is None:
            return

        if corner is not None:
            self.image_converter.feature_editor.remove_corner()
        
        if contour is not None:
            self.image_converter.feature_editor.remove_contour()

        self.update()

    def on_mouse_clicked(self, pos: tuple):
        if self.mode == Mode.ADD_MISSING_CORNERS:
            self.image_converter.corner_added(pos)
        else:
            if not self.image_converter.feature_selected(pos):
                return
        self.update()