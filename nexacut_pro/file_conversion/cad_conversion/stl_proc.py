import sys
import os
import numpy as np
from collections import defaultdict
from stl import mesh

from constants import MIN_QUANTIZED_VALUE, MIN_VALUE_DECIMAL_DIGITS

def is_valid_stl(file_path):
    if not os.path.exists(file_path):
        return False
    
    try: 
        stl_mesh = mesh.Mesh.from_file(file_path)
        return True

    except Exception as e:
        return False
    
def is_valid_axis(axis: int):
    return axis >= 0 and axis <= 2

def is_stl_format_valid(stl_mesh):
    for facet in stl_mesh:
        if facet.shape != (3, 3):
            return False
    return True

# all below methods require stl in .vectors form

def determine_axis_to_flatten(stl_mesh): # assumes valid mesh

    if not is_stl_format_valid:
        raise ValueError("STL mesh of wrong shape")

    x_coordinates, y_coordinates, z_coordinates = [], [], []

    for facet in stl_mesh:
        for point in facet:
            x, y, z = point
            x_coordinates.append(round(x, MIN_VALUE_DECIMAL_DIGITS))
            y_coordinates.append(round(y, MIN_VALUE_DECIMAL_DIGITS))
            z_coordinates.append(round(z, MIN_VALUE_DECIMAL_DIGITS))

    x_unique_count = len(set(x_coordinates))
    y_unique_count = len(set(y_coordinates))
    z_unique_count = len(set(z_coordinates))

    max_unique_count = max(x_unique_count, y_unique_count, z_unique_count)
    if max_unique_count == x_unique_count:
        return 0  # x
    elif max_unique_count == y_unique_count:
        return 1  # y
    else:
        return 2  # z

def flatten_stl(stl_mesh, axis: int = 2, tolerance: float = MIN_QUANTIZED_VALUE): 
    if not is_valid_axis(axis):
        raise ValueError("Axis must be in range 0-2")
    if not is_stl_format_valid:
        raise ValueError("STL mesh of wrong shape")
    if tolerance < 0:
        raise ValueError("Positive value expected for tolerance")

    flattened_mesh = []

    for facet in stl_mesh: 
        all_zero = True
        for point in facet:
            if abs(point[axis]) > tolerance:
                all_zero = False
            if all_zero:
                flattened_mesh.append(facet)
    
    return np.array(flattened_mesh, dtype=np.float32)

def get_outer_edges(stl_mesh, flat_axis: int = 2, tolerance: int = MIN_VALUE_DECIMAL_DIGITS):

    if not is_valid_axis(flat_axis):
        raise ValueError("Axis must be in range 0-2")
    if not is_stl_format_valid:
        raise ValueError("STL mesh of wrong shape")
    if abs(tolerance) > MIN_VALUE_DECIMAL_DIGITS:
        raise ValueError(f"Tolerance value out of range {MIN_VALUE_DECIMAL_DIGITS}")
    
    edge_counts = defaultdict(int)
    edges = []

    for facet in stl_mesh:
        new_facet = []
        for point in facet:
            new_point = [coordinate for i, coordinate in enumerate(point) if i != flat_axis]
            new_facet.append(round(new_point, tolerance))
        
        for i in range(3):
            point1 = tuple([round(facet[i][0], tolerance), round(facet[i][1], tolerance)])
            point2 = tuple([round(facet[(i+1)%3][0], tolerance), round(facet[(i+1)%3][1], tolerance)])
            new_edge = tuple(sorted([point1, point2])) # tuple of lists unhashable
            edges.append(new_edge)
        
        for edge in edges:
            edge_counts[edge] += 1
        
        outer_edges = []

        for edge, count in edge_counts.items():
            if count == 1:
                outer_edges.append(edge)
        
        return outer_edges
