from controller import *

def initialize_application():

    try:
        controller = Controller()
    
    except Exception as e:
        print("An error occurred during initialization:", e)

if __name__ == "__main__":
    controller = initialize_application()