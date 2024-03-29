import sys
import os
from functools import partial
from collections import defaultdict
from PyQt6.QtCore import Qt, pyqtSignal, QFile, QTextStream
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QStackedWidget, QFileDialog, QButtonGroup, QComboBox, QLineEdit
from PyQt6.QtGui import QPixmap

MAX_RES = 4

from filepaths import *

from pref_mgr import PreferenceManager
from router_mgr import RouterManager

# todo: fix preference menu always showing default values on startup
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
    def __init__(self):
        additional_widgets = []

        main_widget = QWidget()
        main_layout = QHBoxLayout()

        left_widget = QWidget()
        apply_stylesheet(left_widget, "left-menu.css")
        left_layout = QVBoxLayout()

        preview_title = QLabel("Preview")
        preview_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        apply_stylesheet(preview_title, "text-widget.css")

        self.image_view = QLabel("No File Selected")
        apply_stylesheet(self.image_view, "app-description-label.css")
        self.image_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_view.setMinimumHeight(int(MIN_HEIGHT*.71))

        left_layout.addWidget(preview_title, 1)
        left_layout.addWidget(self.image_view, 8)
        left_layout.addStretch(1)
        left_widget.setLayout(left_layout)

        right_widget = QWidget()
        right_layout = QVBoxLayout()

        import_button = QPushButton("Import Files")
        apply_stylesheet(import_button, "router-button.css")
        import_button.clicked.connect(self.import_stl_file)

        self.button_ids = defaultdict(int) # maps button ids to filenames (text on button)

        self.import_list_widget = QWidget()
        self.import_list_button_group = QButtonGroup()
        self.selected_button_id = None
        self.max_button_id = 0
        self.import_list_button_group.setExclusive(True) # only possible to check one button at a time
        self.import_list_button_group.buttonClicked.connect(self.import_list_clicked_handler)
        self.import_list_layout = QVBoxLayout()
        self.import_list_widget.setLayout(self.import_list_layout)

        right_layout.addWidget(import_button)
        right_layout.addWidget(self.import_list_widget)
        right_layout.addStretch(1)
        right_widget.setLayout(right_layout)

        main_layout.addStretch(1)
        main_layout.addWidget(left_widget, 6)
        main_layout.addWidget(right_widget, 2)
        main_layout.addStretch(1)
        main_widget.setLayout(main_layout)
        additional_widgets.append(main_widget)

        super().__init__("Import Part Files", *additional_widgets)
        print('import view initialized')

    def import_list_clicked_handler(self, button):
        self.selected_button_id = self.import_list_button_group.id(button)

    def update_file_preview(self):
        if self.selected_button_id is None:
            self.image_view.setText("No File Selected")
        else:
            pass

    def import_stl_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "STL Files (*.stl)")
        if file_path:
            file_name = os.path.basename(file_path)
            self.create_imported_stl_button(file_name)
            self.button_ids[self.max_button_id] = file_path
            self.max_button_id += 1

    def create_imported_stl_button(self, text):
        button = QPushButton(text)
        button.setCheckable(True)
        apply_stylesheet(button, "menu-button.css")
        self.import_list_button_group.addButton(button, id=self.max_button_id)
        self.import_list_layout.addWidget(button)

    def delete_stl_file(self):
        if self.selected_button_id is not None:
            self.delete_imported_stl_button(self.selected_button_id)
            self.button_ids.pop(self.selected_button_id)
            self.selected_button_id = None

    def delete_imported_stl_button(self, button_id):
        button_to_remove = self.import_list_button_group.button(button_id)
        if button_to_remove:
            self.import_list_button_group.removeButton(button_to_remove)
            button_to_remove.deleteLater()

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

        router_list_combobox = QComboBox()
        router_list_combobox.addItems(self.router_manager.routers)
        if len(self.router_manager.routers) == 0:
            router_list_combobox.addItem("None")
        apply_stylesheet(router_list_combobox, "combo-box.css")
        # router_list_combobox.currentIndexChanged.connect(self.select_router)

        select_router_text = QLabel("Select Router: ")
        apply_stylesheet(select_router_text, "text-widget.css")

        right_layout.addWidget(select_router_text)
        right_layout.addWidget(router_list_combobox)
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

        left_layout.addWidget(router_title)

        for key in router_mgr_val_ranges:
            value = router_mgr_val_ranges[key] # range for allowed values
            router_option_widget = QWidget()
            router_option_layout = QHBoxLayout()

            key_widget = QLabel(f"{edit_key_name(key)}: ")
            apply_stylesheet(key_widget, "text-widget.css")

            value_input = QLineEdit()
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
        # add_router_button.clicked.connect(self.add_router)
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


    def select_router(self):
        pass

    def add_router(self):
        pass

class InventoryViewWidget(EmptyTabWidget):
    def __init__(self):
        super().__init__("Manage Inventory")
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
        for key in self.preference_manager.preference_data: # value broken for some reason
            current_val = self.preference_manager.preference_data[key]
            row_widget = QWidget()
            row_layout = QHBoxLayout()

            preference_value_label = QLabel(f"{edit_key_name(key)}: ")
            apply_stylesheet(preference_value_label, "text-widget.css")

            combo_box = QComboBox() 
            options = self.preference_manager.preference_options[key]
            for current_val in options:
                combo_box.addItem(str(current_val))
            if len(options) == 0:
                combo_box.addItem("None")

            initial_index = options.index(current_val) if current_val in options else 0
            combo_box.setCurrentIndex(initial_index)

            combo_box.currentIndexChanged.connect(partial(self.selection_changed, key, combo_box))
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