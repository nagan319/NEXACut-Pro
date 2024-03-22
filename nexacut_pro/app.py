import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QStackedWidget
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

from preferences.pref_mgr import PreferenceManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NEXACut Pro")
        self.setMinimumSize(1600, 900)

        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0) # outside
        self.main_layout.setSpacing(0)

        self.init_left()
        self.init_right()

        central_widget = QWidget()
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)

    def init_left(self):
        left_widget = QWidget()

        left_layout = QVBoxLayout()
        left_layout.setSpacing(0)
        left_layout.setContentsMargins(0, 0, 0, 0)

        home_button = QPushButton('Home', left_widget)
        home_button.clicked.connect(lambda: self.show_tab(0))

        import_button = QPushButton('Import Part Files', left_widget)
        import_button.clicked.connect(lambda: self.show_tab(1))

        router_button = QPushButton('Configure CNC Router', left_widget)
        router_button.clicked.connect(lambda: self.show_tab(2))

        inventory_button = QPushButton('Manage Inventory', left_widget)
        inventory_button.clicked.connect(lambda: self.show_tab(3))

        placement_button = QPushButton('Generate Optimal Placement', left_widget)
        placement_button.clicked.connect(lambda: self.show_tab(4))

        preference_button = QPushButton('Configure Preferences', left_widget)
        preference_button.clicked.connect(lambda: self.show_tab(5))

        for button in (home_button, import_button, router_button, inventory_button, placement_button, preference_button):
            button.setStyleSheet("""
                QPushButton {
                    background-color: #1E1E1E;
                    color: #BFBFBF;
                    font-family: "Helvetica Neue"; 
                    font-size: 16px;
                    border: 0px;
                    border-radius: 0px;
                    padding: 16px;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #3C3C3C;
                    border-color: #555555;
                }
            """)
        
        left_layout.addWidget(home_button)
        left_layout.addWidget(import_button)
        left_layout.addWidget(router_button)
        left_layout.addWidget(inventory_button)
        left_layout.addWidget(placement_button)
        left_layout.addWidget(preference_button)
        left_layout.addStretch(1)

        left_widget.setStyleSheet("background-color: rgb(30, 30, 30);") 
        left_widget.setLayout(left_layout)

        self.main_layout.addWidget(left_widget, 20)
    
    def init_right(self):
        self.right_stacked_widget = QStackedWidget()

        self.views = []

        # Logo view
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
        app_description_label.setStyleSheet("""color: #BFBFBF; font-family: "Helvetica Neue"; font-size: 12px;""")
        app_description_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        logo_view_layout.addStretch(1)
        logo_view_layout.addWidget(logo_label)
        logo_view_layout.addStretch(1)
        logo_view_layout.addWidget(app_description_label)
        logo_view_widget.setLayout(logo_view_layout)

        self.views.append(logo_view_widget)

        # Import View
        import_view_widget = QWidget()
        import_view_layout = QVBoxLayout()

        import_title = QLabel("Import Part Files")
        import_title.setStyleSheet("""color: #EFEFEF; font-family: "Helvetica Neue"; font-size: 40px;""")
        import_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        import_view_layout.addWidget(import_title)
        import_view_layout.addStretch(1)
        import_view_widget.setLayout(import_view_layout)

        self.views.append(import_view_widget)

        # Router View
        router_view_widget = QWidget()
        router_view_layout = QVBoxLayout()

        router_title = QLabel("Configure CNC Router")
        router_title.setStyleSheet("""color: #EFEFEF; font-family: "Helvetica Neue"; font-size: 40px;""")
        router_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        router_view_layout.addWidget(router_title)
        router_view_layout.addStretch(1)
        router_view_widget.setLayout(router_view_layout)

        self.views.append(router_view_widget)

        # Inventory View
        inventory_view_widget = QWidget()
        inventory_view_layout = QVBoxLayout()

        inventory_title = QLabel("Manage Inventory")
        inventory_title.setStyleSheet("""color: #EFEFEF; font-family: "Helvetica Neue"; font-size: 40px;""")
        inventory_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
        inventory_view_layout.addWidget(inventory_title)
        inventory_view_layout.addStretch(1)
        inventory_view_widget.setLayout(inventory_view_layout)

        self.views.append(inventory_view_widget)

        # Placement View
        placement_view_widget = QWidget()
        placement_view_layout = QVBoxLayout()

        placement_title = QLabel("Generate Optimal Placement")
        placement_title.setStyleSheet("""color: #EFEFEF; font-family: "Helvetica Neue"; font-size: 40px;""")
        placement_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        placement_view_layout.addWidget(placement_title)
        placement_view_layout.addStretch(1)
        placement_view_widget.setLayout(placement_view_layout)

        self.views.append(placement_view_widget)

        # Preference View
        preference_view_widget = QWidget()
        preference_view_layout = QVBoxLayout()

        preference_title = QLabel("Configure Preferences")
        preference_title.setStyleSheet("""color: #EFEFEF; font-family: "Helvetica Neue"; font-size: 40px;""")
        preference_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        preference_view_layout.addWidget(preference_title)
        preference_view_layout.addStretch(1)
        preference_view_widget.setLayout(preference_view_layout)

        self.views.append(preference_view_widget)

        for view in self.views:
            self.right_stacked_widget.addWidget(view)

        self.right_stacked_widget.setStyleSheet("background-color: rgb(45, 45, 45);") 
        self.main_layout.addWidget(self.right_stacked_widget, 80)

    def show_tab(self, num: int):
        self.right_stacked_widget.setCurrentIndex(num)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())