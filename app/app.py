import sys
import os
import shutil
import json
import atexit
import copy
import math

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QStackedWidget, QFileDialog, QButtonGroup, QComboBox, QLineEdit
from PyQt6.QtGui import QPixmap, QFontDatabase, QPalette, QBrush

from filepaths import * # paths to data folders

from utils.stl_parser import STLParser
from utils.router_util import RouterUtil
from utils.value_conversion import parse_text

# (almost) all file io is handled in app class, methods are called by widget classes
# one exception is matplotlib-related image saving which is handled by util classes with dst passed in 
class App(QApplication):

    PART_IMPORT_LIMIT = 20 # limits for cad files
    ROUTER_LIMIT = 10

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
        atexit.register(self.__close_app)

        # long-term data
        self.user_preferences = self.load_user_preferences()
        self.router_data = self.load_router_data()

        # temporary data
        self.imported_files = []
        
    def load_user_preferences(self) -> dict:
        return self.read_json(USER_PREFERENCE_FILE_PATH)
    
    def save_user_preferences(self):
        self.save_json(USER_PREFERENCE_FILE_PATH, self.user_preferences)
    
    def load_router_data(self): 

        router_data = []

        all_routers = self.load_folder_contents(ROUTER_DATA_FOLDER_PATH)

        for router in all_routers:
            router_path = os.path.join(ROUTER_DATA_FOLDER_PATH, router)
            router_data.append(self.read_json(router_path))

        return router_data
    
    def save_router_data(self): 
        
        self.clear_folder_contents(ROUTER_DATA_FOLDER_PATH)

        for i, _ in enumerate(self.router_data):
            filename = self.router_data[i]['filename']
            filepath = os.path.join(ROUTER_DATA_FOLDER_PATH, filename)
            self.save_json(filepath, self.router_data[i])

    def clear_temporary_data(self):
        for folder in [CAD_PREVIEW_DATA_PATH, IMAGE_PREVIEW_DATA_PATH, ROUTER_PREVIEW_DATA_PATH]:
            self.clear_folder_contents(folder)

    def __close_app(self):
        self.save_router_data()
        self.save_user_preferences()
        self.clear_temporary_data()

    def apply_stylesheet(self, widget: QWidget, stylesheet_file: str): # read stylesheet info from css

        stylesheet_path = os.path.join(STYLESHEET_FOLDER_PATH, stylesheet_file)

        if not os.path.exists(stylesheet_path):
            raise FileNotFoundError(f"Stylesheet file {stylesheet_path} does not exist")
        
        with open(stylesheet_path, 'r') as f:
            stylesheet = f.read()
            widget.setStyleSheet(stylesheet)

    def load_folder_contents(self, filepath: str): # get filenames in folder

        if not os.path.exists(filepath):
            return []
        
        return os.listdir(filepath)
    
    def clear_folder_contents(self, dirpath: str, *exceptions: str): # clears directory except certain files

        if not os.path.exists(dirpath):
            return
        
        for filename in os.listdir(dirpath):
            if filename not in exceptions:
                filepath = os.path.join(dirpath, filename)
                os.remove(filepath)
    
    def copy_file(self, src_path: str, dst_path: str): # copies a to b

        if not (os.path.exists(src_path) or os.path.exists(dst_path)):
            return
        
        os.remove(dst_path)
        shutil.copyfile(src_path, dst_path)

    def read_json(self, filepath: str): # extract data from json

        if not os.path.exists(filepath):
            return 
        
        if os.path.splitext(filepath)[1].lower() != '.json':
            return
        
        with open(filepath, 'r') as file:
            data = json.load(file)
        
        return data
    
    def save_json(self, filepath: str, data: dict): # saves dict to json
        
        if os.path.splitext(filepath)[1].lower() != '.json':
            return

        with open(filepath, 'w') as file:
            json.dump(data, file, indent=4)

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
            RouterWidget(self.app)
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

class WidgetTemplate(QWidget): # template for widgets with standard layout (widgets inherit from this but can also access app)

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

class WidgetViewer(QStackedWidget): # image viewing 'carousel' (basically grid view)

    MAX_WIDGETS_X = 4
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
        self.main_data = router_data
        self.temp_data = copy.deepcopy(self.main_data)

        layout = QHBoxLayout()

        self.data_widget = self._get_data_widget()
        self.preview_widget = self._get_preview_widget()

        layout.addWidget(self.data_widget, 5)
        layout.addWidget(self.preview_widget, 4)
        self.setLayout(layout)

    def _get_data_widget(self) -> QWidget:

        data_widget = QWidget()
        data_layout = QVBoxLayout()

        router_name_widget = QLineEdit()
        router_name_widget.setText(self.temp_data['name'])
        self.app.apply_stylesheet(router_name_widget, "router-title-input-box.css")
        router_name_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        router_name_widget.editingFinished.connect(lambda box=router_name_widget: self.on_name_edited(box.text()))

        data_layout.addWidget(router_name_widget)

        key_list = self.router_util.editable_key_list

        for key in key_list:
            data_row_widget = self._get_data_row_widget(key, self.temp_data[key])
            data_layout.addWidget(data_row_widget)
        
        button_container = QWidget()
        button_container_layout = QHBoxLayout()

        save_button = QPushButton("Save")
        self.app.apply_stylesheet(save_button, "generic-button.css")
        save_button.pressed.connect(self.on_save_requested)

        delete_button = QPushButton("Delete")
        self.app.apply_stylesheet(delete_button, "generic-button.css")
        delete_button.pressed.connect(self.on_delete_requested)

        button_container_layout.addStretch(1)
        button_container_layout.addWidget(save_button, 2)
        button_container_layout.addWidget(delete_button, 2)
        button_container_layout.addStretch(1)

        button_container.setLayout(button_container_layout)

        data_layout.addWidget(button_container)
        data_widget.setLayout(data_layout)
        
        return data_widget

    def _get_data_row_widget(self, key: str, value: float) -> QWidget:

        data_row_widget = QWidget()
        data_row_layout = QHBoxLayout()

        key_label = QLabel()
        key_text = self._edit_key_text(key)
        key_label.setText(key_text)
        self.app.apply_stylesheet(key_label, "generic-text.css")

        value_box = QLineEdit()
        value_box.setText(str(value))
        value_box.editingFinished.connect(lambda key=key, box=value_box: self.on_value_edited(box.text(), key, box))
        min_value, max_value = self.router_util.value_ranges[key]
        value_box.setPlaceholderText(f"{min_value}-{max_value}")
        self.app.apply_stylesheet(value_box, "small-input-box.css")

        data_row_layout.addWidget(key_label, 3)
        data_row_layout.addWidget(value_box, 1)
        data_row_widget.setLayout(data_row_layout)

        return data_row_widget

    def _edit_key_text(self, str: str):
        words = str.split("_")
        for i, word in enumerate(words):
            words[i] = word.capitalize()     
        return " ".join(words)

    def _get_preview_widget(self):
        router_preview_widget = QLabel()
        self.router_util.get_router_preview(self.temp_data)
        png_path = self.temp_data['preview_path']
        pixmap = QPixmap(png_path)
        router_preview_widget.setPixmap(pixmap)
        router_preview_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)

        return router_preview_widget

    def on_name_edited(self, text: str):
        self.temp_data['name'] = text

    def on_value_edited(self, string: str, key_edited: str, box: QLineEdit):
        
        if string == str(self.temp_data[key_edited]):
            return
        
        min, max = self.router_util.value_ranges[key_edited]
        value = parse_text(string, min, max)

        if value is not None:
            box.setText(str(value))
            self.temp_data[key_edited] = value

    def on_save_requested(self):
        self._update_preview()
        self.main_data = self.temp_data

    def on_delete_requested(self):
        self.deleteRequested.emit(self.temp_data['filename'])

    def _update_preview(self):
        self.router_util.get_router_preview(self.temp_data)
        png_path = self.temp_data['preview_path']
        pixmap = QPixmap(png_path)
        self.preview_widget.setPixmap(pixmap)

class RouterWidget(WidgetTemplate):

    def __init__(self, app_instance: App):
        super().__init__(app_instance)

        self.router_util = RouterUtil(ROUTER_PREVIEW_DATA_PATH)

        self.__init_gui__()

    def __init_gui__(self):

        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        router_widgets = [RouterFileWidget(self.app, self.router_util, router) for router in self.app.router_data]

        for widget in router_widgets:
            widget.deleteRequested.connect(self.on_widget_delete_requested)

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

    def _get_router_amount(self) -> int:
        return(len(self.app.router_data))

    def add_new_router(self):
        if self._get_router_amount() < self.app.ROUTER_LIMIT:
            new_router_data = self.router_util.get_new_router(self.app.router_data)
            self.app.router_data.append(new_router_data)
            
            new_router_widget = RouterFileWidget(self.app, self.router_util, new_router_data)
            new_router_widget.deleteRequested.connect(self.on_widget_delete_requested)

            self.__file_preview_widget.append_widgets([new_router_widget])
            self.update_add_button_text() 

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

    def on_widget_delete_requested(self, filename: str):
        index = self._get_idx_of_filename(filename)
        self.app.router_data.pop(index)
        self.__file_preview_widget.pop_widget(index)
        self.update_add_button_text()

if __name__ == '__main__':
    app = App(sys.argv)
    main_window = MainWindow(app)
    main_window.show()
    sys.exit(app.exec())
