import sys

from PyQt6.QtWidgets import QApplication

from backend.data_mgr import DataManager
from frontend.main.main_window import MainWindow

if __name__ == '__main__':
    app = QApplication()
    data_manager = DataManager()
    main_window = MainWindow(data_manager)
    main_window.show()
    sys.exit(app.exec())
