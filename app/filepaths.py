import os

CURRENT_DIR = os.path.dirname(__file__)

STYLESHEET_FOLDER = 'stylesheets'
STYLESHEET_FOLDER_PATH = os.path.join(CURRENT_DIR, STYLESHEET_FOLDER)

DATA_FOLDER = 'data'
DATA_FOLDER_PATH = os.path.join(CURRENT_DIR, DATA_FOLDER)

CAD_PREVIEW_DATA_FOLDER = 'cad_preview_data'
CAD_PREVIEW_DATA_PATH = os.path.join(DATA_FOLDER_PATH, CAD_PREVIEW_DATA_FOLDER)

PART_IMPORT_DATA_FOLDER = 'part_import_data'
PART_IMPORT_DATA_PATH = os.path.join(DATA_FOLDER_PATH, PART_IMPORT_DATA_FOLDER)

STOCK_DATA_FOLDER = 'stock_data'
STOCK_DATA_FOLDER_PATH = os.path.join(DATA_FOLDER_PATH, STOCK_DATA_FOLDER)

ROUTER_DATA_FOLDER = 'router_data'
ROUTER_DATA_FOLDER_PATH = os.path.join(DATA_FOLDER_PATH, ROUTER_DATA_FOLDER)

PREFERENCE_DATA_FOLDER = 'preference_data'
PREFERENCE_DATA_FOLDER_PATH = os.path.join(CURRENT_DIR, DATA_FOLDER, PREFERENCE_DATA_FOLDER)

USER_PREFERENCE_FILE = 'user_preferences.json'
USER_PREFERENCE_FILE_PATH = os.path.join(PREFERENCE_DATA_FOLDER_PATH, USER_PREFERENCE_FILE)

DEFAULT_PREFERENCE_FILE = 'default_preferences.json'
DEFAULT_PREFERENCE_FILE_PATH = os.path.join(PREFERENCE_DATA_FOLDER_PATH, DEFAULT_PREFERENCE_FILE)