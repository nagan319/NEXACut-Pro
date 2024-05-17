import atexit
import logging
from typing import List, Dict

from .utils.file_processor import FileProcessor

class DataManager:
    """
    Class for loading, saving, and storing all application data with the exception of temporary matplotlib preview files. 
    Loads permanent files at initialization and saves at exit. 
    Cleans out temporary directories at exit.
    
    ### Arguments:
    - user_pref_path: Path for user preference file (json).
    - router_data_path: Path for router data file (csv).
    - plate_data_path: Path for plate data file (csv).
    - temp_data_folders: List of directories for storing temporary data.
    """

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
        """
        Attempts to load long term data from paths specified at initialization, raises exception if an error occurs. 
        """
        try:
            self._user_preferences = self._get_user_preferences()
            self._router_data = self._get_router_data()
            self._plate_data = self._get_plate_data()
        except Exception as e:
            self._logger.error(f"Error initializing long-term data: {e}")

    def _init_temp_data(self):
        """
        Initializes temporary data as empty lists.
        """
        self._imported_parts = []

    def _get_user_preferences(self) -> dict:
        """
        Attempts to read data from user preference file, returning a dictionary.
        Returns an empty dictonary if an error occurs.
        """
        try:
            return FileProcessor.read_file(self._user_preference_file_path)
        except Exception as e:
            self._logger.error(f"Error reading user preferences: {e}")
            return {}

    def _get_router_data(self) -> List[dict]:
        """
        Attempts to read data from router data file, returning a list of dictionaries.
        Returns an empty list if an error occurs.     
        """
        try:
            return FileProcessor.read_file(self._router_data_path)
        except Exception as e:
            self._logger.error(f"Error reading router data: {e}")
            return []

    def _get_plate_data(self) -> List[dict]:
        """
        Attempts to read data from plate data file, returning a list of dictionaries.
        Returns an empty list if an error occurs.     
        """
        try:
            return FileProcessor.read_file(self._plate_data_path)
        except Exception as e:
            self._logger.error(f"Error reading plate data: {e}")
            return []

    def _atexit(self):
        """
        Attempts to save all long-term data and clear temporary directories.
        """
        try:
            self._save_user_preferences()
            self._save_router_data()
            self._save_plate_data()
            self._clear_temporary_data()
        except Exception as e:
            self._logger.error(f"Error saving data or clearing temporary data: {e}")

    def _save_user_preferences(self):
        """
        Saves user preferences to json file specified at initialization.
        """
        try:
            FileProcessor.write_file(self._user_preference_file_path, self._user_preferences)
        except Exception as e:
            self._logger.error(f"Error saving user preferences: {e}")

    def _save_router_data(self):
        """
        Saves router data to csv file specified at initialization.
        """
        try:
            FileProcessor.write_file(self._router_data_path, self._router_data)
        except Exception as e:
            self._logger.error(f"Error saving router data: {e}")

    def _save_plate_data(self):
        """
        Saves plate data to csv file specified at initialization.
        """
        try:
            FileProcessor.write_file(self._plate_data_path, self._plate_data)
        except Exception as e:
            self._logger.error(f"Error saving plate data: {e}")

    def _clear_temporary_data(self):
        """
        Clears all temporary directories specified at initialization.
        """
        try:
            for folder in self._temp_data_folders:
                FileProcessor.clear_folder_contents(folder)
        except Exception as e:
            self._logger.error(f"Error clearing temporary data: {e}")
