from imports import *

class Stock:
    def __init__(self, json_path, folder_path):
        self.json_path = json_path
        self.folder_path = folder_path
        self.stock = []
    
    def to_json(self):
        return {
            "json_path": self.json_path,
            "folder_path": self.folder_path,
            "stock": self.stock
        }
