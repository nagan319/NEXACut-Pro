from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QMainWindow, QHBoxLayout, QWidget
from PyQt6.QtGui import QFontDatabase

from frontend.utils.util_widgets.menu_widget import Menu
from frontend.utils.util_widgets.content_viewer import ContentViewer

from app.config import MAIN_FONT_PATH

class MainWindow(QMainWindow):

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

    WIDGETS = [ # edit

    ]

    def __init__(self): 
        super().__init__()
        self.setWindowTitle(self.APP_TITLE)
        self.setMinimumSize(self.MIN_WIDTH, self.MIN_HEIGHT)
        QFontDatabase.addApplicationFont(MAIN_FONT_PATH)
        self.__init_gui__()
    
    def __init_gui__(self):
        self.__layout = QHBoxLayout()
        self.__layout.setContentsMargins(0, 0, 0, 0) 
        self.__layout.setSpacing(0)

        self.__menu = Menu(self.MENU_BUTTONS)
        self.__content_viewer = ContentViewer(self.WIDGETS)

        self.__layout.addWidget(self.__menu, 2)
        self.__layout.addWidget(self.__content_viewer, 8)

        self.__widget = QWidget()
        self.__widget.setLayout(self.__layout)
        self.setCentralWidget(self.__widget)

        self.__menu.button_clicked.connect(self.__content_viewer.set_view)