import os
import shutil
import json
from typing import Tuple

from common.constants import *

# not all os use '/' divider, therefore path cannot be directly defined in constants
USER_PREFERENCE_PATH = os.path.join(PREFERENCE_DIRECTORY, USER_PREFERENCE_FILE)
DEFAULT_PREFERENCE_PATH = os.path.join(PREFERENCE_DIRECTORY, DEFAULT_PREFERENCE_FILE)

# all units to be stored in mm, input in inches converted automatically
class Controller:

    def __init__(self): # copies user properties to file
        self.new_parts = []
        self.new_plates = []

    # adding new parts to machine

    def add_new_part_to_tray(self, path: str): # further checks for file 'flatness' etc will be carried out upon conversion to stl

        try:
            if not os.path.exists(path):
                raise FileNotFoundError(f"The file {path} does not exist")
            
            _, extension = os.path.splitext(path)
            extension = extension.lower()[1:] # stored w/o '.'
            if extension not in SUPPORTED_PART_FORMATS:
                raise TypeError(f"The file {path} must be converted to a supported part format")

        except (FileNotFoundError, TypeError) as e:
            print(e)
            return
        
        else:
            self.new_parts.append(path)

    def add_new_plate_to_tray(self, path: str):

        try:
            if not os.path.exists(path):
                raise FileNotFoundError(f"The file {path} does not exist")
            
            _, extension = os.path.splitext(path)
            extension = extension.lower()[1:]  

            if extension not in SUPPORTED_IMAGE_FORMATS: 
                raise TypeError(f"The file {path} must be converted to a supported image format")
            
            self.new_plates.append(path)

        except (FileNotFoundError, TypeError) as e:
            print(e)
            return
