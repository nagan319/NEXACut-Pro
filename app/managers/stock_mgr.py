import os
import json
import shutil

class StockManager:

    def __init__(self, stock_data_folder: str):
        self.stock_directory = stock_data_folder
        self.update_properties()

    def new_stock(self, name: str): # adds new blank stock, saves as json

        new_stock_file_path = os.path.join(STOCK_DIRECTORY, name)
        
        try:
            if os.path.exists(new_stock_file_path):
                raise FileExistsError(f"A stock folder with the name {name} already exists.")
            
        except(FileExistsError) as e:
            print(e)
            return
        
        else: 
            os.makedirs(new_stock_file_path)
            
            new_stock_json_path = new_stock_file_path+'/data.json'

            new_stock = Stock(new_stock_json_path, new_stock_file_path)

            with open(new_stock_json_path, "w") as json_file:
                json.dump(new_stock.to_json(), json_file, indent=4)

    def delete_stock(self, name: str):
        stock_folder_path = os.path.join(STOCK_DIRECTORY, name)
        
        try:
            if os.path.exists(stock_folder_path):
                shutil.rmtree(stock_folder_path) # removes entire folder as opposed to single file
            else:
                raise FileNotFoundError(f"The stock {name} does not exist")
            
        except(FileNotFoundError) as e:
            print(e)
            return
        
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
