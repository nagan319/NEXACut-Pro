import sys
import os
from collections import defaultdict
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QStackedWidget, QFileDialog, QButtonGroup
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

from nexacut_pro.pref_mgr import PreferenceManager
from nexacut_pro.router_mgr import RouterManager

MIN_WIDTH, MIN_HEIGHT = 1600, 900
MARGIN = 0

TITLE_STYLESHEET = """color: #EFEFEF; font-family: "Helvetica Neue"; font-size: 40px;"""
TITLE_ALIGNMENT = Qt.AlignmentFlag.AlignCenter

LEFT_MENU_BUTTON_STYLESHEET = """QPushButton {background-color: #1E1E1E; color: #BFBFBF; font-family: "Helvetica Neue"; font-size: 16px; border: 0px; border-radius: 0px; padding: 16px;text-align: left;} QPushButton:hover {background-color: #3C3C3C;}"""

GENERAL_BUTTON_STYLESHEET = """QPushButton {background-color: #1E1E1E; color: #BFBFBF; font-family: "Helvetica Neue"; font-size: 16px; border: 0px; border-radius: 0px; padding: 20px;text-align: center;} QPushButton:hover {background-color: #3C3C3C;}"""
IMPORT_BUTTON_STYLESHEET = """QPushButton {background-color: #1E1E1E; color: #BFBFBF; font-family: "Helvetica Neue"; font-size: 16px; border: 0px; border-radius: 0px; padding: 20px;text-align: center;} QPushButton:hover {background-color: #3C3C3C;} QPushButton:checked {background-color: #4D4D4D}"""

APP_LABEL_STYLESHEET = """color: #BFBFBF; font-family: "Helvetica Neue"; font-size: 12px;"""
APP_LABEL_ALIGNMENT = Qt.AlignmentFlag.AlignLeft

class MainWindow(QMainWindow):
    # general initialization
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NEXACut Pro")
        self.setMinimumSize(MIN_WIDTH, MIN_HEIGHT)

        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(MARGIN, MARGIN, MARGIN, MARGIN) 
        self.main_layout.setSpacing(0)

        self.imported_stl_files = defaultdict(str)

        self.init_methods = [
            "init_home_view",
            "init_import_view",
            "init_router_view",
            "init_inventory_view",
            "init_placement_view",
            "init_preferences_view"
        ]
        self.left_buttons = [
            "Home", 
            "Import Part Files", 
            "Configure CNC Router", 
            "Manage Inventory", 
            "Generate Optimal Placement", 
            "Configure Preferences"
        ]

        self.init_left()
        self.init_right()

        central_widget = QWidget()
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)

    def init_left(self): 
        left_widget = QWidget()

        left_layout = QVBoxLayout()
        left_layout.setSpacing(0)
        left_layout.setContentsMargins(MARGIN, MARGIN, MARGIN, MARGIN)

        for i, button_text in enumerate(self.left_buttons):
            button = QPushButton(button_text)
            button.setStyleSheet(LEFT_MENU_BUTTON_STYLESHEET)
            button.clicked.connect(lambda _, index=i: self.show_tab(index)) # _ - clicked signal ignored
            left_layout.addWidget(button)

        left_layout.addStretch(1)

        left_widget.setStyleSheet("background-color: #1E1E1E;") 
        left_widget.setLayout(left_layout)

        self.main_layout.addWidget(left_widget, 20)
    
    def init_right(self):
        self.right_stacked_widget = QStackedWidget()
        
        for method_name in self.init_methods:
            widget = getattr(self, method_name)()
            self.right_stacked_widget.addWidget(widget)
        
        self.right_stacked_widget.setStyleSheet("background-color: #2D2D2D;") 
        self.right_stacked_widget.setCurrentIndex(0)
        self.main_layout.addWidget(self.right_stacked_widget, 80)

    # general functionality
    def show_tab(self, index: int):
        if 0 <= index < len(self.init_methods):
            method_name = self.init_methods[index]
            if hasattr(self, method_name):
                new_widget = getattr(self, method_name)()
                self.right_stacked_widget.removeWidget(self.right_stacked_widget.widget(index))  
                self.right_stacked_widget.insertWidget(index, new_widget)
                self.right_stacked_widget.setCurrentIndex(index)
            else:
                print(f"Initialization method '{method_name}' does not exist in the class.")
        else:
            print(f"Initialization method for tab index {index} does not exist.")

    # home view
    def init_home_view(self):
        logo_view_widget = QWidget()
        logo_view_layout = QVBoxLayout()
        logo_label = QLabel()
        script_path = os.path.dirname(__file__)
        logo_path = os.path.join(script_path, 'graphics', 'NEXACut Logo.png')
        pixmap = QPixmap(logo_path)
        scaled_pixmap = pixmap.scaled(1000, 500)
        logo_label.setPixmap(scaled_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_description_label = QLabel("Version 0.0.0   Created by nagan__319")
        app_description_label.setStyleSheet(APP_LABEL_STYLESHEET)
        app_description_label.setAlignment(APP_LABEL_ALIGNMENT)
        logo_view_layout.addStretch(1)
        logo_view_layout.addWidget(logo_label)
        logo_view_layout.addStretch(1)
        logo_view_layout.addWidget(app_description_label)
        logo_view_widget.setLayout(logo_view_layout)
        return logo_view_widget

    # import view
    def init_import_view(self):
        import_view_widget = QWidget()
        import_view_layout = QVBoxLayout()
        import_title = QLabel("Import Part Files")
        import_title.setStyleSheet(TITLE_STYLESHEET)
        import_title.setAlignment(TITLE_ALIGNMENT)
        main_widget = QWidget()
        main_widget_layout = QHBoxLayout()

        left_widget = QWidget()
        self.import_list = QButtonGroup()
        self.import_list_max_id = 0
        self.selected_button_id = None
        self.import_list.setExclusive(True)
        self.import_list.buttonClicked.connect(self.import_list_clicked_handler)
        self.import_list_layout = QVBoxLayout()
        left_widget.setLayout(self.import_list_layout)
        left_widget.setStyleSheet("background-color: #1E1E1E;")

        right_widget = QWidget()

        main_widget_layout.addWidget(left_widget, 2)
        main_widget_layout.addWidget(right_widget, 3)
        main_widget.setLayout(main_widget_layout)

        bottom_widget = QWidget()
        bottom_widget_layout = QHBoxLayout()
        import_button = QPushButton("Import STL File")
        delete_button = QPushButton("Delete File")
        import_button.setStyleSheet(GENERAL_BUTTON_STYLESHEET)
        delete_button.setStyleSheet(GENERAL_BUTTON_STYLESHEET)
        import_button.clicked.connect(self.import_stl_file)
        delete_button.clicked.connect(self.delete_stl_file)
        bottom_widget_layout.addStretch(1)
        bottom_widget_layout.addWidget(import_button, 2)
        bottom_widget_layout.addWidget(delete_button, 2)
        bottom_widget_layout.addStretch(1)
        bottom_widget.setLayout(bottom_widget_layout)
        import_view_layout.addWidget(import_title)
        import_view_layout.addWidget(main_widget)
        import_view_layout.addStretch(1)
        import_view_layout.addWidget(bottom_widget)
        import_view_widget.setLayout(import_view_layout)
        return import_view_widget

    def create_imported_stl_button(self, text):
        button = QPushButton(text)
        button.setCheckable(True)
        button.setStyleSheet(IMPORT_BUTTON_STYLESHEET)
        self.import_list.addButton(button, id=self.import_list_max_id)
        self.import_list_layout.addWidget(button)

    def delete_imported_stl_button(self, button_id):
        button_to_remove = self.import_list.button(button_id)
        if button_to_remove:
            self.import_list.removeButton(button_to_remove)
            button_to_remove.deleteLater()  # deletes actual button (garbage collection)

    def import_list_clicked_handler(self, button):
        self.selected_button_id = self.import_list.id(button)

    def import_stl_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "STL Files (*.stl)")
        if file_path:
            file_name = os.path.basename(file_path)
            self.create_imported_stl_button(file_name)
            self.imported_stl_files[self.import_list_max_id] = file_path
            self.import_list_max_id += 1

    def delete_stl_file(self):
        if self.selected_button_id is not None:
            self.delete_imported_stl_button(self.selected_button_id)
            self.imported_stl_files.pop(self.selected_button_id)
            self.selected_button_id = None
            self.show_tab(self.init_methods.index("init_import_view"))

    # router view
    def init_router_view(self):
        router_view_widget = QWidget()
        router_view_layout = QVBoxLayout()
        router_title = QLabel("Configure CNC Router")
        router_title.setStyleSheet(TITLE_STYLESHEET)
        router_title.setAlignment(TITLE_ALIGNMENT)
        self.router_manager = RouterManager()
        router_view_layout.addWidget(router_title)
        router_view_layout.addStretch(1)
        router_view_widget.setLayout(router_view_layout)
        return router_view_widget

    # inventory view
    def init_inventory_view(self):
        inventory_view_widget = QWidget()
        inventory_view_layout = QVBoxLayout()
        inventory_title = QLabel("Manage Inventory")
        inventory_title.setStyleSheet(TITLE_STYLESHEET)
        inventory_title.setAlignment(TITLE_ALIGNMENT)
        inventory_view_layout.addWidget(inventory_title)
        inventory_view_layout.addStretch(1)
        inventory_view_widget.setLayout(inventory_view_layout)
        return inventory_view_widget

    # placement view
    def init_placement_view(self):
        placement_view_widget = QWidget()
        placement_view_layout = QVBoxLayout()
        placement_title = QLabel("Generate Optimal Placement")
        placement_title.setStyleSheet(TITLE_STYLESHEET)
        placement_title.setAlignment(TITLE_ALIGNMENT)
        placement_view_layout.addWidget(placement_title)
        placement_view_layout.addStretch(1)
        placement_view_widget.setLayout(placement_view_layout)
        return placement_view_widget

    # preference view
    def init_preferences_view(self):
        preference_view_widget = QWidget()
        preference_view_layout = QVBoxLayout()
        preference_title = QLabel("Configure Preferences")
        preference_title.setStyleSheet(TITLE_STYLESHEET)
        preference_title.setAlignment(TITLE_ALIGNMENT)
        self.preference_layouts = []
        self.preference_manager = PreferenceManager()
        for key, value in zip(self.preference_manager.keys, self.preference_manager.values):
            row_widget = QWidget()
            row_layout = QHBoxLayout()
            button_text = f"{self._edit_key_name(key)}: {self._edit_par_name(value)}"
            preference_value_button = QPushButton(button_text)
            preference_value_button.setStyleSheet(GENERAL_BUTTON_STYLESHEET)
            preference_value_button.clicked.connect(lambda _, k=key: self.modify_preference(k))
            preference_value_button.update()
            row_layout.addStretch(1)
            row_layout.addWidget(preference_value_button, 2)
            row_layout.addStretch(1)
            row_widget.setLayout(row_layout)
            self.preference_layouts.append(row_widget)
        revert_preference_widget = QWidget()
        revert_preference_layout = QHBoxLayout()
        revert_preference_button = QPushButton("Revert Preferences")
        revert_preference_button.setStyleSheet(GENERAL_BUTTON_STYLESHEET)
        revert_preference_button.clicked.connect(self.revert_preferences)
        revert_preference_layout.addStretch(1)
        revert_preference_layout.addWidget(revert_preference_button, 2)
        revert_preference_layout.addStretch(1)
        revert_preference_widget.setLayout(revert_preference_layout)
        preference_view_layout.addWidget(preference_title)
        for layout in self.preference_layouts:
            preference_view_layout.addWidget(layout)
        preference_view_layout.addStretch(1)
        preference_view_layout.addWidget(revert_preference_widget)
        preference_view_widget.setLayout(preference_view_layout)
        return preference_view_widget

    def _edit_key_name(self, str: str): # snake_case to Snake Case
        words = str.split("_")
        for i, word in enumerate(words):
            words[i] = word.capitalize()
        
        return " ".join(words)

    def _edit_par_name(self, param):
        if isinstance(param, str):
            if len(param) == 0:
                return("None")
            else:
                return(param.capitalize())
        return param
    
    def modify_preference(self, idx: int):
        self.preference_manager.edit_preference(idx)
        self.show_tab(self.init_methods.index("init_preferences_view"))

    def revert_preferences(self):
        self.preference_manager.revert_preferences()
        self.show_tab(self.init_methods.index("init_preferences_view"))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())