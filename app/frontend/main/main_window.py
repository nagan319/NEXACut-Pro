from PyQt6.QtWidgets import QMainWindow, QHBoxLayout, QWidget
from PyQt6.QtGui import QFontDatabase

from ..utils.util_widgets.menu_widget import Menu
from ..utils.util_widgets.content_viewer import ContentViewer

from ..views.home_widget import HomeWidget
from ..views.import_widget import ImportWidget
from ..views.router_widget import RouterWidget
from ..views.inventory_widget import InventoryWidget

from ...backend.data_mgr import DataManager

from ...config import MIN_WIDTH, MIN_HEIGHT, APP_TITLE, MAIN_FONT_PATH

class MainWindow(QMainWindow):

    MENU_BUTTONS = [
        "Home", 
        "Import Part Files", 
        "Configure CNC Router", 
        "Manage Inventory", 
        "Generate Optimal Placement", 
        "Configure Preferences"]

    def __init__(self, data_manager: DataManager): 
        super().__init__()

        self.setWindowTitle(APP_TITLE)
        self.setMinimumSize(MIN_WIDTH, MIN_HEIGHT)
        QFontDatabase.addApplicationFont(MAIN_FONT_PATH)

        self.__layout = QHBoxLayout()
        self.__layout.setContentsMargins(0, 0, 0, 0) 
        self.__layout.setSpacing(0)

        self.__menu = Menu(self.MENU_BUTTONS)

        self.WIDGETS = [
            HomeWidget(),
            ImportWidget(data_manager.imported_parts, data_manager.PART_IMPORT_LIMIT),
            RouterWidget(data_manager.router_data, data_manager.ROUTER_LIMIT),
            InventoryWidget(data_manager.plate_data, data_manager.PLATE_LIMIT)
        ]

        self.__content_viewer = ContentViewer(self.WIDGETS)

        self.__layout.addWidget(self.__menu, 2)
        self.__layout.addWidget(self.__content_viewer, 8)

        self.__widget = QWidget()
        self.__widget.setLayout(self.__layout)
        self.setCentralWidget(self.__widget)

        self.__menu.button_clicked.connect(self.__content_viewer.set_view)