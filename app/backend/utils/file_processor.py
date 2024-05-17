import os
import shutil
import json
import csv
from typing import List, Dict, Union, Any

class FileProcessor:
    """
    Functional class to read from and write to files in various formats.
    """

    @staticmethod
    def read_file(filepath):
        """
        Read data from a file.

        Arguments:
        - filepath: The path to the file to be read.

        Returns:
        - The data read from the file.
            Returns a list of dictionaries if the file is a CSV, or a dictionary if the file is JSON.
            Returns None if the file does not exist.
        """
        _, extension = os.path.splitext(filepath)

        if not os.path.exists(filepath):
            return 
        if extension.lower() == '.csv':
            return FileProcessor._read_csv(filepath)
        if extension.lower() == '.json':
            return FileProcessor._read_json(filepath)

    @staticmethod
    def _read_csv(filepath):
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
    def _read_json(filepath):
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
    def write_file(filepath, data, format='csv'):
        """
        Write data to a file.

        Arguments:
        - filepath: The path to the file to write the data to.
        - data: The data to be written to the file.
        - format: The format of the file ('csv' or 'json'). Defaults to 'csv'.
        """
        _, extension = os.path.splitext(filepath)

        if extension.lower() == '.csv' and format == 'csv':
            FileProcessor._write_csv(filepath, data)
            return
        if extension.lower() == '.json' and format == 'json':
            FileProcessor._write_json(filepath, data)
            return

    @staticmethod
    def _write_csv(filepath, data):
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
    def _write_json(filepath, data):
        """
        Write data to a JSON file.

        Arguments:
        - filepath: The path to the JSON file to write the data to.
        - data: The data to be written to the JSON file as a dictionary.
        """
        with open(filepath, 'w') as file:
            json.dump(data, file, indent=4)

    @staticmethod
    def read_all_json_in_folder(folder_path):
        """
        Read data from all JSON files in a folder.

        Arguments:
        - folder_path: The path to the folder containing JSON files.

        Returns:
        - The data read from all JSON files in the folder as a list of dictionaries.
            Returns None if the folder does not exist.
        """
        if not os.path.exists(folder_path):
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
    def write_multiple_json_to_folder(data, folder_path):
        """
        Write multiple dictionaries to separate JSON files in a folder.

        Arguments:
        - data: A list of dictionaries, where each dictionary represents data to be written to a JSON file.
        - folder_path: The path to the folder where JSON files will be written.
        """
        if not os.path.exists(folder_path):
            return
        
        for item in data:
            if not isinstance(item, dict):
                return
            try:
                temp = item['filename']
            except KeyError:
                return
        
        FileProcessor.clear_folder_contents(folder_path)

        for item in data:
            filename = item['filename']
            filepath = os.path.join(folder_path, filename)
            FileProcessor._write_json(filepath, item)

    @staticmethod
    def get_all_filenames_in_folder(filepath):
        """
        Get a list of all filenames in a folder.

        Arguments:
        - filepath: The path to the folder.

        Returns:
        - A list of filenames in the folder.
        """
        if not os.path.exists(filepath):
            return []
        return os.listdir(filepath)
    
    @staticmethod
    def clear_folder_contents(dirpath, *exceptions):
        """
        Clear the contents of a folder, excluding specified filenames.

        Arguments:
        - dirpath: The path to the folder to clear.
        - *exceptions: Filenames to exclude from deletion.
        """
        if not os.path.exists(dirpath):
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
        if not (os.path.exists(filepath)):
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
        if os.path.exists(src_path) and not os.path.exists(dst_path):
            shutil.copyfile(src_path, dst_path)
