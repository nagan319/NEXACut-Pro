import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton

import logging

from ..utils.style import Style
from ..utils.util_widgets.widget_template import WidgetTemplate
from ..utils.util_widgets.widget_viewer import WidgetViewer
from ..utils.file_widgets.plate_file_widget import PlateFileWidget
from ..utils.image_widgets.image_editor_window import ImageEditorWindow

from ...backend.utils.plate_util import PlateUtil
from ...backend.utils.file_processor import FileProcessor

from ...config import PLATE_PREVIEW_DATA_PATH

class InventoryWidget(WidgetTemplate):
    """
    Tab for handling CNC stock.

    ### Parameters:
    - plate_data: List of plates currently in inventory.
    - plate_limit: Maximum number of plates able to be stored in app.
    """
    def __init__(self, plate_data: list, plate_limit: int):
        self.logger = logging.getLogger(__name__)
        if not self.logger.hasHandlers():
            self.logger.setLevel(logging.DEBUG)
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        self.logger.debug(f"Initializing inventory widget...")

        super().__init__()

        self.plate_data = plate_data
        self.plate_limit = plate_limit
        self.image_editor_active = False

        self._setup_ui()
        self.logger.debug(f"Initialization complete.")

    def _setup_ui(self):
        """
        Initialize widget ui.
        """
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        self.plate_widgets = [PlateFileWidget(plate) for plate in self.plate_data]

        for widget in self.plate_widgets:
            widget.deleteRequested.connect(self.__on_plate_delete_requested__)
            widget.importRequested.connect(self.__on_plate_import_image_requested__)

        self._file_preview_widget = WidgetViewer(3, 1, self.plate_widgets) 

        add_new_button_wrapper = QWidget()
        add_new_button_wrapper_layout = QHBoxLayout()

        self._add_new_button = QPushButton()
        Style.apply_stylesheet(self._add_new_button, "generic-button.css")
        self._add_new_button.clicked.connect(self.add_new_plate)

        add_new_button_wrapper_layout.addStretch(2)
        add_new_button_wrapper_layout.addWidget(self._add_new_button, 1)
        add_new_button_wrapper_layout.addStretch(2)
        add_new_button_wrapper.setLayout(add_new_button_wrapper_layout)

        main_layout.addWidget(self._file_preview_widget, 7)
        main_layout.addWidget(add_new_button_wrapper, 1)
        main_widget.setLayout(main_layout)

        Style.apply_stylesheet(main_widget, "light.css")

        self.__init_template_gui__("Manage Inventory", main_widget)
        self._update_add_button_text()

    def add_new_plate(self):
        """
        Add new plate to data list.
        """
        if self.image_editor_active:
            return
        if self._get_plate_amount() >= self.plate_limit:
            return 
        
        self.logger.debug(f"Adding new plate...")

        new_plate_data = PlateUtil.get_new_plate(self.plate_data)
        PlateUtil.save_preview_image(new_plate_data)
        self.plate_data.append(new_plate_data)

        self.logger.debug(f"Creating widget for new plate...")
        new_plate_widget = PlateFileWidget(new_plate_data)
        new_plate_widget.deleteRequested.connect(self.__on_plate_delete_requested__)
        new_plate_widget.importRequested.connect(self.__on_plate_import_image_requested__)
        self._file_preview_widget.append_widgets([new_plate_widget])
        self._update_add_button_text()       
        self.logger.debug(f"New plate added successfully.")
    
    def _get_plate_amount(self) -> int:
        """
        Get amount of plates in data list.
        """
        return len(self.plate_data)  

    def _get_idx_of_plate_in_list(self, id: int):
        """
        Get index of plate in data list by id.
        """
        for idx, dict in enumerate(self.plate_data):
            if dict['id'] == id: 
                return idx
        return -1

    def _update_add_button_text(self):
        """
        Update button based on amount of parts and whether or not the plate limit is reached.
        """
        if self._get_plate_amount() >= self.plate_limit:
            Style.apply_stylesheet(self._add_new_button, "generic-button-red.css")
        else:
            Style.apply_stylesheet(self._add_new_button, "generic-button.css")
        self._add_new_button.setText(f"Add New ({self._get_plate_amount()}/{self.plate_limit})")

    def __on_plate_import_image_requested__(self, id: int):
        if self.image_editor_active:
            return
        
        self.image_editor_active = True
        self._create_image_edit_window(id)

    def _create_image_edit_window(self, id: int): 
        """
        Initialize ImageEditorWindow for plate with a given id.
        """
        self.logger.debug(f"Initializing image editor for plate #{str(id)}...")
        plate_idx = self._get_idx_of_plate_in_list(id)
        plate_w = self.plate_data[plate_idx]['width_(x)'] 
        plate_h = self.plate_data[plate_idx]['height_(y)']
        self.image_editor = ImageEditorWindow(id, plate_w, plate_h) 
        self.image_editor.imageEditorClosed.connect(self.__on_image_editor_closed__)

    def __on_image_editor_closed__(self, id: int, contours: list): 
        self.logger.debug(f"Saving data for plate #{str(id)}...")
        plate_idx = self._get_idx_of_plate_in_list(id)
        self.plate_data[plate_idx]['contours'] = self._serialize_contours(contours)
        PlateUtil.save_preview_image(self.plate_data[plate_idx])
        self.plate_widgets[plate_idx].update_image_preview()
        self.logger.debug(f"Plate contours saved successfully.")
        self.image_editor_active = False

    def _serialize_contours(self, contours: list):
        serialized = []
        for contour in contours:
            serialized.append(contour.tolist())
        return serialized

    def __on_plate_delete_requested__(self, id: int):
        """
        Removes plate from data, deleting preview path.
        """
        if self.image_editor_active:
            return

        index = self._get_idx_of_plate_in_list(id)

        file_processor = FileProcessor()
        png_path = self.plate_data[index]['preview_path']
        file_processor.remove_file(png_path)

        self.plate_data.pop(index)
        self._file_preview_widget.pop_widget(index)
        self._update_add_button_text()

