import sys

from PyQt6.QtWidgets import QApplication

from app.backend.data_mgr import DataManager
from app.frontend.main.main_window import MainWindow

from app.config import USER_PREFERENCE_FILE_PATH, ROUTER_DATA_FOLDER_PATH, PLATE_DATA_FOLDER_PATH, CAD_PREVIEW_DATA_PATH, IMAGE_PREVIEW_DATA_PATH

if __name__ == '__main__':
    app = QApplication([])
    data_manager = DataManager(USER_PREFERENCE_FILE_PATH, ROUTER_DATA_FOLDER_PATH, PLATE_DATA_FOLDER_PATH, CAD_PREVIEW_DATA_PATH, IMAGE_PREVIEW_DATA_PATH)
    main_window = MainWindow(data_manager)
    main_window.show()
    sys.exit(app.exec())
