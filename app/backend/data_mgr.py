import atexit
import logging
from .utils.file_processor import FileProcessor

class DataManager:
    def __init__(self, user_pref_path: str, router_data_path: str, plate_data_path: str, temp_data_folders: list):
        self._user_preference_file_path = user_pref_path
        self._router_data_path = router_data_path
        self._plate_data_path = plate_data_path
        self._temp_data_folders = temp_data_folders

        self._logger = logging.getLogger(__name__)  

        self._init_long_term_data()
        self._init_temp_data()
        atexit.register(self._atexit)

    def _init_long_term_data(self):
        try:
            self._user_preferences = self._get_user_preferences()
            self._router_data = self._get_router_data()
            self._plate_data = self._get_plate_data()
        except Exception as e:
            self._logger.error(f"Error initializing long-term data: {e}")

    def _init_temp_data(self):
        self._imported_parts = []

    def _get_user_preferences(self) -> dict:
        try:
            return FileProcessor.read_file(self._user_preference_file_path)
        except Exception as e:
            self._logger.error(f"Error reading user preferences: {e}")
            return {}

    def _get_router_data(self) -> dict:
        try:
            return FileProcessor.read_file(self._router_data_path)
        except Exception as e:
            self._logger.error(f"Error reading router data: {e}")
            return {}

    def _get_plate_data(self) -> dict:
        try:
            return FileProcessor.read_file(self._plate_data_path)
        except Exception as e:
            self._logger.error(f"Error reading plate data: {e}")
            return {}

    def _atexit(self):
        try:
            self._save_user_preferences()
            self._save_router_data()
            self._save_plate_data()
            self._clear_temporary_data()
        except Exception as e:
            self._logger.error(f"Error saving data or clearing temporary data: {e}")

    def _save_user_preferences(self):
        try:
            FileProcessor.write_file(self._user_preference_file_path, self._user_preferences)
        except Exception as e:
            self._logger.error(f"Error saving user preferences: {e}")

    def _save_router_data(self):
        try:
            FileProcessor.write_file(self._router_data_path, self._router_data)
        except Exception as e:
            self._logger.error(f"Error saving router data: {e}")

    def _save_plate_data(self):
        try:
            FileProcessor.write_file(self._plate_data_path, self._plate_data)
        except Exception as e:
            self._logger.error(f"Error saving plate data: {e}")

    def _clear_temporary_data(self):
        try:
            for folder in self._temp_data_folders:
                FileProcessor.clear_folder_contents(folder)
        except Exception as e:
            self._logger.error(f"Error clearing temporary data: {e}")
