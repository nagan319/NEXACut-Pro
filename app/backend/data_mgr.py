import atexit
from .utils.file_operations import FileProcessor

class DataManager:

    PART_IMPORT_LIMIT = 20 
    ROUTER_LIMIT = 10
    PLATE_LIMIT = 50

    def __init__(self, user_pref_path: str, router_data_path: str, plate_data_path: str, temp_data_folders: list):

        self.USER_PREFERENCE_FILE_PATH = user_pref_path
        self.ROUTER_DATA_FOLDER_PATH = router_data_path
        self.PLATE_DATA_FOLDER_PATH = plate_data_path
        self.TEMP_DATA_FOLDERS = temp_data_folders

        self.file_processor = FileProcessor()
        self.__init_long_term_data__()
        self.__init_temp_data__()
        atexit.register(self.__atexit__)

    def __init_long_term_data__(self):
        self.user_preferences = self.__get_user_preferences__()
        self.router_data = self.__get_router_data__()
        self.plate_data = self.__get_plate_data__()

    def __init_temp_data__(self):
        self.imported_parts = []

    def __get_user_preferences__(self) -> dict:
        return self.file_processor.get_json_data(self.USER_PREFERENCE_FILE_PATH)
    
    def __get_router_data__(self) -> dict:
        return self.file_processor.get_all_json_in_folder(self.ROUTER_DATA_FOLDER_PATH)

    def __get_plate_data__(self) -> dict:
        return self.file_processor.get_all_json_in_folder(self.PLATE_DATA_FOLDER_PATH)

    def __atexit__(self):
        self.__save_user_preferences__()
        self.__save_router_data__()
        self.__save_plate_data__()
        self.__clear_temporary_data__()

    def __save_user_preferences__(self):
        self.file_processor.save_json(self.USER_PREFERENCE_FILE_PATH, self.user_preferences)
    
    def __save_router_data__(self): 
        self.file_processor.save_all_json_to_folder(self.router_data, self.ROUTER_DATA_FOLDER_PATH)
    
    def __save_plate_data__(self):
        self.file_processor.save_all_json_to_folder(self.plate_data, self.PLATE_DATA_FOLDER_PATH)

    def __clear_temporary_data__(self):
        for folder in self.TEMP_DATA_FOLDERS:
            self.file_processor.clear_folder_contents(folder)