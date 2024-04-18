import os

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton

from frontend.utils.style import Style
from frontend.utils.widget_template import WidgetTemplate
from frontend.utils.widget_viewer import WidgetViewer

from frontend.file_widgets.plate_file_widget import PlateFileWidget

from backend.utils.plate_util import PlateUtil
from backend.utils.image_conversion.image_converter import ImageConverter

class InventoryWidget(WidgetTemplate):

    def __init__(self):
        super().__init__()

        self.plate_util = PlateUtil(PLATE_DATA_PREVIEW_FOLDER_PATH)

        self.image_editor_active = False

        self.__init_gui__()
        self.__init_timeout__()

    def __init_gui__(self):

        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        plate_widgets = [PlateFileWidget(self.plate_util, plate) for plate in self.app.plate_data]

        for widget in plate_widgets:
            widget.deleteRequested.connect(self.on_plate_delete_requested)
            widget.importRequested.connect(self.on_plate_import_image_requested)

        self.__file_preview_widget = WidgetViewer(3, 1, plate_widgets) 

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
        self.update_add_button_text()
    
    def __init_timeout__(self):
        self.timeout = False

    def _get_idx_of_filename(self, filename: str):
        for idx, dict in enumerate(self.app.plate_data):
            if dict['filename'] == filename: 
                return idx
        return -1

    def _get_plate_amount(self) -> int:
        return len(self.app.plate_data)

    def add_new_plate(self):
        if self.timeout:
            return

        self.timeout = True
        if self._get_plate_amount() < self.app.PLATE_LIMIT:
            new_plate_data = self.plate_util.get_new_plate(self.app.plate_data)
            self.app.plate_data.append(new_plate_data)
            
            self.plate_util.save_preview_image(new_plate_data)

            new_plate_widget = PlateFileWidget(self.plate_util, new_plate_data)
            new_plate_widget.deleteRequested.connect(self.on_plate_delete_requested)
            new_plate_widget.importRequested.connect(self.on_plate_import_image_requested)
            self.__file_preview_widget.append_widgets([new_plate_widget])
            self.update_add_button_text() 

        self.timeout = False            

    def on_plate_import_image_requested(self, filename: str):
        if self.image_editor_active:
            return

        self.image_editor_active = True
        self._create_image_edit_window(filename)

    def on_plate_delete_requested(self, filename: str):
        if self.timeout:
            return

        self.timeout = True
        index = self._get_idx_of_filename(filename)
        png_path = self.app.plate_data[index]['preview_path']
        if os.path.exists(png_path):
            self.app.file_processor.delete_file(png_path)
        self.app.plate_data.pop(index)
        self.__file_preview_widget.pop_widget(index)
        self.update_add_button_text()
        self.timeout = False

    def update_add_button_text(self):
        if self._get_plate_amount() >= self.app.PLATE_LIMIT:
            self.app.apply_stylesheet(self.__add_new_button, "generic-button-red.css")
        else:
            self.app.apply_stylesheet(self.__add_new_button, "generic-button.css")
        self.__add_new_button.setText(f"Add New ({self._get_plate_amount()}/{self.app.PLATE_LIMIT})")

    def _create_image_edit_window(self, filename: str): # refactor this trash
        
        plate_idx = self._get_idx_of_filename(filename)
        plate_dimensions = tuple([self.app.plate_data[plate_idx][key] for key in ['width_(x)', 'height_(y)', 'thickness_(z)']])

        self.image_converter = ImageConverter(IMAGE_PREVIEW_DATA_PATH, plate_dimensions)

        self.image_editor = ImageEditorWindow(self.app, self.image_converter) # necessary to keep reference to prevent immediate closure
        self.image_editor.imageEditorClosed.connect(self.on_image_editor_closed)

    def on_image_editor_closed(self):
        self.image_editor_active = False