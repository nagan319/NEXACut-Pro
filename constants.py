# file paths

user_preferences_path = 'Preferences/user_preferences.json'
default_preferences_path = 'Preferences/default_preferences.json'
routers_path = 'Routers/'
stock_path = 'Stock/'
preview_path = 'Image Preview/'

# image properties

supported_image_formats = ['bmp', 'dib', 'jpeg', 'jpg', 'jp2', 'png', 'webp', 'avif']
processing_max_width = 2000
processing_max_height = 2000
max_resolution = 4 # pixels/mm for final image

raw_extension = 'raw.png'
binary_extension = 'bin.png'
contour_extension = 'ctr.png'
flattened_extension = 'flat.png'

none_state = 0
raw_state = 1
binary_state = 2
contour_state = 3
flattened_state = 4

corner_search_point_delta = 16
min_corner_angle = 60
min_corner_separation = 120 # corner distance from each other for removing duplicates

supported_part_formats = ['stl']

# machine hard limits

router_max_dimension = 5000
plate_max_dimension = 5000
drill_bit_max_size = 100
mill_bit_max_size = 100