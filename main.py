from imports import *
from stock_manager import StockManager
from router_manager import RouterManager
from controller import Controller

def initialize_application():

    try:
        controller = Controller()
        router_manager = RouterManager()
        stock_manager = StockManager()
        return controller, router_manager, stock_manager
    
    except Exception as e:
        print("An error occurred during initialization:", e)

if __name__ == "__main__":
    controller, router_manager, stock_manager = initialize_application()
    router_manager.delete_router("OMIO 2200")
    # stock_manager.delete_stock("6560 Stock") # returns permission error