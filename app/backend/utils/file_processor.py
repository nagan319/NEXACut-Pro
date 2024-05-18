import os
import sys
import shutil
import json
import csv
from typing import List, Dict, Union, Any
import logging
import numpy as np

class FileProcessor:
    """
    Functional class to read from and write to files in various formats.
    """
    logger = logging.getLogger(__name__)
    if not logger.hasHandlers():
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    @staticmethod
    def read_file(filepath: str) -> Union[dict, List[dict], None]:
        """
        Read data from a file.

        Arguments:
        - filepath: The path to the file to be read.

        Returns:
        - The data read from the file.
            Returns a list of dictionaries if the file is a CSV, or a dictionary if the file is JSON.
            Returns None if an error is encountered or the file does not exist.
        """
        FileProcessor.logger.debug(f"Reading file: {filepath}")

        _, extension = os.path.splitext(filepath)

        if not os.path.exists(filepath):
            FileProcessor.logger.error(f"File does not exist: {filepath}")
            return None
        try:
            if extension.lower() == '.csv':
                return FileProcessor._read_csv(filepath)
            elif extension.lower() == '.json':
                return FileProcessor._read_json(filepath)
            else:
                FileProcessor.logger.error(f"Unsupported file extension: {extension}")
                return None
        except Exception as e:
            FileProcessor.logger.error(f"Error reading file: {filepath} - {e}")
            return None

    @staticmethod
    def _read_csv(filepath: str) -> List[dict]:
        """
        Read data from a CSV file.

        Arguments:
        - filepath: The path to the CSV file to be read.

        Returns:
        - The data read from the CSV file as a list of dictionaries.
        """
        with open(filepath, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            data = list(reader)    
        return data

    @staticmethod
    def _deserialize_array(array_str: str):
        """
        Converts np array stored as string to array format.
        """
        return np.fromstring(array_str.strip('[]'), sep=',')

    @staticmethod
    def _read_json(filepath: str) -> dict:
        """
        Read data from a JSON file.

        Arguments:
        - filepath: The path to the JSON file to be read.

        Returns:
        - The data read from the JSON file as a dictionary.
        """
        with open(filepath, 'r') as file:
            data = json.load(file)
        return data

    @staticmethod
    def write_file(filepath: str, data: Union[dict, List[dict]], format: str = 'csv') -> None:
        """
        Write data to a file.

        Arguments:
        - filepath: The path to the file to write the data to.
        - data: The data to be written to the file.
        - format: The format of the file ('csv' or 'json'). Defaults to 'csv'.
        """
        _, extension = os.path.splitext(filepath)

        FileProcessor.logger.debug(f"Writing to file: {filepath}")

        if extension.lower() == '.csv' and format == 'csv':
            FileProcessor._write_csv(filepath, data)
            return
        if extension.lower() == '.json' and format == 'json':
            FileProcessor._write_json(filepath, data)
            return
    
        FileProcessor.logger.error(f"Cannot write to file of unsupported filetype {extension}.")

    @staticmethod
    def _write_csv(filepath: str, data: List[dict]) -> None:
        """
        Write data to a CSV file.

        Arguments:
        - filepath: The path to the CSV file to write the data to.
        - data: The data to be written to the CSV file as a list of dictionaries.
        """               
        with open(filepath, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

    @staticmethod
    def _write_json(filepath: str, data: dict) -> None:
        """
        Write data to a JSON file.

        Arguments:
        - filepath: The path to the JSON file to write the data to.
        - data: The data to be written to the JSON file as a dictionary.
        """
        with open(filepath, 'w') as file:
            json.dump(data, file, indent=4)

    @staticmethod
    def read_all_json_in_folder(folder_path: str) -> List[dict]:
        """
        Read data from all JSON files in a folder.

        Arguments:
        - folder_path: The path to the folder containing JSON files.

        Returns:
        - The data read from all JSON files in the folder as a list of dictionaries.
            Returns None if the folder does not exist.
        """
        FileProcessor.logger.debug(f"Reading all JSON files in directory {folder_path}")

        if not os.path.exists(folder_path):
            FileProcessor.logger.error(f"Directory does not exist: {folder_path}")
            return

        data = []
        files = FileProcessor.get_all_filenames_in_folder(folder_path)

        for filename in files:
            _, extension = os.path.splitext(filename)
            if extension.lower() != '.json':
                continue
            filepath = os.path.join(folder_path, filename)
            data.append(FileProcessor._read_json(filepath))

        return data

    @staticmethod
    def write_multiple_json_to_folder(data: List[dict], folder_path: str) -> None:
        """
        Write multiple dictionaries to separate JSON files in a folder.

        Arguments:
        - data: A list of dictionaries, where each dictionary represents data to be written to a JSON file.
        - folder_path: The path to the folder where JSON files will be written.
        """
        FileProcessor.logger.debug(f"Writing multiple JSON files to directory {folder_path}")

        if not os.path.exists(folder_path):
            FileProcessor.logger.error(f"Directory does not exist: {folder_path}")
            return
        
        for item in data:
            if not isinstance(item, dict):
                return
            try:
                temp = item['id']
            except KeyError:
                FileProcessor.logger.error(f"Data is in invalid format") # edit this thing to be more understandable - add structs or smth
                return
        
        FileProcessor.clear_folder_contents(folder_path)

        for item in data:
            filename = item['filename']
            filepath = os.path.join(folder_path, filename)
            FileProcessor._write_json(filepath, item)

    @staticmethod
    def get_all_filenames_in_folder(folder_path: str):
        """
        Get a list of all filenames in a folder.

        Arguments:
        - folder_path: The path to the folder.

        Returns:
        - A list of filenames in the folder.
        """
        FileProcessor.logger.debug(f"Retrieving all filenames in directory {folder_path}")

        if not os.path.exists(folder_path):
            FileProcessor.logger.error(f"Directory does not exist: {folder_path}")
            return []
        return os.listdir(folder_path)
    
    @staticmethod
    def clear_folder_contents(dirpath, *exceptions):
        """
        Clear the contents of a folder, excluding specified filenames.

        Arguments:
        - dirpath: The path to the folder to clear.
        - *exceptions: Filenames to exclude from deletion.
        """
        FileProcessor.logger.debug(f"Clearing all files in directory {dirpath} except {exceptions}")

        if not os.path.exists(dirpath):
            FileProcessor.logger.error(f"Directory does not exist: {dirpath}")
            return
        
        for filename in os.listdir(dirpath):
            if filename not in exceptions:
                filepath = os.path.join(dirpath, filename)
                os.remove(filepath)

    @staticmethod
    def remove_file(filepath):
        """
        Remove a file.

        Arguments:
        - filepath: The path to the file to be removed.
        """
        FileProcessor.logger.debug(f"Removing file {filepath}")

        if not (os.path.exists(filepath)):
            FileProcessor.logger.error(f"File does not exist: {filepath}")
            return
        os.remove(filepath)

    @staticmethod
    def copy_file(src_path, dst_path):
        """
        Copy a file from source to destination.

        Arguments:
        - src_path: The path to the source file.
        - dst_path: The path to the destination file.
        """
        FileProcessor.logger.debug(f"Copying file from {src_path} to {dst_path}")

        if os.path.splitext(src_path)[1] != os.path.splitext(dst_path)[1]:
            FileProcessor.logger.error(f"Files {src_path} and {dst_path} are of different types.")
            return

        if os.path.exists(src_path) and not os.path.exists(dst_path):
            shutil.copyfile(src_path, dst_path)
