from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton

from ..style import apply_stylesheet
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
        self.img_button_container = self._get_img_import_widget()
        self.data_widget = self._get_data_widget()

        layout.addWidget(self.preview_widget, 5)
        layout.addWidget(self.img_button_container, 1)
        layout.addWidget(self.data_widget, 4)
        self.setLayout(layout)

    def _get_img_import_widget(self) -> QWidget:
        import_button_container = QWidget()
        import_button_container_layout = QHBoxLayout()
        import_button = QPushButton("Import Image")
        import_button.pressed.connect(self.__on_import_requested__)
        apply_stylesheet(import_button, 'small-button.css')

        import_button_container_layout.addStretch(1)
        import_button_container_layout.addWidget(import_button, 2)
        import_button_container_layout.addStretch(1)
        import_button_container.setLayout(import_button_container_layout)
        return import_button_container

    def _get_data_widget(self) -> QWidget:
        data_widget = DataWidget(self.data, self.plate_util.editable_keys, self.plate_util.value_ranges, False, True)
        data_widget.deleteRequested.connect(self.__on_delete_requested__)
        data_widget.saveRequested.connect(self.__on_save_requested__)
        return data_widget

    def _update_preview(self):
        self.plate_util.save_preview_image(self.data)
        self.preview_widget.update()

    def __on_import_requested__(self):
        self.importRequested.emit(self.data['filename'])

    def __on_save_requested__(self, data: dict):
        self.data = data
        self._update_preview()

    def update_image_preview(self):
        self._update_preview()

    def __on_delete_requested__(self):
        self.deleteRequested.emit(self.data['filename'])

