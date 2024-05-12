import os
import math
from collections import defaultdict
from stl import mesh
from typing import Tuple, List
from enum import Enum
import numpy as np
import matplotlib.pyplot as plt

MIN_QUANTIZED_VALUE = 0.01
MIN_QUANTIZED_VALUE_DECIMALS = 2
MIN_POINT_DISTANCE = 10

VectorArrayShape = Tuple[float, float, float]
EdgeShape = Tuple[Tuple[float, float], Tuple[float, float]]

class Axis(Enum):
    X = 0
    Y = 1
    Z = 2

class STLParser: 
    '''
    Converts a valid STL file into a numpy ndarray consisting of a reasonable number of points for use in a 2D packing algorithm.
    Utilizes the Mesh class from the numpy-stl library for processing.
    The mesh is converted to vector format during initialization, resulting in a shape of (Nfacets, Nvertices == 3, Ncoordinates == 3).
    
    Criteria for a valid STL file:
    - Must be in ASCII format.
    - File must represent a single 2D shape extruded along a third axis, which aligns with the x, y, or z axis.
    - Files with improper orientation may produce erroneous results (a stricter check will be added in future versions).

    Output values:
    - Flat axis (int in range 0-2): Represents the axis along which there is a minimum number of unique points, rounded to a tolerance threshold.    
    - Thickness (float): Represents the distance between the minimum and maximum point along the flat axis.
    - Flattened mesh (np array): Represents the mesh with all coordinates along the flat axis set to 0.
    - Outer edges (list of tuples): Represents an unsorted list of the outer edges of the polygon.
    - Outer contour (np array): Contour created frmo edges with largest bounding box
    The outer contour is refined to include an amount of vertices appropriate for processing
    '''

    def __init__(self, src_path: str, cad_preview_dst: str = None, bg_color: str='#ffffff', text_color: str='#000000', plot_color: str='#000000'):
        if not os.path.exists(src_path):
            raise FileNotFoundError(f"STL file {src_path} does not exist") 
        if not STLParser.stl_file_valid(src_path):
            raise ValueError(f"STL file {src_path} is invalid")

        if cad_preview_dst:
            png_filename = os.path.basename(src_path)[:-4] + ".png" 
            self.png_filepath: str = os.path.join(cad_preview_dst, png_filename)
        else:
            self.png_filepath: str = None

        self.stl_filepath: str = src_path

        self.bg_color: str = bg_color
        self.text_color: str = text_color
        self.plot_color: str = plot_color
        
        self.stl_mesh: np.array = mesh.Mesh.from_file(self.stl_filepath)
        self.stl_mesh_vector: np.array = np.array(self.stl_mesh.vectors)
        
        if not STLParser.stl_mesh_valid(self.stl_mesh_vector):
            raise ValueError(f"STL file {self.stl_filepath} must be in mesh vector format.")
        
        self._parse_stl()

    def _parse_stl(self):
        self.flat_axis: Axis = STLParser.get_flat_axis(self.stl_mesh_vector)
        self.thickness: float = STLParser.get_thickness(self.stl_mesh_vector, self.flat_axis)
        self.flattened_mesh: np.array = STLParser.get_flattened_mesh(self.stl_mesh_vector, self.flat_axis)
        self.outer_edges: List[EdgeShape] = STLParser.get_outer_edges(self.flattened_mesh, self.flat_axis)
        self.contours: List[np.array] = STLParser.get_contours(self.outer_edges)
        self.outer_contour: np.array = STLParser.get_outermost_contour(self.contours)
        self.outer_contour = STLParser.get_smooth_contour(self.outer_contour)

    @staticmethod
    def stl_file_valid(filepath: str) -> bool:
        try: 
            mesh.Mesh.from_file(filepath)
            return True
        except Exception:
            return False
    
    @staticmethod
    def axis_valid(axis: Axis) -> bool:
        return axis in Axis

    @staticmethod
    def stl_mesh_valid(stl_mesh: np.array) -> bool:
        expected_shape: VectorArrayShape = (Ellipsis, 3, 3)
        return stl_mesh.shape == expected_shape

    @staticmethod # assumes valid mesh
    def get_flat_axis(stl_mesh: np.array, tolerance: int = MIN_QUANTIZED_VALUE_DECIMALS) -> Axis:
        coordinates = np.round([stl_mesh[:, :, i] for i in range(3)], tolerance)
        unique_counts = [np.unique(coordinates[i]).size for i in range(3)] 
        flat_axis_index = np.argmin(unique_counts)
        return Axis(flat_axis_index)

    @staticmethod # assumes valid mesh
    def get_thickness(stl_mesh: np.array, flat_axis: Axis, tolerance: int = MIN_QUANTIZED_VALUE_DECIMALS) -> float:
        flat_axis_coordinates = np.round(stl_mesh[:, :, flat_axis.value], tolerance)
        unique_points = np.unique(flat_axis_coordinates)
        thickness = max(unique_points) - min(unique_points) 
        return thickness

    @staticmethod # assumes valid mesh
    def get_flattened_mesh(stl_mesh: np.array, flat_axis: Axis, tolerance: float = MIN_QUANTIZED_VALUE) -> np.array: 
        if flat_axis not in Axis:
            raise ValueError(f"Invalid axis {flat_axis}")
        if tolerance <= 0:
            raise ValueError("Tolerance must be positive value")
        
        absolute_values = np.abs(stl_mesh[:, :, flat_axis.value])
        mask = np.all(absolute_values <= tolerance, axis=1)
        flattened_mesh = stl_mesh[mask]  
        return flattened_mesh

    @staticmethod # assumes valid mesh
    def get_outer_edges(flattened_mesh: np.array, flat_axis: Axis) -> List[EdgeShape]:
        if flat_axis not in Axis:
            raise ValueError(f"Invalid axis {flat_axis}")

        edges = []

        for facet in flattened_mesh:
            for i in range(3): 
                point1 = [facet[i][j] for j in range(3) if j != flat_axis.value] 
                point2 = [facet[(i+1)%3][j] for j in range(3) if j != flat_axis.value]
                edge = tuple(sorted([tuple(point1), tuple(point2)]))
                edges.append(edge)

        edge_counts = defaultdict(int) # outer edges are only part of one facet
        for edge in edges:
            edge_counts[edge] += 1
        
        outer_edges = [edge for edge, count in edge_counts.items() if count == 1] 
        return outer_edges 

    @staticmethod
    def get_contours(outer_edges: List[EdgeShape]) -> List[np.array]:

        points = defaultdict(list) 

        for edge in outer_edges:
            for i, point in enumerate(edge): 
                points[point].append(edge[(i+1)%2])

        contours = []
        iter_list = list(points)
        while iter_list:
            point = iter_list[0]
            current_contour = []
            while True:
                current_contour.append(list(point))
                next_point_options = points[point] 
                next_point = next_point_options[0] 
                points.pop(point) 
                iter_list.remove(point)
                if not points[next_point]: 
                    break
                points[next_point].remove(point) 
                point = next_point
            contours.append(np.array(current_contour))

        return contours

    @staticmethod
    def get_outermost_contour(contours: List[np.array]) -> np.array: 
        max_area = 0
        outermost_contour = None

        for contour in contours: 
            min_x, max_x, min_y, max_y = STLParser._get_bounding_box(contour)
            area = (max_x - min_x) * (max_y - min_y)
            if area > max_area:
                max_area = area
                outermost_contour = contour

        return outermost_contour
    
    @staticmethod
    def _get_bounding_box(contour: np.array) -> np.array:
        min_x, max_x = np.min(contour[:, 0]), np.max(contour[:, 0])
        min_y, max_y = np.min(contour[:, 1]), np.max(contour[:, 1])
        return np.array([min_x, max_x, min_y, max_y])

    @staticmethod
    def get_smooth_contour(contour: np.array) -> np.array: 
        contour = STLParser._remove_contour_points(contour)
        contour = STLParser._add_contour_points(contour)
        return contour

    @staticmethod
    def _remove_contour_points(contour: np.array) -> np.array: 
        new_contour = [contour[0]]

        point_a = contour[0]
        for point_b in contour[1:]:
            if np.linalg.norm(point_b - point_a) > MIN_POINT_DISTANCE:
                new_contour.append(point_a)
                point_a = point_b

        if np.linalg.norm(contour[-1] - contour[0]) > MIN_POINT_DISTANCE:
            new_contour.append(contour[-1])

        return np.array(new_contour)

    @staticmethod
    def _add_contour_points(contour: np.array): 
        new_contour = []

        contour = tuple(map(tuple, contour)) 

        for i in range(len(contour)):
            point_a = np.array(contour[i])
            point_b = np.array(contour[0]) if i == len(contour)-1 else np.array(contour[i+1])
            angle = math.atan2(point_b[1]-point_a[1], point_b[0]-point_a[0])

            curr_point = point_a
            while True:
                distance =  np.linalg.norm(point_b-curr_point)
                if distance < 2 * MIN_POINT_DISTANCE:
                    new_contour.append(tuple(point_b))
                    break
                curr_point += (MIN_POINT_DISTANCE * math.cos(angle), MIN_POINT_DISTANCE * math.sin(angle))
                new_contour.append(tuple(curr_point))

        return np.array(new_contour)

    def save_preview_image(self, scale_factor: float = 1, figsize: tuple = (3.9, 3.75), dpi: int = 80): 

        if not self.png_filepath: 
            return

        if os.path.exists(self.png_filepath): 
            return

        plt.figure(figsize=figsize)

        for edge in self.outer_edges:
            x_values, y_values = zip(*edge)
            if scale_factor != 1:
                x_values = tuple([x * scale_factor for x in x_values])
                y_values = tuple([y * scale_factor for y in y_values])
            plt.plot(x_values, y_values, color=self.plot_color)

        plt.xlabel('Z: ' + str(self.thickness) + ' mm', fontsize=10, labelpad=5, horizontalalignment='center')

        plt.grid(True)
        plt.gca().set_facecolor(self.bg_color) 
        plt.gca().set_aspect('equal') 
        plt.grid(False)
        plt.tick_params(axis='x', colors=self.text_color)  
        plt.tick_params(axis='y', colors=self.text_color) 

        plt.gca().spines['top'].set_color(self.text_color) 
        plt.gca().spines['bottom'].set_color(self.text_color)
        plt.gca().spines['left'].set_color(self.text_color)
        plt.gca().spines['right'].set_color(self.text_color)

        plt.savefig(self.png_filepath, bbox_inches='tight', facecolor='#FFFFFF', dpi=dpi) 
