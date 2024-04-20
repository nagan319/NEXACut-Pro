import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton

from ..utils.style import apply_stylesheet
from ..utils.util_widgets.widget_template import WidgetTemplate
from ..utils.util_widgets.widget_viewer import WidgetViewer
from ..utils.file_widgets.plate_file_widget import PlateFileWidget
from ..utils.image_widgets.image_editor_window import ImageEditorWindow

from ...backend.utils.plate_util import PlateUtil
from ...backend.utils.image_conversion.image_converter import ImageConverter
from ...backend.utils.file_operations import FileProcessor

from ...config import PLATE_PREVIEW_DATA_PATH

class InventoryWidget(WidgetTemplate):

    def __init__(self, plate_data: list, plate_limit: int):
        super().__init__()

        self.plate_util = PlateUtil(PLATE_PREVIEW_DATA_PATH)

        self.plate_data = plate_data
        self.plate_limit = plate_limit
        self.image_editor_active = False

        self.__init_gui__()

    def __init_gui__(self):

        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        plate_widgets = [PlateFileWidget(self.plate_util, plate) for plate in self.plate_data]

        for widget in plate_widgets:
            widget.deleteRequested.connect(self.on_plate_delete_requested)
            widget.importRequested.connect(self.on_plate_import_image_requested)

        self.__file_preview_widget = WidgetViewer(3, 1, plate_widgets) 

        self.__add_new_button_wrapper = QWidget()
        self.__add_new_button_wrapper_layout = QHBoxLayout()

        self.__add_new_button = QPushButton()
        apply_stylesheet(self.__add_new_button, "generic-button.css")
        self.__add_new_button.clicked.connect(self.add_new_plate)

        self.__add_new_button_wrapper_layout.addStretch(2)
        self.__add_new_button_wrapper_layout.addWidget(self.__add_new_button, 1)
        self.__add_new_button_wrapper_layout.addStretch(2)
        self.__add_new_button_wrapper.setLayout(self.__add_new_button_wrapper_layout)

        main_layout.addWidget(self.__file_preview_widget, 7)
        main_layout.addWidget(self.__add_new_button_wrapper, 1)
        main_widget.setLayout(main_layout)

        apply_stylesheet(main_widget, "light.css")

        self.__init_template_gui__("Manage Inventory", main_widget)
        self.update_add_button_text()

    def _get_idx_of_filename(self, filename: str):
        for idx, dict in enumerate(self.plate_data):
            if dict['filename'] == filename: 
                return idx
        return -1

    def _get_plate_amount(self) -> int:
        return len(self.plate_data)

    def add_new_plate(self):
        if self._get_plate_amount() < self.plate_limit:
            new_plate_data = self.plate_util.get_new_plate(self.plate_data)
            self.plate_data.append(new_plate_data)
            
            self.plate_util.save_preview_image(new_plate_data)

            new_plate_widget = PlateFileWidget(self.plate_util, new_plate_data)
            new_plate_widget.deleteRequested.connect(self.on_plate_delete_requested)
            new_plate_widget.importRequested.connect(self.on_plate_import_image_requested)
            self.__file_preview_widget.append_widgets([new_plate_widget])
            self.update_add_button_text()         

    def on_plate_import_image_requested(self, filename: str):
        if self.image_editor_active:
            return

        self.image_editor_active = True
        self._create_image_edit_window(filename)

    def on_plate_delete_requested(self, filename: str):
        self.timeout = True
        index = self._get_idx_of_filename(filename)

        file_processor = FileProcessor()
        png_path = self.plate_data[index]['preview_path']
        file_processor.delete_file(png_path)

        self.plate_data.pop(index)
        self.__file_preview_widget.pop_widget(index)
        self.update_add_button_text()

    def update_add_button_text(self):
        if self._get_plate_amount() >= self.plate_limit:
            apply_stylesheet(self.__add_new_button, "generic-button-red.css")
        else:
            apply_stylesheet(self.__add_new_button, "generic-button.css")
        self.__add_new_button.setText(f"Add New ({self._get_plate_amount()}/{self.plate_limit})")

    def _create_image_edit_window(self, filename: str): 
        
        plate_idx = self._get_idx_of_filename(filename)
        plate_w = self.plate_data[plate_idx]['width_(x)'] 
        plate_h = self.plate_data[plate_idx]['height_(y)']
        self.image_editor = ImageEditorWindow(plate_w, plate_h) 
        self.image_editor.imageEditorClosed.connect(self.on_image_editor_closed)

    def on_image_editor_closed(self):
        self.image_editor_active = False