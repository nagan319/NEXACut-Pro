import os

"""
Application constants and filepaths.
"""

# global constants
MIN_WIDTH = 1200
MIN_HEIGHT = 1000
APP_TITLE = 'NEXACut Pro'

PART_IMPORT_LIMIT = 20
ROUTER_LIMIT = 10
PLATE_LIMIT = 40

CURRENT_DIR = os.path.dirname(__file__)

PROCESSING_SCALE_FACTOR = 5

# frontend paths
FRONTEND_FOLDER = 'frontend'
RESOURCES_FOLDER = 'resources'
FONT_FOLDER = 'fonts'
IMAGES_FOLDER = 'images'
STYLESHEET_FOLDER = 'stylesheets'
MAIN_FONT = 'Tajawal-Regular.ttf'
LOGO_IMAGE = 'NEXACut Logo.png'

# data paths
DATA_FOLDER = 'data'

PERMANENT_DATA_FOLDER = 'permanent'
PREFERENCE_DATA_FOLDER = 'preference_data'
PLATE_DATA_FILE = 'plate_data.csv'
PLATE_PREVIEW_DATA_FOLDER = 'plate_preview_data'
ROUTER_DATA_FILE = 'router_data.csv'
ROUTER_PREVIEW_DATA_FOLDER = 'router_preview_data'

TEMPORARY_DATA_FOLDER = 'temporary'
CAD_PREVIEW_DATA_FOLDER = 'cad_preview_data'
IMAGE_PREVIEW_DATA_FOLDER = 'image_preview_data'

USER_PREFERENCE_FILE = 'user_preferences.json'

# full paths
MAIN_FONT_PATH = os.path.join(CURRENT_DIR, FRONTEND_FOLDER, RESOURCES_FOLDER, FONT_FOLDER, MAIN_FONT)
LOGO_PATH = os.path.join(CURRENT_DIR, FRONTEND_FOLDER, RESOURCES_FOLDER, IMAGES_FOLDER, LOGO_IMAGE)
STYLESHEET_FOLDER_PATH = os.path.join(CURRENT_DIR, FRONTEND_FOLDER, RESOURCES_FOLDER, STYLESHEET_FOLDER)

USER_PREFERENCE_FILE_PATH = os.path.join(CURRENT_DIR, DATA_FOLDER, PERMANENT_DATA_FOLDER, PREFERENCE_DATA_FOLDER, USER_PREFERENCE_FILE)
PLATE_DATA_PATH = os.path.join(CURRENT_DIR, DATA_FOLDER, PERMANENT_DATA_FOLDER, PLATE_DATA_FILE)
PLATE_PREVIEW_DATA_PATH = os.path.join(CURRENT_DIR, DATA_FOLDER, PERMANENT_DATA_FOLDER, PLATE_PREVIEW_DATA_FOLDER)
ROUTER_DATA_PATH = os.path.join(CURRENT_DIR, DATA_FOLDER, PERMANENT_DATA_FOLDER, ROUTER_DATA_FILE)
ROUTER_PREVIEW_DATA_PATH = os.path.join(CURRENT_DIR, DATA_FOLDER, PERMANENT_DATA_FOLDER, ROUTER_PREVIEW_DATA_FOLDER)

CAD_PREVIEW_DATA_PATH = os.path.join(CURRENT_DIR, DATA_FOLDER, TEMPORARY_DATA_FOLDER, CAD_PREVIEW_DATA_FOLDER)
IMAGE_PREVIEW_DATA_PATH = os.path.join(CURRENT_DIR, DATA_FOLDER, TEMPORARY_DATA_FOLDER, IMAGE_PREVIEW_DATA_FOLDER)

TEMP_PATHS = [CAD_PREVIEW_DATA_PATH, IMAGE_PREVIEW_DATA_PATH]