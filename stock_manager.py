from imports import *
from stock import Stock

class StockManager:

    def add_stock(self, name: str): # adds new blank stock, saves as json

        new_stock_file_path = os.path.join(stock_path, name)
        
        if os.path.exists(new_stock_file_path):
            raise FileExistsError(f"A stock folder with the name {name} already exists.")
        
        os.makedirs(new_stock_file_path)
        
        new_stock_json_path = new_stock_file_path+'data.json'

        new_stock = Stock(new_stock_json_path, new_stock_file_path)

        with open(new_stock_json_path, "w") as json_file:
            json.dump(new_stock.to_json(), json_file, indent=4)

    def delete_stock(self, name: str):

        new_stock_file_path = os.path.join(stock_path, name)
        
        if os.path.exists(new_stock_file_path):
            os.remove(new_stock_file_path)

