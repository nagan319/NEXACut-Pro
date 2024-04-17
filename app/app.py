import sys
import os
import shutil
import json
import atexit
import copy
import math

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QStackedWidget, QFileDialog, QLineEdit, QSlider
from PyQt6.QtGui import QPixmap, QFontDatabase

from filepaths import * 
from file_operations import FileProcessor

from utils.stl_parser import STLParser

from utils.router_util import RouterUtil
from utils.plate_util import PlateUtil
from utils.value_conversion import parse_text

from utils.image_conversion.image_converter import ImageConverter
from utils.image_conversion.constants import SUPPORTED_IMAGE_FORMATS, RAW_EXTENSION, BINARY_EXTENSION, CONTOUR_EXTENSION, FLATTENED_EXTENSION

class App(QApplication):

    PART_IMPORT_LIMIT = 20 # limits for cad files
    ROUTER_LIMIT = 10
    PLATE_LIMIT = 50

    MIN_WIDTH = 1200
    MIN_HEIGHT = 1000
    APP_TITLE = 'NEXACut Pro'

    MENU_BUTTONS = [
        "Home", 
        "Import Part Files", 
        "Configure CNC Router", 
        "Manage Inventory", 
        "Generate Optimal Placement", 
        "Configure Preferences"]

    def __init__(self, argv):
        super().__init__(argv)

        self.file_processor = FileProcessor()

        atexit.register(self.__close_app)

        # long-term data
        self.user_preferences = self.get_user_preferences()
        self.router_data = self.get_router_data()
        self.plate_data = self.get_plate_data()

        # temporary data
        self.imported_files = []


    def get_user_preferences(self) -> dict:
        return self.file_processor.get_json_data(USER_PREFERENCE_FILE_PATH)
    
    def save_user_preferences(self):
        self.file_processor.save_json(USER_PREFERENCE_FILE_PATH, self.user_preferences)
    

    def get_router_data(self): 
        return self.file_processor.get_all_json_in_folder(ROUTER_DATA_FOLDER_PATH)
    
    def save_router_data(self): 
        self.file_processor.save_all_json_to_folder(self.router_data, ROUTER_DATA_FOLDER_PATH)


    def get_plate_data(self):
        return self.file_processor.get_all_json_in_folder(PLATE_DATA_FOLDER_PATH)
    
    def save_plate_data(self):
        self.file_processor.save_all_json_to_folder(self.plate_data, PLATE_DATA_FOLDER_PATH)

    def apply_stylesheet(self, widget: QWidget, stylesheet_file: str): # read stylesheet info from css

        stylesheet_path = os.path.join(STYLESHEET_FOLDER_PATH, stylesheet_file)

        if not os.path.exists(stylesheet_path):
            raise FileNotFoundError(f"Stylesheet file {stylesheet_path} does not exist")
        
        with open(stylesheet_path, 'r') as f:
            stylesheet = f.read()
            widget.setStyleSheet(stylesheet)
    
    def clear_temporary_data(self):
        for folder in [CAD_PREVIEW_DATA_PATH, IMAGE_PREVIEW_DATA_PATH]:
            self.file_processor.clear_folder_contents(folder)

    def __close_app(self):
        self.save_router_data()
        self.save_plate_data()
        self.save_user_preferences()
        self.clear_temporary_data()

class MainWindow(QMainWindow):

    def __init__(self, app_instance: App): # gives access to app data/methods without needing to directly inherit
        super().__init__()
        self.app = app_instance

        self.setWindowTitle(self.app.APP_TITLE)
        self.setMinimumSize(self.app.MIN_WIDTH, self.app.MIN_HEIGHT)
        QFontDatabase.addApplicationFont(FONT_PATH)
        self.__init_gui__()
    
    def __init_gui__(self):
        self.__layout = QHBoxLayout()
        self.__layout.setContentsMargins(0, 0, 0, 0) 
        self.__layout.setSpacing(0)

        self.__menu = Menu(self.app)
        self.__content_viewer = ContentViewer(self.app)

        self.__layout.addWidget(self.__menu, 2)
        self.__layout.addWidget(self.__content_viewer, 8)

        self.__widget = QWidget()
        self.__widget.setLayout(self.__layout)
        self.setCentralWidget(self.__widget)

        self.__menu.button_clicked.connect(self.__content_viewer.set_view) # changes view on button click

class Menu(QWidget):

    button_clicked = pyqtSignal(int)

    def __init__(self, app_instance: App):
        super().__init__()
        self.app = app_instance
        self.__init_gui__()

    def __init_gui__(self):

        self.app.apply_stylesheet(self, "window.css")
        self.__layout = QVBoxLayout()
        self.__layout.setContentsMargins(0, 0, 0, 0)
        self.__layout.setSpacing(0)

        buttons = self.app.MENU_BUTTONS

        for i, button_text in enumerate(buttons):
            button = QPushButton(button_text)
            self.app.apply_stylesheet(button, "generic-button.css")
            button.clicked.connect(lambda _, index=i: self.button_clicked.emit(index)) # button clicked boolean signal is ignored, sends button index
            self.__layout.addWidget(button, 1)

        self.__bottom_widget = QWidget() # purely for background
        self.app.apply_stylesheet(self.__bottom_widget, "light.css")

        self.__layout.addWidget(self.__bottom_widget, 10)
        self.setLayout(self.__layout)
    
class ContentViewer(QStackedWidget):

    def __init__(self, app_instance: App):
        super().__init__()
        self.app = app_instance
        self.__init_gui__()
    
    def __init_gui__(self):
        self.app.apply_stylesheet(self, "light.css")
        self.setCurrentIndex(0)
        self.__views = [
            HomeWidget(self.app),
            ImportWidget(self.app),
            RouterWidget(self.app),
            InventoryWidget(self.app)
        ]
        for widget in self.__views:
            self.addWidget(widget)

    def set_view(self, index: int):
        if 0 <= index < len(self.__views):
            self.setCurrentIndex(index)

class HomeWidget(QWidget):
    def __init__(self, app_instance: App):
        super().__init__()
        self.app = app_instance
        self.__init_gui__()

    def __init_gui__(self):
        self.__layout = QVBoxLayout()

        self.__logo_label = QLabel()
        script_path = os.path.dirname(__file__)
        logo_path = os.path.join(script_path, 'graphics', 'NEXACut Logo.png')
        pixmap = QPixmap(logo_path)
        scaled_pixmap = pixmap.scaled(1000, 500)
        self.__logo_label.setPixmap(scaled_pixmap)
        self.__logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.__app_description_label = QLabel("Version 0.0.0   Created by nagan__319")
        self.app.apply_stylesheet(self.__app_description_label, "small-text.css")

        self.__layout.addStretch()
        self.__layout.addWidget(self.__logo_label)
        self.__layout.addStretch()
        self.__layout.addWidget(self.__app_description_label)

        self.setLayout(self.__layout)

class WidgetTemplate(QWidget): # template for widgets with standard layout

    MARGIN_WIDTH = 1
    WIDGET_WIDTH = 68

    def __init__(self, app_instance: App):
        super().__init__()
        self.app = app_instance # can be accessed from child classes

    def __init_template_gui__(self, title_text: str, core_widget: QWidget): # called by child class after gui is configured

        self.__main_layout = QHBoxLayout()

        self.__content_widget = QWidget()
        self.__content_layout = QVBoxLayout()

        self.__title = QLabel(title_text)
        self.app.apply_stylesheet(self.__title, "title.css")
        self.__title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.__content_layout.addWidget(self.__title, 1)
        self.__content_layout.addWidget(core_widget, 9)
        self.__content_layout.addStretch(1)
        self.__content_widget.setLayout(self.__content_layout)

        self.__main_layout.addStretch(self.MARGIN_WIDTH)
        self.__main_layout.addWidget(self.__content_widget, self.WIDGET_WIDTH)
        self.__main_layout.addStretch(self.MARGIN_WIDTH)

        self.setLayout(self.__main_layout)

class ArrowButton(QPushButton):

    def __init__(self, app_instance: App, left_right: bool):
        super().__init__()
        self.app = app_instance
        if left_right:
            self.setText('>')
        else:
            self.setText('<')
        self.app.apply_stylesheet(self, 'small-button.css')

class WidgetViewer(QStackedWidget): # grid view

    MAX_WIDGETS_X = 4 # add proper index setting to avoid weird deletion
    MAX_WIDGETS_Y = 2

    def __init__(self, app_instance: App, widgets_x: int, widgets_y: int, widgets: list = []): # amount of objects in view 

        if widgets_x > self.MAX_WIDGETS_X or widgets_x <= 0:
            raise ValueError(f"widgets_x must be in range 0-{self.MAX_WIDGETS_X}")
        if widgets_y > self.MAX_WIDGETS_Y or widgets_y <= 0:    
            raise ValueError(f"widgets_y must be in range 0-{self.MAX_WIDGETS_Y}")

        super().__init__()

        self.app = app_instance
        self.widgets_x = widgets_x
        self.widgets_y = widgets_y

        self.curr_tab = 0
        self.widgets = widgets 
        
        self.update_view()

    def update_view(self):

        for i in reversed(range(self.count())):
            widget = self.widget(i)
            self.removeWidget(widget)

        for i in range(self._get_max_tab_idx()+1):
            widget = self.get_tab(i)
            self.addWidget(widget)

        self.setCurrentIndex(self.curr_tab)

    def append_widgets(self, widgets: list): 
        for widget in widgets:
            self.widgets.append(widget)
        self.update_view()

    def pop_widget(self, widget_idx: int):
        if widget_idx >= 0 and widget_idx < len(self.widgets):
            try: 
                self.widgets.pop(widget_idx)
                self.update_view()
            except Exception: # Avoids IndexError due to lag
                return

    def _get_max_tab_idx(self):
        return 0 if len(self.widgets) == 0 else math.ceil(len(self.widgets) / (self.widgets_x * self.widgets_y)) - 1
    
    def prev_tab(self):
        if self.curr_tab > 0:
            self.curr_tab -= 1
        self.update_view()

    def next_tab(self):
        if self.curr_tab < self._get_max_tab_idx():
            self.curr_tab += 1
        self.update_view()

    def get_tab(self, tab_idx: int) -> QWidget:

        if tab_idx < 0 or tab_idx > self._get_max_tab_idx():
            return

        min_widget_idx = tab_idx * self.widgets_x * self.widgets_y
        all_slots_used_max_idx = (tab_idx+1) * self.widgets_x * self.widgets_y 
        max_widget_idx = all_slots_used_max_idx if all_slots_used_max_idx < len(self.widgets) else len(self.widgets) - 1

        main_widget = QWidget()
        main_layout = QHBoxLayout() # includes left/right arrow keys if relevant, applied to 'self'

        if tab_idx > 0:
            left_arrow = ArrowButton(self.app, False)
            left_arrow.pressed.connect(self.prev_tab)
            main_layout.addWidget(left_arrow, 1)
        else:
            main_layout.addStretch(1)

        view_widget = self._get_tab_central_widget(min_widget_idx, max_widget_idx)
        main_layout.addWidget(view_widget, 18)

        if tab_idx < self._get_max_tab_idx():
            right_arrow = ArrowButton(self.app, True)
            right_arrow.pressed.connect(self.next_tab)
            main_layout.addWidget(right_arrow, 1)
        else:
            main_layout.addStretch(1)

        main_widget.setLayout(main_layout)

        return main_widget

    def _get_tab_central_widget(self, min_widget_idx: int, max_widget_idx: int) -> QWidget:

        view_widget = QWidget()
        view_layout = QVBoxLayout()

        for i in range(self.widgets_y):

            row_widget = QWidget()
            row_widget.setMinimumHeight(int(self.app.MIN_HEIGHT*.8/self.widgets_y))
            self.app.apply_stylesheet(row_widget, "light.css")
            row_widget_layout = QHBoxLayout()

            for j in range(self.widgets_x):

                curr_widget_idx = min_widget_idx + i*self.widgets_x + j

                if curr_widget_idx > max_widget_idx:
                    row_widget_layout.addStretch(1)

                else: # add widget from widgets list
                    curr_widget = self.widgets[curr_widget_idx]
                    row_widget_layout.addWidget(curr_widget, 1)
            
            row_widget.setLayout(row_widget_layout)
            view_layout.addWidget(row_widget, 1)
        
        view_widget.setLayout(view_layout)

        return view_widget

class STLFileWidget(QWidget): 
    
    deleteRequested = pyqtSignal(str)
    amountEdited = pyqtSignal(str, int)

    def __init__(self, app_instance: App, file_name: str, png_location: str):

        super().__init__()

        self.app = app_instance
        self.file_name = file_name
        self.png_location = png_location

        layout = QVBoxLayout()

        preview_widget = QLabel()
        preview_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_image = QPixmap(self.png_location)
        preview_widget.setPixmap(preview_image)

        bottom_widget = self._get_bottom_widget()

        layout.addWidget(preview_widget, 5)
        layout.addWidget(bottom_widget, 1)
        self.setLayout(layout)

    def _get_bottom_widget(self) -> QWidget:
        bottom_widget = QWidget()
        bottom_widget_layout = QHBoxLayout()

        amt_input = QLineEdit()
        amt_input.setPlaceholderText("Amount")
        self.app.apply_stylesheet(amt_input, 'small-input-box.css')
        amt_input.textEdited.connect(self.on_amount_edited)
        amt_input.setText("1")

        delete_button = QPushButton("Delete")
        self.app.apply_stylesheet(delete_button, 'small-button.css')
        delete_button.pressed.connect(self.on_delete_button_clicked) 

        bottom_widget_layout.addStretch(2)
        bottom_widget_layout.addWidget(amt_input, 1)
        bottom_widget_layout.addWidget(delete_button, 1)
        bottom_widget_layout.addStretch(2)
        bottom_widget.setLayout(bottom_widget_layout)
        return bottom_widget

    def on_delete_button_clicked(self):
        self.deleteRequested.emit(self.file_name)

    def on_amount_edited(self, new_text):
        try:
            new_amount = int(new_text)
            self.amountEdited.emit(self.file_name, new_amount) 
        except ValueError:
            pass

class ImportWidget(WidgetTemplate):

    def __init__(self, app_instance: App):
        super().__init__(app_instance)
        self.__init_gui__()
    
    def __init_gui__(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        self.__file_preview_widget = WidgetViewer(self.app, 4, 2) 

        self.__import_button_wrapper = QWidget()
        self.__import_button_wrapper_layout = QHBoxLayout()

        self.__import_button = QPushButton()
        self.app.apply_stylesheet(self.__import_button, "generic-button.css")
        self.__import_button.clicked.connect(self.import_files)
        self.update_import_button_text()

        self.__import_button_wrapper_layout.addStretch(2)
        self.__import_button_wrapper_layout.addWidget(self.__import_button, 1)
        self.__import_button_wrapper_layout.addStretch(2)
        self.__import_button_wrapper.setLayout(self.__import_button_wrapper_layout)

        main_layout.addWidget(self.__file_preview_widget, 7)
        main_layout.addWidget(self.__import_button_wrapper, 1)
        main_widget.setLayout(main_layout)

        self.app.apply_stylesheet(main_widget, "light.css")

        self.__init_template_gui__("Import Part Files", main_widget)

    def _get_total_part_amount(self) -> int:
        total = 0
        for file in self.app.imported_files:
            try:
                total += file['amount']
            except Exception:
                continue
        return total
    
    def _get_idx_of_filename(self, filename: str):
        for idx, dict in enumerate(self.app.imported_files):
            if dict['filename'] == filename: 
                return idx
        return -1
    
    def _save_file_to_data(self, filename: str, outer_contour: list, amount: int = 1):
        new_entry = {
            "filename": filename, 
            "amount": amount, 
            "outer_contour": outer_contour}
        self.app.imported_files.append(new_entry)

    def import_files(self): 

        if self._get_total_part_amount() >= self.app.PART_IMPORT_LIMIT:
            return

        IMPORT_LIMIT = 10 
        
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select File", "", "STL Files (*.stl)")

        widgets = []

        imported = 0

        for path in file_paths:

            if imported >= IMPORT_LIMIT:
                break
            if self._get_total_part_amount() >= self.app.PART_IMPORT_LIMIT:
                break
                
            file_name = os.path.basename(path)

            duplicate = False

            for file in self.app.imported_files:
                if file["filename"] == file_name:
                    duplicate = True

            if duplicate: 
                continue

            try:
                parser = STLParser(path, CAD_PREVIEW_DATA_PATH)
                parser.save_preview_image()
                outer_contour = parser.outer_contour
                png_location = parser.preview_path

                preview_widget = STLFileWidget(self.app, file_name, png_location)
                preview_widget.deleteRequested.connect(self.on_widget_delete_request)
                preview_widget.amountEdited.connect(self.on_widget_amt_edited)
                widgets.append(preview_widget)

                self._save_file_to_data(file_name, outer_contour, 1) 

            except Exception as e:
                continue

            imported += 1

        self.__file_preview_widget.append_widgets(widgets)
        self.update_import_button_text()

    def update_import_button_text(self):
        if self._get_total_part_amount() >= self.app.PART_IMPORT_LIMIT:
            self.app.apply_stylesheet(self.__import_button, "generic-button-red.css")
        else:
            self.app.apply_stylesheet(self.__import_button, "generic-button.css")
        self.__import_button.setText(f"Import Parts ({self._get_total_part_amount()}/{self.app.PART_IMPORT_LIMIT})")

    def on_widget_amt_edited(self, filename: str, value: int): 
        index = self._get_idx_of_filename(filename)
        self.app.imported_files[index]['amount'] = value
        self.update_import_button_text()

    def on_widget_delete_request(self, filename: str):
        index = self._get_idx_of_filename(filename)
        self.app.imported_files.pop(index)
        self.__file_preview_widget.pop_widget(index)
        self.update_import_button_text()

class RouterFileWidget(QWidget): 
    
    deleteRequested = pyqtSignal(str) 

    def __init__(self, app_instance: App, router_util: RouterUtil, router_data: dict): 

        super().__init__()

        self.app = app_instance
        self.router_util = router_util
        self.data = router_data 

        layout = QHBoxLayout()

        self.data_widget = DataWidget(self.app, self.data, self.router_util.editable_keys, self.router_util.value_ranges, True, False)
        self.data_widget.deleteRequested.connect(self.on_delete_requested)
        self.data_widget.saveRequested.connect(self.on_save_requested)

        self.preview_widget = PreviewWidget(self.data['preview_path'])

        layout.addWidget(self.data_widget, 5)
        layout.addWidget(self.preview_widget, 4)
        self.setLayout(layout)

    def on_save_requested(self, data):
        self.data = data
        self._update_preview()

    def on_delete_requested(self):
        self.deleteRequested.emit(self.data['filename'])

    def _update_preview(self):
        self.router_util.save_router_preview(self.data)
        self.preview_widget.update()

class RouterWidget(WidgetTemplate):

    def __init__(self, app_instance: App):
        super().__init__(app_instance)

        self.router_util = RouterUtil(ROUTER_PREVIEW_DATA_PATH)

        self.__init_gui__()
        self.__init_timeout__()

    def __init_gui__(self):

        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        router_widgets = [RouterFileWidget(self.app, self.router_util, router) for router in self.app.router_data]

        for widget in router_widgets:
            widget.deleteRequested.connect(self.on_router_delete_requested)

        self.__file_preview_widget = WidgetViewer(self.app, 1, 1, router_widgets) 

        self.__add_new_button_wrapper = QWidget()
        self.__add_new_button_wrapper_layout = QHBoxLayout()

        self.__add_new_button = QPushButton()
        self.app.apply_stylesheet(self.__add_new_button, "generic-button.css")
        self.__add_new_button.clicked.connect(self.add_new_router)

        self.__add_new_button_wrapper_layout.addStretch(2)
        self.__add_new_button_wrapper_layout.addWidget(self.__add_new_button, 1)
        self.__add_new_button_wrapper_layout.addStretch(2)
        self.__add_new_button_wrapper.setLayout(self.__add_new_button_wrapper_layout)

        main_layout.addWidget(self.__file_preview_widget, 7)
        main_layout.addWidget(self.__add_new_button_wrapper, 1)
        main_widget.setLayout(main_layout)

        self.app.apply_stylesheet(main_widget, "light.css")

        self.__init_template_gui__("Configure CNC Router", main_widget)
        self.update_add_button_text()

    def __init_timeout__(self):
        self.timeout = False

    def _get_router_amount(self) -> int:
        return len(self.app.router_data) 

    def add_new_router(self):
        if self.timeout:
            return

        self.timeout = True
        if self._get_router_amount() < self.app.ROUTER_LIMIT:
            new_router_data = self.router_util.get_new_router(self.app.router_data)
            self.app.router_data.append(new_router_data)
            
            self.router_util.save_router_preview(new_router_data)

            new_router_widget = RouterFileWidget(self.app, self.router_util, new_router_data)
            new_router_widget.deleteRequested.connect(self.on_router_delete_requested)

            self.__file_preview_widget.append_widgets([new_router_widget])
            self.update_add_button_text() 
        self.timeout = False

    def update_add_button_text(self):
        if self._get_router_amount() >= self.app.ROUTER_LIMIT:
            self.app.apply_stylesheet(self.__add_new_button, "generic-button-red.css")
        else:
            self.app.apply_stylesheet(self.__add_new_button, "generic-button.css")
        self.__add_new_button.setText(f"Add New ({self._get_router_amount()}/{self.app.ROUTER_LIMIT})")

    def _get_idx_of_filename(self, filename: str):
        for idx, dict in enumerate(self.app.router_data):
            if dict['filename'] == filename: 
                return idx
        return -1

    def on_router_delete_requested(self, filename: str):
        if self.timeout:
            return
    
        self.timeout = True
        index = self._get_idx_of_filename(filename)
        self.app.file_processor.delete_file(self.app.router_data[index]['preview_path'])
        self.app.router_data.pop(index)
        self.__file_preview_widget.pop_widget(index)
        self.update_add_button_text()
        self.timeout = False

class PreviewWidget(QLabel):

    def __init__(self, png_path: str):

        if not os.path.exists(png_path): 
            raise ValueError("Attempted to create preview widget with invalid file ")

        super().__init__()
        
        self.png_path = png_path
        self.pixmap = QPixmap(self.png_path)
        self.setPixmap(self.pixmap)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def update(self):
        self.pixmap = QPixmap(self.png_path)
        self.setPixmap(self.pixmap)

class DataWidget(QWidget):

    deleteRequested = pyqtSignal() 
    saveRequested = pyqtSignal(dict) # data

    def __init__(self, app_instance: App, data: dict, editable_keys: list, value_ranges: list, has_name_property: False, is_small: False):

        if len(value_ranges) != len(editable_keys):
            raise ValueError("Each editable key must have a corresponding value range")
        
        if has_name_property and 'name' not in data.keys():
            raise ValueError("Data must include name property")

        super().__init__()

        if is_small:
            self.button_stylesheet = 'small-button.css'
            self.text_stylesheet = 'small-text.css'
            self.key_val_ratio = (3, 2)
        else:
            self.button_stylesheet = 'generic-button.css'
            self.text_stylesheet = 'generic-text.css'
            self.key_val_ratio = (3, 1)

        self.app = app_instance
        self.data = data
        self.editable_keys = editable_keys
        self.value_ranges = value_ranges

        layout = QVBoxLayout()

        if has_name_property:
            name_widget = QLineEdit()
            name_widget.setText(self.data['name'])
            self.app.apply_stylesheet(name_widget, "data-title-input-box.css")
            name_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            name_widget.editingFinished.connect(lambda box=name_widget: self.on_name_edited(box.text()))

            layout.addWidget(name_widget)

        for key in self.editable_keys:
            data_row_widget = self._get_data_row_widget(key, self.data[key])
            layout.addWidget(data_row_widget)
        
        button_container = QWidget()
        button_container_layout = QHBoxLayout()

        save_button = QPushButton("Save")
        self.app.apply_stylesheet(save_button, self.button_stylesheet)
        save_button.pressed.connect(self.on_save_requested)

        delete_button = QPushButton("Delete")
        self.app.apply_stylesheet(delete_button, self.button_stylesheet)
        delete_button.pressed.connect(self.on_delete_requested)

        button_container_layout.addStretch(1)
        button_container_layout.addWidget(save_button, 2)
        button_container_layout.addWidget(delete_button, 2)
        button_container_layout.addStretch(1)

        button_container.setLayout(button_container_layout)

        layout.addWidget(button_container)
        self.setLayout(layout)

    def _get_data_row_widget(self, key: str, value: float) -> QWidget:

        data_row_widget = QWidget()
        data_row_layout = QHBoxLayout()

        key_label = QLabel()
        key_text = self._edit_key_text(key)
        key_label.setText(key_text)
        self.app.apply_stylesheet(key_label, self.text_stylesheet)

        value_box = QLineEdit()
        value_box.setText(str(value))
        value_box.editingFinished.connect(lambda key=key, box=value_box: self.on_value_edited(box.text(), key, box))
        if type(self.value_ranges[key]) == tuple and self.value_ranges[key] is not None: 
            min_value, max_value = self.value_ranges[key]
            value_box.setPlaceholderText(f"{min_value}-{max_value}")
        else:
            value_box.setPlaceholderText(f"")
        self.app.apply_stylesheet(value_box, "small-input-box.css")
  
        data_row_layout.addWidget(key_label, self.key_val_ratio[0])
        data_row_layout.addWidget(value_box, self.key_val_ratio[1])
        data_row_widget.setLayout(data_row_layout)

        return data_row_widget

    def _edit_key_text(self, str: str):
        words = str.split("_")
        for i, word in enumerate(words):
            words[i] = word.capitalize()     
        return " ".join(words)

    def on_name_edited(self, text: str):
        self.data['name'] = text

    def on_value_edited(self, string: str, key_edited: str, box: QLineEdit):
        
        if string == str(self.data[key_edited]):
            return
        
        if self.value_ranges[key_edited]:
            min, max = self.value_ranges[key_edited]
            value = parse_text(string, min, max)
        else:
            value = parse_text(string)

        if value is not None:
            box.setText(str(value))
            self.data[key_edited] = value

    def on_save_requested(self):
        self.saveRequested.emit(self.data)

    def on_delete_requested(self):
        self.deleteRequested.emit()

class PlateFileWidget(QWidget):

    deleteRequested = pyqtSignal(str)
    importRequested = pyqtSignal(str)

    def __init__(self, app_instance: App, plate_util: PlateUtil, data: dict):
        super().__init__()

        self.app = app_instance
        self.plate_util = plate_util
        self.data = data

        layout = QVBoxLayout()

        self.preview_widget = PreviewWidget(self.data['preview_path'])

        self.img_button_container = QWidget()
        self.img_button_container_layout = QHBoxLayout()
        self.img_button = QPushButton("Import Image")
        self.img_button.pressed.connect(self.on_import_requested)
        self.app.apply_stylesheet(self.img_button, 'small-button.css')
        self.img_button_container_layout.addStretch(1)
        self.img_button_container_layout.addWidget(self.img_button, 2)
        self.img_button_container_layout.addStretch(1)
        self.img_button_container.setLayout(self.img_button_container_layout)

        self.data_widget = DataWidget(self.app, self.data, self.plate_util.editable_keys, self.plate_util.value_ranges, False, True)
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

class InventoryWidget(WidgetTemplate):

    def __init__(self, app_instance: App):
        super().__init__(app_instance)

        self.plate_util = PlateUtil(PLATE_DATA_PREVIEW_FOLDER_PATH)

        self.image_editor_active = False

        self.__init_gui__()
        self.__init_timeout__()

    def __init_gui__(self):

        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        plate_widgets = [PlateFileWidget(self.app, self.plate_util, plate) for plate in self.app.plate_data]

        for widget in plate_widgets:
            widget.deleteRequested.connect(self.on_plate_delete_requested)
            widget.importRequested.connect(self.on_plate_import_image_requested)

        self.__file_preview_widget = WidgetViewer(self.app, 3, 1, plate_widgets) 

        self.__add_new_button_wrapper = QWidget()
        self.__add_new_button_wrapper_layout = QHBoxLayout()

        self.__add_new_button = QPushButton()
        self.app.apply_stylesheet(self.__add_new_button, "generic-button.css")
        self.__add_new_button.clicked.connect(self.add_new_plate)

        self.__add_new_button_wrapper_layout.addStretch(2)
        self.__add_new_button_wrapper_layout.addWidget(self.__add_new_button, 1)
        self.__add_new_button_wrapper_layout.addStretch(2)
        self.__add_new_button_wrapper.setLayout(self.__add_new_button_wrapper_layout)

        main_layout.addWidget(self.__file_preview_widget, 7)
        main_layout.addWidget(self.__add_new_button_wrapper, 1)
        main_widget.setLayout(main_layout)

        self.app.apply_stylesheet(main_widget, "light.css")

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

            new_plate_widget = PlateFileWidget(self.app, self.plate_util, new_plate_data)
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

    def _create_image_edit_window(self, filename: str):
        
        plate_idx = self._get_idx_of_filename(filename)
        plate_dimensions = tuple([self.app.plate_data[plate_idx][key] for key in ['width_(x)', 'height_(y)', 'thickness_(z)']])

        self.image_converter = ImageConverter(IMAGE_PREVIEW_DATA_PATH, plate_dimensions)

        self.image_editor = ImageEditorWindow(self.app, self.image_converter) # necessary to keep reference to prevent immediate closure
        self.image_editor.imageEditorClosed.connect(self.on_image_editor_closed)

    def on_image_editor_closed(self):
        self.image_editor_active = False

class ImageEditorWindow(QMainWindow):
    
    MIN_HEIGHT = 800
    MIN_WIDTH = 800
    WINDOW_TITLE = 'Attach Image File'

    imageEditorClosed = pyqtSignal()

    def __init__(self, app_instance: App, image_converter_instance: ImageConverter):
        super().__init__()

        self.app = app_instance
        self.image_converter = image_converter_instance

        self.setMinimumSize(self.MIN_WIDTH, self.MIN_HEIGHT)
        self.setWindowTitle(self.WINDOW_TITLE)

        self.__init_gui__()
    
    def __init_gui__(self):
        self.__layout = QVBoxLayout()
        self.__layout.setContentsMargins(0, 0, 0, 0) 
        self.__layout.setSpacing(0)
        self.image_editor = ImageEditorWidget(self.app, self.image_converter)
        self.__layout.addWidget(self.image_editor)
        self.__widget = QWidget()
        self.__widget.setLayout(self.__layout)
        self.setCentralWidget(self.__widget)
        self.show()

    def closeEvent(self, event):
        print()
        self.imageEditorClosed.emit()

class ImageEditorWidget(QStackedWidget):

    def __init__(self, app_instance: App, image_converter_instance: ImageConverter):
        super().__init__()
        self.app = app_instance
        self.image_converter = image_converter_instance
        self.__init_gui__()

    def __init_gui__(self):

        self.app.apply_stylesheet(self, 'light.css')

        self.setCurrentIndex(0)

        params = (self.app, self.image_converter)

        self.image_load_widget = ImageLoadWidget(*params)
        self.image_load_widget.imageImported.connect(self.on_image_imported)

        self.image_threshold_widget = ImageThresholdWidget(*params)
        self.image_threshold_widget.binaryFinalized.connect(self.on_binary_finalized)

        self.image_feature_widget = ImageFeatureWidget(*params)
        self.image_feature_widget.featuresFinalized.connect(self.on_features_finalized)

        for widget in [
            self.image_load_widget, 
            self.image_threshold_widget,
            self.image_feature_widget]:
            self.addWidget(widget)

    def on_image_imported(self):
        self.setCurrentIndex(1)
        self.image_threshold_widget.update_preview()
    
    def on_binary_finalized(self):
        self.setCurrentIndex(2)
        self.image_converter.get_contours_from_binary()
        self.image_feature_widget.update_preview()

    def on_features_finalized(self):
        self.setCurrentIndex(3)
    
class ImageLoadWidget(QWidget):

    imageImported = pyqtSignal()

    def __init__(self, app_instance: App, image_converter_instance: ImageConverter):
        super().__init__()
        self.app = app_instance
        self.image_converter = image_converter_instance
        self.__init_gui__()
    
    def __init_gui__(self):
        self.main_layout = QVBoxLayout()

        self.button_frame = QWidget()
        self.button_frame_layout = QHBoxLayout()
        self.import_button = QPushButton("Import Image File")
        self.app.apply_stylesheet(self.import_button, 'generic-button.css')
        self.import_button.pressed.connect(self.import_image_file)

        self.button_frame_layout.addStretch(2)
        self.button_frame_layout.addWidget(self.import_button, 1)
        self.button_frame_layout.addStretch(2)
        self.button_frame.setLayout(self.button_frame_layout)

        self.main_layout.addStretch(3)
        self.main_layout.addWidget(self.button_frame, 1)
        self.main_layout.addStretch(3)

        self.setLayout(self.main_layout)

    def import_image_file(self):
 
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", SUPPORTED_IMAGE_FORMATS)
        self.image_converter.save_external_image_as_raw(file_path)
        self.imageImported.emit()

class ImageThresholdWidget(QWidget):

    binaryFinalized = pyqtSignal()

    COLOR_MIN = 0
    COLOR_MAX = 255
    COLOR_MID = (COLOR_MIN + COLOR_MAX)//2

    def __init__(self, app_instance: App, image_converter_instance: ImageConverter):
        super().__init__()

        self.app = app_instance
        self.image_converter = image_converter_instance
        
        self.threshold = self.COLOR_MID

        self.__init_gui__()

    def __init_gui__(self):
        self.layout_with_margins = QHBoxLayout()

        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout()

        self.preview_widget = QLabel()
        self.preview_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.slider_label = QLabel("Adjust Threshold Value")
        self.slider_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.app.apply_stylesheet(self.slider_label, 'small-text.css')

        self.slider = QSlider()
        self.slider.setOrientation(Qt.Orientation.Horizontal) 
        self.slider.setMinimum(self.COLOR_MIN)
        self.slider.setMaximum(self.COLOR_MAX)
        self.slider.setValue(self.COLOR_MID)

        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)  
        self.slider.setTickInterval(16)

        self.slider.valueChanged.connect(self.on_threshold_parameter_edited)

        self.save_button_wrapper = QWidget()
        self.save_button_wrapper_layout = QHBoxLayout()
        self.save_button = QPushButton("Save Binary")
        self.save_button.pressed.connect(self.on_save_button_pressed)
        self.app.apply_stylesheet(self.save_button, 'small-button.css')

        self.save_button_wrapper_layout.addStretch(2)
        self.save_button_wrapper_layout.addWidget(self.save_button, 1)
        self.save_button_wrapper_layout.addStretch(2)
        self.save_button_wrapper.setLayout(self.save_button_wrapper_layout)

        self.main_layout.addWidget(self.preview_widget, 3)
        self.main_layout.addWidget(self.slider_label, 0)
        self.main_layout.addWidget(self.slider, 1)
        self.main_layout.addWidget(self.save_button_wrapper, 0)
        self.main_widget.setLayout(self.main_layout)

        self.layout_with_margins.addStretch(1)
        self.layout_with_margins.addWidget(self.main_widget, 5)
        self.layout_with_margins.addStretch(1)

        self.setLayout(self.layout_with_margins)

    def _generate_binary(self):
        self.image_converter.save_binary_image(self.threshold)

    def update_preview(self):
        self._generate_binary()
        binary_path = os.path.join(IMAGE_PREVIEW_DATA_PATH, BINARY_EXTENSION)
        pixmap = QPixmap(binary_path)
        scaled_pixmap = pixmap.scaledToHeight(600)
        self.preview_widget.setPixmap(scaled_pixmap)
    
    def on_threshold_parameter_edited(self, value: int):
        self.threshold = value
        self.update_preview()

    def on_save_button_pressed(self):
        self.binaryFinalized.emit()

class ImageFeatureWidget(QWidget):

    featuresFinalized = pyqtSignal()

    def __init__(self, app_instance: App, image_converter_instance: ImageConverter):
        super().__init__()

        self.app = app_instance
        self.image_converter = image_converter_instance

        self.__init_gui__()
    
    def __init_gui__(self):
        
        self.layout_with_margins = QHBoxLayout()

        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout()

        self.preview_widget = QLabel()
        self.preview_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.save_button_wrapper = QWidget()
        self.save_button_wrapper_layout = QHBoxLayout()
        self.save_button = QPushButton("Save Features")
        self.save_button.pressed.connect(self.on_save_button_pressed)
        self.app.apply_stylesheet(self.save_button, 'small-button.css')

        self.save_button_wrapper_layout.addStretch(2)
        self.save_button_wrapper_layout.addWidget(self.save_button, 1)
        self.save_button_wrapper_layout.addStretch(2)
        self.save_button_wrapper.setLayout(self.save_button_wrapper_layout)

        self.main_layout.addWidget(self.preview_widget, 3)
        self.main_layout.addWidget(self.save_button_wrapper, 0)
        self.main_widget.setLayout(self.main_layout)

        self.layout_with_margins.addStretch(1)
        self.layout_with_margins.addWidget(self.main_widget, 5)
        self.layout_with_margins.addStretch(1)

        self.setLayout(self.layout_with_margins)

    def _generate_contour_img(self):
        self.image_converter.save_contour_image()

    def update_preview(self):
        self._generate_contour_img()
        contour_path = os.path.join(IMAGE_PREVIEW_DATA_PATH, CONTOUR_EXTENSION)
        pixmap = QPixmap(contour_path)
        scaled_pixmap = pixmap.scaledToHeight(600)
        self.preview_widget.setPixmap(scaled_pixmap)

    def on_save_button_pressed(self):
        self.featuresFinalized.emit()

if __name__ == '__main__':
    app = App(sys.argv)
    main_window = MainWindow(app)
    main_window.show()
    sys.exit(app.exec())
