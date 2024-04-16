SUPPORTED_IMAGE_EXTENSIONS = ['bmp', 'dib', 'jpeg', 'jpg', 'jp2', 'png', 'webp', 'avif']
SUPPORTED_IMAGE_FORMATS = "Image Files (*.bmp *.dib *.jpeg *.jpg *.jp2 *.png *.webp *.avif)" # for QFileDialog
MAX_PROCESSING_WIDTH = 2000
MAX_PROCESSING_HEIGHT = 2000
MAX_PPMM = 4 # pixels/mm for final image

RAW_EXTENSION = 'raw.png'
BINARY_EXTENSION = 'bin.png'
CONTOUR_EXTENSION = 'ctr.png'
FLATTENED_EXTENSION = 'flat.png'

NONE_STATE = 0
RAW_STATE = 1
BINARY_STATE = 2
CONTOUR_STATE = 3
FLATTENED_STATE = 4

MIN_CONTOUR_AREA = 1500
MIN_CONTOUR_DISTANCE_FROM_EDGE = 100

CORNER_SEARCH_POINT_DELTA = 16
MIN_CORNER_ANGLE = 60
MIN_CORNER_SEPARATION = 120

COLOR_DELETION_THRESHOLD = 32

RAW_EXTENSION = 'raw.png'
BINARY_EXTENSION = 'bin.png'
CONTOUR_EXTENSION = 'contours.png'
FLATTENED_EXTENSION = 'flattened.png'

DEFAULT_COLORS = {
    'background_color': (255, 255, 255),
    'contour_color': (100, 100, 100),
    'selected_element_color': (255, 0, 0),
    'plate_edge_color': (0, 0, 0),
    'corner_color': (0, 255, 0)
}