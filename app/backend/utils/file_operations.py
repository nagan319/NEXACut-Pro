import os
import shutil
import json

class FileProcessor:

    def get_json_data(self, filepath: str): # extract data from json

        if not os.path.exists(filepath):
            return 
        
        if os.path.splitext(filepath)[1].lower() != '.json':
            return
        
        with open(filepath, 'r') as file:
            data = json.load(file)
        
        return data
    
    def save_json(self, filepath: str, data: dict): # saves dict to json
        
        if os.path.splitext(filepath)[1].lower() != '.json':
            return

        with open(filepath, 'w') as file:
            json.dump(data, file, indent=4)


    def get_all_json_in_folder(self, folder_path: str) -> list:

        if not os.path.exists(folder_path):
            return

        data = []

        files = self.load_folder_contents(folder_path)

        for file in files:
            file_path = os.path.join(folder_path, file)
            data.append(self.get_json_data(file_path))
        
        return data

    def save_all_json_to_folder(self, data: list, folder_path: str):

        if not os.path.exists(folder_path):
            return
        
        for item in data:
            if type(item) != dict:
                return
            try:
                temp = item['filename']
            except KeyError:
                return
        
        self.clear_folder_contents(folder_path)

        for i, _ in enumerate(data):
            filename = data[i]['filename']
            filepath = os.path.join(folder_path, filename)
            self.save_json(filepath, data[i])


    def load_folder_contents(self, filepath: str): # get filenames in folder

        if not os.path.exists(filepath):
            return []
        
        return os.listdir(filepath)
    
    def clear_folder_contents(self, dirpath: str, *exceptions: str): # clears directory except certain files

        if not os.path.exists(dirpath):
            return
        
        for filename in os.listdir(dirpath):
            if filename not in exceptions:
                filepath = os.path.join(dirpath, filename)
                os.remove(filepath)


    def delete_file(self, filepath: str):

        if not (os.path.exists(filepath)):
            return
        
        os.remove(filepath)

    def copy_file(self, src_path: str, dst_path: str):

        if os.path.exists(src_path) and not os.path.exists(dst_path):
            shutil.copyfile(src_path, dst_path)
