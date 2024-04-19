from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton

from ..style import Style
from ..util_widgets.preview_widget import PreviewWidget
from ..util_widgets.data_widget import DataWidget

from ....backend.utils.plate_util import PlateUtil

class PlateFileWidget(QWidget):

    deleteRequested = pyqtSignal(str)
    importRequested = pyqtSignal(str)

    def __init__(self, plate_util: PlateUtil, data: dict):
        super().__init__()

        self.plate_util = plate_util
        self.data = data

        layout = QVBoxLayout()

        self.preview_widget = PreviewWidget(self.data['preview_path'])

        self.img_button_container = QWidget()
        self.img_button_container_layout = QHBoxLayout()
        self.img_button = QPushButton("Import Image")
        self.img_button.pressed.connect(self.on_import_requested)
        Style.apply_stylesheet(self.img_button, 'small-button.css')
        self.img_button_container_layout.addStretch(1)
        self.img_button_container_layout.addWidget(self.img_button, 2)
        self.img_button_container_layout.addStretch(1)
        self.img_button_container.setLayout(self.img_button_container_layout)

        self.data_widget = DataWidget(self.data, self.plate_util.editable_keys, self.plate_util.value_ranges, False, True)
        self.data_widget.deleteRequested.connect(self.on_delete_requested)
        self.data_widget.saveRequested.connect(self.on_save_requested)

        layout.addWidget(self.preview_widget, 5)
        layout.addWidget(self.img_button_container, 1)
        layout.addWidget(self.data_widget, 4)
        self.setLayout(layout)

    def on_import_requested(self):
        self.importRequested.emit(self.data['filename'])

    def on_save_requested(self, data: dict):
        self.data = data
        self._update_preview()

    def on_delete_requested(self):
        self.deleteRequested.emit(self.data['filename'])

    def _update_preview(self):
        self.plate_util.save_preview_image(self.data)
        self.preview_widget.update()