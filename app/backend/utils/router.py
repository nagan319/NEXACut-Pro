

class Router:
    
    def __init__(self, filename, preview_path, name, machineable_area_x, machineable_area_y, machineable_area_z, max_plate_size_x, max_plate_size_y, max_plate_size_z, min_safe_distance_from_edge, drill_bit_diameter, mill_bit_diameter):

        self.filename = filename
        self.preview_path = preview_path
        self.name = name
        self.machineable_area_x = machineable_area_x
        self.machineable_area_y = machineable_area_y
        self.machineable_area_z = machineable_area_z
        self.max_plate_size_x = max_plate_size_x
        self.max_plate_size_y = max_plate_size_y
        self.max_plate_size_z = max_plate_size_z
        self.min_safe_distance_from_edge = min_safe_distance_from_edge
        self.drill_bit_diameter = drill_bit_diameter
        self.mill_bit_diameter = mill_bit_diameter

 