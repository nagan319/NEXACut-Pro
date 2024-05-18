from PyQt6.QtWidgets import QMainWindow, QHBoxLayout, QWidget
from PyQt6.QtGui import QFontDatabase

import logging

from ..utils.util_widgets.menu_widget import Menu
from ..utils.util_widgets.content_viewer import ContentViewer

from ..views.home_widget import HomeWidget
from ..views.import_widget import ImportWidget
from ..views.router_widget import RouterWidget
from ..views.inventory_widget import InventoryWidget

from ...backend.data_mgr import DataManager

from ...config import MIN_WIDTH, MIN_HEIGHT, APP_TITLE, MAIN_FONT_PATH, PART_IMPORT_LIMIT, ROUTER_LIMIT, PLATE_LIMIT

class MainWindow(QMainWindow):

    MENU_BUTTONS = [
        "Home", 
        "Import Part Files", 
        "Configure CNC Router", 
        "Manage Inventory", 
        "Generate Optimal Placement", 
        "Configure Preferences"
    ]

    def __init__(self, data_manager: DataManager): 
        self.logger = logging.getLogger(__name__)
        if not self.logger.hasHandlers():
            self.logger.setLevel(logging.DEBUG)
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        self.logger.debug(f"Initializing main window...")
        super().__init__()

        self.setWindowTitle(APP_TITLE)
        self.setMinimumSize(MIN_WIDTH, MIN_HEIGHT)
        QFontDatabase.addApplicationFont(MAIN_FONT_PATH) 

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0) 
        layout.setSpacing(0)

        menu = Menu(self.MENU_BUTTONS)

        self.WIDGETS = [
            HomeWidget(),
            ImportWidget(data_manager.imported_parts, PART_IMPORT_LIMIT),
            RouterWidget(data_manager.router_data, ROUTER_LIMIT),
            InventoryWidget(data_manager.plate_data, PLATE_LIMIT)
        ]

        content_viewer = ContentViewer(self.WIDGETS)

        layout.addWidget(menu, 2)
        layout.addWidget(content_viewer, 8)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        menu.button_clicked.connect(content_viewer.set_view)