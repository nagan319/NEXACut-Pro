import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton

from ..utils.style import Style
from ..utils.util_widgets.widget_template import WidgetTemplate
from ..utils.util_widgets.widget_viewer import WidgetViewer
from ..utils.file_widgets.plate_file_widget import PlateFileWidget
from ..utils.image_widgets.image_editor_window import ImageEditorWindow

from ...backend.utils.plate_util import PlateUtil
from ...backend.utils.file_processor import FileProcessor

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
        
        self.plate_widgets = [PlateFileWidget(self.plate_util, plate) for plate in self.plate_data]

        for widget in self.plate_widgets:
            widget.deleteRequested.connect(self.__on_plate_delete_requested__)
            widget.importRequested.connect(self.__on_plate_import_image_requested__)

        self.__file_preview_widget = WidgetViewer(3, 1, self.plate_widgets) 

        self.__add_new_button_wrapper = QWidget()
        self.__add_new_button_wrapper_layout = QHBoxLayout()

        self.__add_new_button = QPushButton()
        Style.apply_stylesheet(self.__add_new_button, "generic-button.css")
        self.__add_new_button.clicked.connect(self.add_new_plate)

        self.__add_new_button_wrapper_layout.addStretch(2)
        self.__add_new_button_wrapper_layout.addWidget(self.__add_new_button, 1)
        self.__add_new_button_wrapper_layout.addStretch(2)
        self.__add_new_button_wrapper.setLayout(self.__add_new_button_wrapper_layout)

        main_layout.addWidget(self.__file_preview_widget, 7)
        main_layout.addWidget(self.__add_new_button_wrapper, 1)
        main_widget.setLayout(main_layout)

        Style.apply_stylesheet(main_widget, "light.css")

        self.__init_template_gui__("Manage Inventory", main_widget)
        self._update_add_button_text()

    def add_new_plate(self):
        if self.image_editor_active:
            return

        if self._get_plate_amount() < self.plate_limit:
            new_plate_data = self.plate_util.get_new_plate(self.plate_data)
            self.plate_data.append(new_plate_data)
            
            self.plate_util.save_preview_image(new_plate_data)

            new_plate_widget = PlateFileWidget(self.plate_util, new_plate_data)
            new_plate_widget.deleteRequested.connect(self.__on_plate_delete_requested__)
            new_plate_widget.importRequested.connect(self.__on_plate_import_image_requested__)
            self.__file_preview_widget.append_widgets([new_plate_widget])
            self._update_add_button_text()       

    def _get_idx_of_filename(self, filename: str):
        for idx, dict in enumerate(self.plate_data):
            if dict['filename'] == filename: 
                return idx
        return -1

    def _get_plate_amount(self) -> int:
        return len(self.plate_data)  

    def _update_add_button_text(self):
        if self._get_plate_amount() >= self.plate_limit:
            Style.apply_stylesheet(self.__add_new_button, "generic-button-red.css")
        else:
            Style.apply_stylesheet(self.__add_new_button, "generic-button.css")
        self.__add_new_button.setText(f"Add New ({self._get_plate_amount()}/{self.plate_limit})")

    def __on_plate_import_image_requested__(self, filename: str):
        if self.image_editor_active:
            return

        self.image_editor_active = True
        self._create_image_edit_window(filename)

    def _create_image_edit_window(self, filename: str): 
        
        plate_idx = self._get_idx_of_filename(filename)
        plate_w = self.plate_data[plate_idx]['width_(x)'] 
        plate_h = self.plate_data[plate_idx]['height_(y)']
        self.image_editor = ImageEditorWindow(filename, plate_w, plate_h) 
        self.image_editor.imageEditorClosed.connect(self.__on_image_editor_closed__)

    def __on_image_editor_closed__(self, filename: str, contours: list): 
        plate_idx = self._get_idx_of_filename(filename)
        self.plate_data[plate_idx]['contours'] = self._serialize_contours(contours)
        self.plate_util.save_preview_image(self.plate_data[plate_idx])
        self.plate_widgets[plate_idx].update_image_preview()
        self.image_editor_active = False

    def _serialize_contours(self, contours: list):
        serialized = []
        for contour in contours:
            serialized.append(contour.tolist())
        return serialized

    def __on_plate_delete_requested__(self, filename: str):
        if self.image_editor_active:
            return

        index = self._get_idx_of_filename(filename)

        file_processor = FileProcessor()
        png_path = self.plate_data[index]['preview_path']
        file_processor.remove_file(png_path)

        self.plate_data.pop(index)
        self.__file_preview_widget.pop_widget(index)
        self._update_add_button_text()

