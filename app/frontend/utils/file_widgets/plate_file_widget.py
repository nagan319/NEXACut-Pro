from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton

from ..style import Style
from ..util_widgets.preview_widget import PreviewWidget
from ..util_widgets.data_widget import DataWidget

from ....backend.utils.plate_util import PlateUtil

class PlateFileWidget(QWidget):
    """
    Widget for managing plate files.

    ### Parameters:
    - data: Plate data in dict form.
    """
    deleteRequested = pyqtSignal(int)
    importRequested = pyqtSignal(int)

    def __init__(self, data: dict):
        super().__init__()

        self.data = data

        self._setup_ui()

    # ui initialization functions

    def _setup_ui(self):
        """
        Initialize widget ui.
        """
        self._preview_widget = PreviewWidget(self.data['preview_path'])
        image_button_container = self._get_image_button_container()
        data_widget = self._get_data_widget()

        layout = QVBoxLayout()
        layout.addWidget(self._preview_widget, 5)
        layout.addWidget(image_button_container, 1)
        layout.addWidget(data_widget, 4)
        self.setLayout(layout)

    def _get_image_button_container(self) -> QWidget:
        """
        Get container for "Import Image" button.
        """
        image_button = QPushButton("Import Image")
        image_button.pressed.connect(self.__on_import_requested)
        Style.apply_stylesheet(image_button, 'small-button.css')

        image_button_container_layout = QHBoxLayout()
        image_button_container_layout.addStretch(1)
        image_button_container_layout.addWidget(image_button, 2)
        image_button_container_layout.addStretch(1)

        image_button_container = QWidget()
        image_button_container.setLayout(image_button_container_layout)

        return image_button_container

    def _get_data_widget(self) -> QWidget:
        """
        Get widget for storing plate data.
        """
        data_widget = DataWidget(self.data, PlateUtil.editable_keys(), PlateUtil.value_ranges(), False, True)
        data_widget.deleteRequested.connect(self.__on_delete_requested)
        data_widget.saveRequested.connect(self.__on_save_requested)
        return data_widget

    # runtime functions

    def update_image_preview(self):
        """
        Update image preview (public).
        """
        self._update_preview()

    def _update_preview(self):
        PlateUtil.save_preview_image(self.data)
        self._preview_widget.update()

    def __on_import_requested(self):
        self.importRequested.emit(self.data['id'])

    def __on_save_requested(self, data: dict):
        self.data = data
        self._update_preview()

    def __on_delete_requested(self):
        self.deleteRequested.emit(self.data['id'])

