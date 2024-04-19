import atexit
from .utils.file_operations import FileProcessor

class TemporaryDataManager:

    def __init__(self, cad_preview_path: str, img_data_path: str):
        self.CAD_PREVIEW_DATA_PATH = cad_preview_path
        self.IMAGE_PREVIEW_DATA_PATH = img_data_path

        self.file_processor = FileProcessor()

        atexit.register(self.__clear_temporary_data__)

    def __clear_temporary_data__(self):
        for folder in [self.CAD_PREVIEW_DATA_PATH, self.IMAGE_PREVIEW_DATA_PATH]:
            self.file_processor.clear_folder_contents(folder)