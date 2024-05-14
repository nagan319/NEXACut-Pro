import os
import shutil
import json
import csv
from typing import List, Dict, Union, Any

class FileProcessor:

    @staticmethod
    def read_file(filepath: str) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        _, extension = os.path.splitext(filepath)

        if not os.path.exists(filepath):
            return 
        if extension.lower() == '.csv':
            return FileProcessor._read_csv(filepath)
        if extension.lower() == '.json':
            return FileProcessor._read_json(filepath)

    @staticmethod
    def _read_csv(filepath: str) -> List[Dict[str, Any]]:
        with open(filepath, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            data = list(reader)    
        return data

    @staticmethod
    def _read_json(filepath: str) -> Dict[str, Any]:
        with open(filepath, 'r') as file:
            data = json.load(file)
        return data

    @staticmethod
    def write_file(filepath: str, data, format='csv'):
        _, extension = os.path.splitext(filepath)

        if extension.lower() == '.csv' and format == 'csv':
            FileProcessor._write_csv(filepath, data)
            return
        if extension.lower() == '.json' and format == 'json':
            FileProcessor._write_json(filepath, data)
            return

    @staticmethod
    def _write_csv(filepath: str, data: list):
        with open(filepath, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

    @staticmethod
    def _write_json(filepath: str, data: dict):
        with open(filepath, 'w') as file:
            json.dump(data, file, indent=4)

    @staticmethod
    def read_all_json_in_folder(folder_path: str) -> List[Dict[str, Any]]:
        if not os.path.exists(folder_path):
            return

        data = []
        files: list[str] = FileProcessor.get_all_filenames_in_folder(folder_path)

        for filename in files:
            _, extension = os.path.splitext(filename)
            if extension.lower() != '.json':
                continue
            filepath = os.path.join(folder_path, filename)
            data.append(FileProcessor._read_json(filepath))

        return data

    @staticmethod
    def write_multiple_json_to_folder(data: list, folder_path: str):
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
    def get_all_filenames_in_folder(filepath: str) -> List[str]: 
        if not os.path.exists(filepath):
            return []
        return os.listdir(filepath)
    
    @staticmethod
    def clear_folder_contents(dirpath: str, *exceptions: str):
        if not os.path.exists(dirpath):
            return
        
        for filename in os.listdir(dirpath):
            if filename not in exceptions:
                filepath = os.path.join(dirpath, filename)
                os.remove(filepath)

    @staticmethod
    def remove_file(filepath: str):
        if not (os.path.exists(filepath)):
            return
        os.remove(filepath)

    @staticmethod
    def copy_file(src_path: str, dst_path: str):
        if os.path.exists(src_path) and not os.path.exists(dst_path):
            shutil.copyfile(src_path, dst_path)
