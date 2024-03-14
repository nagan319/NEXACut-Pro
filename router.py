from imports import *

class Router:
    def __init__(self, path, machineable_area, max_plate_size, min_safe_distance_from_edge, drill_bit_diameter, mill_bit_diameter):
        self.path = path
        self.machineable_area = machineable_area
        self.max_plate_size = max_plate_size
        self.min_safe_distance_from_edge = min_safe_distance_from_edge
        self.drill_bit_diameter = drill_bit_diameter
        self.mill_bit_diameter = mill_bit_diameter
    
    def to_json(self):
        return {
            "machineable_area": self.machineable_area,
            "max_plate_size": self.max_plate_size,
            "min_safe_distance_from_edge": self.min_safe_distance_from_edge,
            "drill_bit_diameter": self.drill_bit_diameter,
            "mill_bit_diameter": self.mill_bit_diameter
        }
