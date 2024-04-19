import sys

from PyQt6.QtWidgets import QApplication

from app.backend.data_mgr import DataManager
from app.frontend.main.main_window import MainWindow

from app.config import \
    USER_PREFERENCE_FILE_PATH, \
    ROUTER_DATA_PATH, \
    PLATE_DATA_PATH, \
    TEMP_PATHS

if __name__ == '__main__':
    app = QApplication([])
    data_manager = DataManager(USER_PREFERENCE_FILE_PATH, ROUTER_DATA_PATH, PLATE_DATA_PATH, TEMP_PATHS)
    main_window = MainWindow(data_manager)
    main_window.show()
    sys.exit(app.exec())
