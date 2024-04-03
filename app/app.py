import sys
import os
import json
import atexit

from functools import partial
from collections import defaultdict

from PyQt6.QtCore import Qt, pyqtSignal, QFile, QTextStream
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QStackedWidget, QFileDialog, QButtonGroup, QComboBox, QLineEdit, QMessageBox, QFrame
from PyQt6.QtGui import QPixmap

from filepaths import *

from utils.pref_mgr import PreferenceManager
from utils.router_mgr import RouterManager
from app.utils.cad_to_svg import CADToSVG

MAX_RES = 4

# todo: fix preference menu always showing default values on startup
#       create stl save json
#       make router editing more clean, review functionality
#       add inventory view

MIN_WIDTH, MIN_HEIGHT = 1600, 900

def apply_stylesheet(widget: QWidget, stylesheet_file: str):

    stylesheet_path = os.path.join(STYLESHEET_FOLDER_PATH, stylesheet_file)
    if not os.path.exists(stylesheet_path):
        raise FileNotFoundError(f"Stylesheet file {stylesheet_path} does not exist")
    with open(stylesheet_path, 'r') as f:
        stylesheet = f.read()
        widget.setStyleSheet(stylesheet)

def edit_key_name(str: str): # snake_case to Snake Case
        words = str.split("_")
        for i, word in enumerate(words):
            words[i] = word.capitalize()
        
        return " ".join(words)

def get_user_settings():
    if os.path.exists(USER_PREFERENCE_FILE_PATH):
        with open(USER_PREFERENCE_FILE_PATH) as f:
            data = json.load(f)
            return data
        
def clear_temporary_data():
    for filename in os.listdir(CAD_PREVIEW_DATA_PATH):
        filepath = os.path.join(CAD_PREVIEW_DATA_PATH, filename)
        os.remove(filepath)
    for filename in os.listdir(PART_IMPORT_DATA_PATH):
        filepath = os.path.join(PART_IMPORT_DATA_PATH, filename)
        if filename != PART_IMPORT_INFO_FILENAME:
            os.remove(filepath)

class MainWindow(QMainWindow):  

    def __init__(self):
        super().__init__()
        self.setWindowTitle("NEXACut Pro")
        self.setMinimumSize(MIN_WIDTH, MIN_HEIGHT)
        
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0) 
        main_layout.setSpacing(0)

        self.left_menu = LeftMenu()
        self.stacked_widget = StackedWidget()

        main_layout.addWidget(self.left_menu, 20)
        main_layout.addWidget(self.stacked_widget, 80)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # connects menu button clicks to window switching
        self.left_menu.menu_button_clicked.connect(self.stacked_widget.switch_view)

        atexit.register(self.close_app)
    
    def close_app(self):
        clear_temporary_data()

class LeftMenu(QWidget):

    menu_button_clicked = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        buttons = [
            "Home", 
            "Import Part Files", 
            "Configure CNC Router", 
            "Manage Inventory", 
            "Generate Optimal Placement", 
            "Configure Preferences"]

        for i, button_text in enumerate(buttons):
            button = QPushButton(button_text)
            apply_stylesheet(button, "menu-button.css")
            button.clicked.connect(lambda _, index=i: self.menu_button_clicked.emit(index)) # button clicked boolean signal is ignored
            layout.addWidget(button, 1)

        bottom_widget = QWidget() # fixes random white bg
        apply_stylesheet(bottom_widget, "left-menu.css")

        layout.addWidget(bottom_widget, 10)
        self.setLayout(layout)

class StackedWidget(QStackedWidget):

    def __init__(self):
        super().__init__()
        apply_stylesheet(self, "stacked-widget.css")
        self.setCurrentIndex(0)
        self.widgets = [
            HomeViewWidget(), 
            ImportViewWidget(),  
            RouterViewWidget(), 
            InventoryViewWidget(), 
            PlacementViewWidget(), 
            PreferenceViewWidget()]
        for widget in self.widgets:
            self.addWidget(widget)

    def switch_view(self, index: int):
        if 0 <= index < len(self.widgets):

            old_widget = self.widgets[index]
            self.removeWidget(old_widget)
            old_widget.deleteLater()  

            new_widget = type(old_widget)()

            if type(new_widget) != ImportViewWidget: # clears import preview images in case settings are changed etc.
                clear_temporary_data()

            self.insertWidget(index, new_widget)
            self.widgets[index] = new_widget
            self.setCurrentIndex(index)

class HomeViewWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        logo_label = QLabel()
        script_path = os.path.dirname(__file__)
        logo_path = os.path.join(script_path, 'graphics', 'NEXACut Logo.png')
        pixmap = QPixmap(logo_path)
        scaled_pixmap = pixmap.scaled(1000, 500)
        logo_label.setPixmap(scaled_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_description_label = QLabel("Version 0.0.0   Created by nagan__319")
        apply_stylesheet(app_description_label, "app-description-label.css")
        layout.addStretch(1)
        layout.addWidget(logo_label)
        layout.addStretch(1)
        layout.addWidget(app_description_label)
        self.setLayout(layout)
        print('home view initialized')

class EmptyTabWidget(QWidget):
    def __init__(self, title_text: str, *widgets):
        super().__init__()
        layout = QVBoxLayout()
        title = QLabel(title_text)
        apply_stylesheet(title, "title.css")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        for widget in widgets:
            layout.addWidget(widget)
        layout.addStretch(1)
        self.setLayout(layout)

class ImportViewWidget(EmptyTabWidget):

    MAX_IMPORT_FILES = 8
    MAX_AMT_EACH_FILE = 9

    def __init__(self):
        additional_widgets = [] # passed into super init

        main_widget = QWidget() # includes external padding
        main_layout = QHBoxLayout()

        inner_widget = QWidget()
        inner_layout = QHBoxLayout()
        apply_stylesheet(inner_widget, "left-menu.css")

        left_widget = QWidget() # file import wrapper widget
        left_layout = QVBoxLayout()

        preview_title = QLabel("Preview")
        preview_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        apply_stylesheet(preview_title, "text-widget.css")

        self.image_view = QLabel("No File Selected") # displays matplotlib png from data/cad_preview_data
        apply_stylesheet(self.image_view, "app-description-label.css")
        self.image_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_view.setMinimumHeight(int(MIN_HEIGHT*.71))

        delete_button_wrapper = QWidget()
        delete_button_wrapper_layout = QHBoxLayout()

        delete_button = QPushButton("Remove Selected File")
        apply_stylesheet(delete_button, "router-button.css")
        delete_button.clicked.connect(self.remove_file)

        delete_button_wrapper_layout.addStretch(1)
        delete_button_wrapper_layout.addWidget(delete_button, 1)
        delete_button_wrapper_layout.addStretch(1)
        delete_button_wrapper.setLayout(delete_button_wrapper_layout)

        left_layout.addWidget(preview_title, 1)
        left_layout.addWidget(self.image_view, 8)
        left_layout.addWidget(delete_button_wrapper, 1)
        left_layout.addStretch(1)
        left_widget.setLayout(left_layout)

        barrier = QWidget()
        apply_stylesheet(barrier, "barrier.css")
        barrier.setFixedWidth(1)

        right_widget = QWidget()
        right_layout = QVBoxLayout()

        self.import_button = QPushButton("Import Files")
        apply_stylesheet(self.import_button, "router-button.css")
        self.import_button.clicked.connect(self.import_stl_file)

        self.id_to_filename = defaultdict(int) # maps button ids to filenames (text on button)
        self.id_to_amount = defaultdict(int) # amount of each file
        self.id_to_widgets = defaultdict(int) # tuple containing wrapper widget, scrollbox, and button

        self.import_list_widget = QWidget()
        self.import_list_button_group = QButtonGroup()
        self.selected_button_id = None
        self.new_id = 0

        self.import_list_button_group.setExclusive(True) # only possible to check one button at a time
        self.import_list_button_group.buttonClicked.connect(self.selection_changed_handler)
        self.import_list_layout = QVBoxLayout()
        self.import_list_widget.setLayout(self.import_list_layout)

        right_layout.addWidget(self.import_button)
        right_layout.addWidget(self.import_list_widget)
        right_layout.addStretch(1)
        right_widget.setLayout(right_layout)

        inner_layout.addWidget(left_widget, 3)
        inner_layout.addWidget(barrier)
        inner_layout.addWidget(right_widget, 1)
        inner_widget.setLayout(inner_layout)

        main_layout.addStretch(1)
        main_layout.addWidget(inner_widget, 8)
        main_layout.addStretch(1)
        main_widget.setLayout(main_layout)
        additional_widgets.append(main_widget)

        super().__init__("Import Part Files", *additional_widgets)
        print('import view initialized')

    # file selection

    def selection_changed_handler(self, button):
        self.selected_button_id = self.import_list_button_group.id(button)
        self.update_file_preview()

    def update_file_preview(self): # selects file to display in preview widget
        if self.selected_button_id is None:
            self.image_view.setText("No File Selected")
        else:
            image_name = self.id_to_filename[self.selected_button_id] + '.png'
            image_path = os.path.join(CAD_PREVIEW_DATA_PATH, image_name)
            pixmap = QPixmap(image_path)
            self.image_view.setPixmap(pixmap)

    # adding new file

    # all imported files to use mm
    def import_stl_file(self):

        if len(self.id_to_widgets) >= self.MAX_IMPORT_FILES: 
            return

        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "STL Files (*.stl)")
        file_name = os.path.basename(file_path)[:-4] # no extension

        for i in range(self.new_id): # prevents import of existing files
            if self.id_to_filename[i] == file_name:
                return

        if file_path:
            try:
                button_wrapper = QWidget()
                button_wrapper_layout = QHBoxLayout()

                button = QPushButton()
                button.setCheckable(True)
                button.setText(file_name)
                apply_stylesheet(button, "import-button.css")

                amt_input = QLineEdit()
                apply_stylesheet(amt_input, "amt-line-edit.css")
                amt_input.setPlaceholderText(f"1-{self.MAX_AMT_EACH_FILE}")
                # amt_input.textEdited.connect()
                amt_input.setText("1")

                cad_converter = CADToSVG(file_path, CAD_PREVIEW_DATA_PATH, PART_IMPORT_DATA_PATH)
                user_units = get_user_settings()['units']

                inches_in_mm = 0.0393701

                if user_units == 'Imperial':
                    cad_converter.save_preview_image(inches_in_mm)
                else:
                    cad_converter.save_preview_image() # no scaling necessary
                cad_converter.save_as_svg()

                # dict-like structures containing button and input widgets, wrappers
                self.import_list_button_group.addButton(button, id=self.new_id)
                self.id_to_widgets[self.new_id] = (button_wrapper, button, amt_input)

                button_wrapper_layout.addWidget(button, 3)
                button_wrapper_layout.addWidget(amt_input, 1)
                button_wrapper.setLayout(button_wrapper_layout)

                self.import_list_layout.addWidget(button_wrapper)

                self.id_to_amount[self.new_id] = 1
                self.id_to_filename[self.new_id] = file_name

                self.new_id += 1
            
            except Exception as e: # includes invalid stl etc.
                print(e)

    # file deletion

    def remove_file(self):
        if self.selected_button_id is not None:
            self.delete_preview_file(self.id_to_filename[self.selected_button_id])
            self.delete_svg_file(self.id_to_filename[self.selected_button_id])
            self.delete_imported_stl_button(self.selected_button_id)
            self.update_file_preview()

    def delete_preview_file(self, name: str): # removes file from data/cad_preview_data
        filename = name+'.png'
        file_path = os.path.join(CAD_PREVIEW_DATA_PATH, filename)
        if os.path.exists(file_path):
            os.remove(file_path)

    def delete_svg_file(self, name: str): # removes file from data/part_import_data
        filename = name+'.svg'
        file_path = os.path.join(PART_IMPORT_DATA_PATH, filename)
        if os.path.exists(file_path):
            os.remove(file_path)

    def delete_imported_stl_button(self, button_id): # deletes button widget, pops from dict, unselects
        wrapper_to_remove, button_to_remove, combobox_to_remove = self.id_to_widgets[button_id]

        if button_to_remove:

            self.import_list_button_group.removeButton(button_to_remove)

            self.id_to_widgets.pop(button_id)
            self.id_to_filename.pop(self.selected_button_id)
            self.id_to_amount.pop(button_id)

            button_to_remove.deleteLater()
            combobox_to_remove.deleteLater()
            wrapper_to_remove.deleteLater()

            self.selected_button_id = None
    
class RouterViewWidget(EmptyTabWidget):
    def __init__(self):
        additional_widgets = []
        self.router_manager = RouterManager(ROUTER_DATA_FOLDER_PATH)

        main_widget = QWidget()
        main_layout = QHBoxLayout()

        left_widget = QWidget()
        left_layout = self.get_left_layout_new(self.router_manager.value_ranges)
        print('left layout initialized')

        left_widget.setLayout(left_layout)
        apply_stylesheet(left_widget, "left-menu.css")

        right_widget = QWidget()
        right_layout = QVBoxLayout()

        self.router_list_combobox = QComboBox()
        self.router_list_combobox.addItem("None")
        for router_file in self.router_manager.routers:
            self.router_list_combobox.addItem(router_file[:-5]) # removes .json ending            
        apply_stylesheet(self.router_list_combobox, "combo-box.css")
        self.router_list_combobox.currentIndexChanged.connect(lambda: self.select_router(self.router_list_combobox.currentText())) # calls with name arg

        select_router_text = QLabel("Select Router: ")
        apply_stylesheet(select_router_text, "text-widget.css")

        right_layout.addWidget(select_router_text)
        right_layout.addWidget(self.router_list_combobox)
        right_layout.addStretch(1)
        right_widget.setLayout(right_layout)

        main_layout.addStretch(1)
        main_layout.addWidget(left_widget, 6)
        main_layout.addWidget(right_widget, 2)
        main_layout.addStretch(1)
        main_widget.setLayout(main_layout)

        additional_widgets.append(main_widget)

        super().__init__("Configure CNC Router", *additional_widgets)
        print('router view initialized')

    def get_left_layout_new(self, router_mgr_val_ranges: dict):
        return self.get_left_layout(router_mgr_val_ranges)

    def get_left_layout(self, router_mgr_val_ranges: dict, router_data: dict=None):

        new_router = True if router_data is None else False

        left_layout = QVBoxLayout()

        router_title = QLabel("New Router")
        router_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        apply_stylesheet(router_title, "text-widget.css")

        self.input_widgets = []

        left_layout.addWidget(router_title)

        for key in router_mgr_val_ranges:
            value = router_mgr_val_ranges[key] # range for allowed values
            router_option_widget = QWidget()
            router_option_layout = QHBoxLayout()

            key_widget = QLabel(f"{edit_key_name(key)}: ")
            apply_stylesheet(key_widget, "text-widget.css")

            value_input = QLineEdit()
            self.input_widgets.append(value_input)
            apply_stylesheet(value_input, "line-input.css")
            value_input.setPlaceholderText(f"{value[0]}-{value[1]} mm")

            if not new_router:
                value_input.setText(f"{router_data[key]} mm")

            router_option_layout.addWidget(key_widget, 1)
            router_option_layout.addStretch(1)
            router_option_layout.addWidget(value_input)

            router_option_widget.setLayout(router_option_layout)
            left_layout.addWidget(router_option_widget)
            
        bottom_widget = QWidget()
        bottom_layout = QHBoxLayout()

        add_router_button = QPushButton("Save")
        apply_stylesheet(add_router_button, "router-button.css")
        add_router_button.clicked.connect(self.add_router)
        if not new_router:
            delete_router_button = QPushButton("Delete")
            apply_stylesheet(delete_router_button, "router-button.css")

        bottom_layout.addStretch(1)
        bottom_layout.addWidget(add_router_button, 1)
        if not new_router:
            bottom_layout.addWidget(delete_router_button, 1)
        bottom_layout.addStretch(1)

        bottom_widget.setLayout(bottom_layout)

        left_layout.addWidget(bottom_widget)
        left_layout.addStretch(1)
        
        return left_layout

    def select_router(self, router_name: str):
        if self.router_list_combobox.currentIndex == 0: # none selected
            for i, _ in enumerate(self.input_widgets):
                self.input_widgets[i].setText("banana") # fix this carp
        else:
            self.router_manager.select_router(router_name)
            selected_router_values = self.router_manager.router_data.values()
            for i, value in enumerate(selected_router_values):
                self.input_widgets[i].setText(str(value))

    def add_router(self):
        try:
            values = [int(self.input_widgets[i].text()) for i, _ in enumerate(self.input_widgets)]
            limit_values = self.router_manager.value_ranges.values()
            for i, lim_value in enumerate(limit_values):
                min_value = lim_value[0]
                max_value = lim_value[1]
                if values[i] < min_value or values[i] > max_value:
                    raise ValueError("Input value out of range")
            self.router_manager.add_router('test', values)
            self.router_list_combobox.addItem('test')
            for widget in self.input_widgets:
                widget.setText("")
            self.router_manager.update_properties()

        except Exception as e:
            print(e)

class InventoryViewWidget(EmptyTabWidget):
    def __init__(self):
        additional_widgets = []

        main_widget = QWidget()
        main_layout = QHBoxLayout()

        left_widget = QWidget()  # view individual plates and previews
        apply_stylesheet(left_widget, "left-menu.css")
        left_layout = QVBoxLayout()

        top_wrapper = QWidget()
        top_wrapper_layout = QHBoxLayout()

        preview_title = QLabel("Select Plate: ")
        preview_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        apply_stylesheet(preview_title, "text-widget.css")

        plate_select_combobox = QComboBox()
        apply_stylesheet(plate_select_combobox, "combo-box.css")

        top_wrapper_layout.addWidget(preview_title, 1)
        top_wrapper_layout.addWidget(plate_select_combobox, 1)
        top_wrapper_layout.addStretch(2)
        top_wrapper.setLayout(top_wrapper_layout)

        self.image_view = QLabel("No Plate Selected")
        apply_stylesheet(self.image_view, "app-description-label.css")
        self.image_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_view.setMinimumHeight(int(MIN_HEIGHT*.71))

        button_wrapper = QWidget()
        button_wrapper_layout = QHBoxLayout()

        add_new_button = QPushButton("Add New")
        apply_stylesheet(add_new_button, "router-button.css")

        delete_button = QPushButton("Delete Selected")
        apply_stylesheet(delete_button, "router-button.css")

        button_wrapper_layout.addStretch(1)
        button_wrapper_layout.addWidget(add_new_button, 1)
        button_wrapper_layout.addWidget(delete_button, 1)
        button_wrapper_layout.addStretch(1)
        button_wrapper.setLayout(button_wrapper_layout)

        left_layout.addWidget(top_wrapper, 1)
        left_layout.addWidget(self.image_view, 8)
        left_layout.addWidget(button_wrapper, 1)
        left_widget.setLayout(left_layout)

        right_widget = QWidget()
        right_layout = QVBoxLayout()

        self.stock_list_combobox = QComboBox()
        self.stock_list_combobox.addItem("None")      
        apply_stylesheet(self.stock_list_combobox, "combo-box.css")
        # self.stock_list_combobox.currentIndexChanged.connect(lambda: self.select_router(self.stock_list_combobox.currentText())) # calls with name arg

        select_router_text = QLabel("Select Stock: ")
        apply_stylesheet(select_router_text, "text-widget.css")

        right_layout.addWidget(select_router_text)
        right_layout.addWidget(self.stock_list_combobox)
        right_layout.addStretch(1)
        right_widget.setLayout(right_layout)

        main_layout.addStretch(1)
        main_layout.addWidget(left_widget, 6)
        main_layout.addWidget(right_widget, 2)
        main_layout.addStretch(1)
        main_widget.setLayout(main_layout)

        additional_widgets.append(main_widget)

        super().__init__("Manage Inventory", *additional_widgets)
        print('inventory view initialized')

class PlacementViewWidget(EmptyTabWidget):
    def __init__(self):
        super().__init__("Generate Optimal Placement")
        print('placement view initialized')

class PreferenceViewWidget(EmptyTabWidget):
    def __init__(self):
        additional_widgets = []

        main_widget = QWidget() # includes side margins
        main_layout = QHBoxLayout()

        central_widget = QWidget()
        central_layout = QVBoxLayout()

        self.preference_manager = PreferenceManager(MAX_RES, ROUTER_DATA_FOLDER_PATH, STOCK_DATA_FOLDER_PATH, DEFAULT_PREFERENCE_FILE_PATH, USER_PREFERENCE_FILE_PATH)

        for current_key in self.preference_manager.preference_data: 
            current_val = self.preference_manager.preference_data[current_key]
            row_widget = QWidget()
            row_layout = QHBoxLayout()

            preference_value_label = QLabel(f"{edit_key_name(current_key)}: ")
            apply_stylesheet(preference_value_label, "text-widget.css")

            combo_box = QComboBox() 
            options = self.preference_manager.preference_options[current_key] # all possible values for key
            for current_val in options:
                combo_box.addItem(str(current_val))
            if len(options) == 0:
                combo_box.addItem("None")

            if current_val in options:
                combo_box.setCurrentText(current_val)

            combo_box.currentIndexChanged.connect(partial(self.selection_changed, current_key, combo_box))
            apply_stylesheet(combo_box, "combo-box.css")

            row_layout.addWidget(preference_value_label, 1)
            row_layout.addStretch(1)
            row_layout.addWidget(combo_box, 1)
            row_widget.setLayout(row_layout)

            central_layout.addWidget(row_widget)

        central_widget.setLayout(central_layout)
        apply_stylesheet(central_widget, "left-menu.css")

        main_layout.addStretch(2)
        main_layout.addWidget(central_widget, 6)
        main_layout.addStretch(2)
        main_widget.setLayout(main_layout)

        additional_widgets.append(main_widget)

        super().__init__("Configure Preferences", *additional_widgets)
        print('preference view initialized')
    
    def selection_changed(self, key: str, combo_box: QComboBox, index: int):
        new_value = combo_box.itemText(index)
        self.preference_manager.update_preference(key, new_value)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    print('app running')
    window = MainWindow()
    window.show()
    print('window showing')
    sys.exit(app.exec())