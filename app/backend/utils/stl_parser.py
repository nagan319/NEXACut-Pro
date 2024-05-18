import os
import math
import logging
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
    """
    Converts a valid STL file into a numpy ndarray consisting of a reasonable number of points for use in a 2D packing algorithm.
    Utilizes the Mesh class from the numpy-stl library for processing.
    The mesh is converted to vector format during initialization, resulting in a shape of (Nfacets, Nvertices == 3, Ncoordinates == 3).
    
    ### Criteria for a valid STL file:
    - Must be in ASCII format.
    - File must represent a single 2D shape extruded along a third axis, which aligns with the x, y, or z axis.
    - Files with improper orientation may produce erroneous results (a stricter check will be added in future versions).

    ### Attributes:
    - Flat axis (int in range 0-2): Represents the axis along which there is a minimum number of unique points, rounded to a tolerance threshold.    
    - Thickness (float): Represents the distance between the minimum and maximum point along the flat axis.
    - Flattened mesh (np array): Represents the mesh with all coordinates along the flat axis set to 0.
    - Outer edges (list of tuples): Represents an unsorted list of the outer edges of the polygon.
    - Outer contour (np array): Contour created from edges with largest bounding box
    The outer contour is refined to include an amount of vertices appropriate for processing.

    ### Raises:
    - FileNotFoundError if file path is invalid.
    - FileNotFoundError if destination folder path is not found.
    - ValueError if STL file is invalid. 
    - ValueError if STL mesh is invalid. 
    """

    BG_COLOR: str = "#ffffff"
    TEXT_COLOR: str = '#000000'
    PLOT_COLOR: str = '#000000'

    def __init__(self, src_path: str, dst_folder: str):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(logging.StreamHandler())
        self.logger.info(f"@{self.__class__.__name__}: Initializing STLParser with source path: {src_path}")

        self.parsing_complete = False

        if not os.path.exists(src_path):
            self.logger.error(f"@{self.__class__.__name__}: STL file {src_path} does not exist") 
            raise FileNotFoundError(f"@{self.__class__.__name__}: STL file {src_path} does not exist") 
        
        if not STLParser.stl_file_valid(src_path):
            self.logger.error(f"@{self.__class__.__name__}: STL file {src_path} is invalid")
            raise ValueError(f"@{self.__class__.__name__}: STL file {src_path} is invalid")

        if not os.path.exists(dst_folder):
            self.logger.error(f"@{self.__class__.__name__}: Destination folder path {dst_folder} does not exist")
            raise FileNotFoundError(f"@{self.__class__.__name__}: Destination folder path {dst_folder} does not exist")

        self.stl_filepath: str = src_path
        self.stl_mesh: np.array = mesh.Mesh.from_file(self.stl_filepath)
        self.stl_mesh_vector: np.array = np.array(self.stl_mesh.vectors)
        
        if not STLParser.stl_mesh_valid(self.stl_mesh_vector):
            e = f"@{self.__class__.__name__}: STL file {self.stl_filepath} must be in mesh vector format. Current shape is {self.stl_mesh_vector.shape}"
            self.logger.error(e)
            raise ValueError(e)

        self.dst_path = os.path.join(dst_folder, os.path.basename(self.stl_filepath)+'.png') 

    def parse_stl(self):
        """"
        Parses STL file and sets class attributes
        """
        self.logger.info(f"@{self.__class__.__name__}: Parsing STL file...")
        self.logger.info(f"@{self.__class__.__name__}: Finding flat axis...")
        self.flat_axis: Axis = STLParser.get_flat_axis(self.stl_mesh_vector)
        self.logger.info(f"@{self.__class__.__name__}: Calculating thickness...")
        self.thickness: float = STLParser.get_thickness(self.stl_mesh_vector, self.flat_axis)
        self.logger.info(f"@{self.__class__.__name__}: Flattening mesh...")
        self.flattened_mesh: np.array = STLParser.get_flattened_mesh(self.stl_mesh_vector, self.flat_axis)
        self.logger.info(f"@{self.__class__.__name__}: Finding outer edges...")
        self.outer_edges: List[EdgeShape] = STLParser.get_outer_edges(self.flattened_mesh, self.flat_axis)
        self.logger.info(f"@{self.__class__.__name__}: Finding contours...")
        self.contours: List[np.array] = STLParser.get_contours(self.outer_edges)
        self.logger.info(f"@{self.__class__.__name__}: Finding outermost contour...")
        self.outer_contour: np.array = STLParser.get_outermost_contour(self.contours)
        self.logger.info(f"@{self.__class__.__name__}: Smoothing contour...")
        self.outer_contour = STLParser.get_smooth_contour(self.outer_contour)
        self.parsing_complete = True
        self.logger.info(f"@{self.__class__.__name__}: Parsing complete.")

    @staticmethod
    def stl_file_valid(filepath: str) -> bool:
        """
        Check if an STL file is valid.

        - filepath: Path to the STL file.

        Returns:
        - True if the STL file is valid, False otherwise.
        """
        try:
            mesh.Mesh.from_file(filepath)
            return True
        except Exception:
            return False

    @staticmethod
    def stl_mesh_valid(stl_mesh: np.array) -> bool:
        """
        Check if an STL mesh is valid.

        - stl_mesh: The STL mesh to validate.

        Returns:
        - True if the STL mesh is valid, False otherwise.
        """
        return len(stl_mesh.shape) == 3 and stl_mesh.shape[1:] == (3, 3)

    @staticmethod
    def get_flat_axis(stl_mesh: np.array, tolerance: int = MIN_QUANTIZED_VALUE_DECIMALS) -> Axis:
        """
        Get the flat axis of an STL mesh.

        - stl_mesh: The STL mesh.
        - tolerance: Tolerance for rounding coordinates.

        Returns:
        - The flat axis as an Axis enum.
        """
        coordinates = np.round([stl_mesh[:, :, i] for i in range(3)], tolerance)
        unique_counts = [np.unique(coordinates[i]).size for i in range(3)]
        flat_axis_index = np.argmin(unique_counts)
        return Axis(flat_axis_index)

    @staticmethod
    def get_thickness(stl_mesh: np.array, flat_axis: Axis, tolerance: int = MIN_QUANTIZED_VALUE_DECIMALS) -> float:
        """
        Get the thickness of an STL mesh along a flat axis.

        - stl_mesh: The STL mesh.
        - flat_axis: The flat axis as an Axis enum.
        - tolerance: Tolerance for rounding coordinates.

        Returns:
        - The thickness as a float.
        """
        flat_axis_coordinates = np.round(stl_mesh[:, :, flat_axis.value], tolerance)
        unique_points = np.unique(flat_axis_coordinates)
        thickness = max(unique_points) - min(unique_points)
        return float(thickness)

    @staticmethod
    def get_flattened_mesh(stl_mesh: np.array, flat_axis: Axis, tolerance: float = MIN_QUANTIZED_VALUE) -> np.array:
        """
        Get a flattened version of an STL mesh along a flat axis.

        - stl_mesh: The STL mesh.
        - flat_axis: The flat axis as an Axis enum.
        - tolerance: Tolerance for considering points as flat.

        Returns:
        - A flattened STL mesh as a numpy array.
        """
        if flat_axis not in Axis:
            raise ValueError(f"Invalid axis {flat_axis}")
        if tolerance <= 0:
            raise ValueError("Tolerance must be positive value")

        absolute_values = np.abs(stl_mesh[:, :, flat_axis.value])
        mask = np.all(absolute_values <= tolerance, axis=1)
        flattened_mesh = stl_mesh[mask]
        return flattened_mesh

    @staticmethod
    def get_outer_edges(flattened_mesh: np.array, flat_axis: Axis) -> List[EdgeShape]:
        """
        Get the outer edges of a flattened STL mesh.

        - flattened_mesh: The flattened STL mesh.
        - flat_axis: The flat axis as an Axis enum.

        Returns:
        - A list of outer edges as EdgeShape tuples.
        """
        if flat_axis not in Axis:
            raise ValueError(f"Invalid axis {flat_axis}")

        edges = []

        for facet in flattened_mesh:
            for i in range(3):
                point1 = [facet[i][j] for j in range(3) if j != flat_axis.value]
                point2 = [facet[(i+1)%3][j] for j in range(3) if j != flat_axis.value]
                edge = tuple(sorted([tuple(point1), tuple(point2)]))
                edges.append(edge)

        edge_counts = defaultdict(int)
        for edge in edges:
            edge_counts[edge] += 1

        outer_edges = [edge for edge, count in edge_counts.items() if count == 1]
        return outer_edges

    @staticmethod
    def get_contours(outer_edges: List[EdgeShape]) -> List[np.array]:
        """
        Get contours from a list of outer edges.

        - outer_edges: A list of outer edges as EdgeShape tuples.

        Returns:
        - A list of contours as numpy arrays.
        """
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
        """
        Get the outermost contour from a list of contours.

        - contours: A list of contours as numpy arrays.

        Returns:
        - The outermost contour as a numpy array.
        """
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
        """
        Get the bounding box of a contour.

        - contour: The contour as a numpy array.

        Returns:
        - The bounding box as a numpy array [min_x, max_x, min_y, max_y].
        """
        min_x, max_x = np.min(contour[:, 0]), np.max(contour[:, 0])
        min_y, max_y = np.min(contour[:, 1]), np.max(contour[:, 1])
        return np.array([min_x, max_x, min_y, max_y])

    @staticmethod
    def get_smooth_contour(contour: np.array) -> np.array:
        """
        Get a smoothed contour by removing and adding points.

        - contour: The contour as a numpy array.

        Returns:
        - The smoothed contour as a numpy array.
        """
        contour = STLParser._remove_contour_points(contour)
        contour = STLParser._add_contour_points(contour)
        return contour

    @staticmethod
    def _remove_contour_points(contour: np.array) -> np.array:
        """
        Remove points from a contour to smooth it.

        - contour: The contour as a numpy array.

        Returns:
        - The contour with points removed as a numpy array.
        """
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
    def _add_contour_points(contour: np.array) -> np.array:
        """
        Add points to a contour to smooth it.

        - contour: The contour as a numpy array.

        Returns:
        - The contour with points added as a numpy array.
        """
        new_contour = []

        contour = tuple(map(tuple, contour))

        for i in range(len(contour)):
            point_a = np.array(contour[i])
            point_b = np.array(contour[0]) if i == len(contour)-1 else np.array(contour[i+1])
            angle = math.atan2(point_b[1]-point_a[1], point_b[0]-point_a[0])

            curr_point = point_a
            while True:
                distance = np.linalg.norm(point_b-curr_point)
                if distance < 2 * MIN_POINT_DISTANCE:
                    new_contour.append(tuple(point_b))
                    break
                curr_point += (MIN_POINT_DISTANCE * math.cos(angle), MIN_POINT_DISTANCE * math.sin(angle))
                new_contour.append(tuple(curr_point))

        return np.array(new_contour)

    def save_image(self, scale_factor: float = 1, figsize: tuple = (3.9, 3.75), dpi: int = 80):
        """
        Save an image of the parsed STL file.

        - scale_factor: Factor to scale the image.
        - figsize: Size of the figure (width, height).
        - dpi: Dots per inch for the saved image.
        """
        if not self.parsing_complete or os.path.exists(self.dst_path):
            return

        self.logger.info(f"@{self.__class__.__name__}: Creating plot for preview image...")

        plt.figure(figsize=figsize)

        for edge in self.outer_edges:
            x_values, y_values = zip(*edge)
            if scale_factor != 1:
                x_values = tuple([x * scale_factor for x in x_values])
                y_values = tuple([y * scale_factor for y in y_values])
            plt.plot(x_values, y_values, color=STLParser.PLOT_COLOR)

        plt.xlabel('Z: ' + str(self.thickness) + ' mm', fontsize=10, labelpad=5, horizontalalignment='center')

        plt.grid(True)
        plt.gca().set_facecolor(STLParser.BG_COLOR)
        plt.gca().set_aspect('equal')
        plt.grid(False)
        plt.tick_params(axis='x', colors=STLParser.TEXT_COLOR)
        plt.tick_params(axis='y', colors=STLParser.TEXT_COLOR)

        plt.gca().spines['top'].set_color(STLParser.TEXT_COLOR)
        plt.gca().spines['bottom'].set_color(STLParser.TEXT_COLOR)
        plt.gca().spines['left'].set_color(STLParser.TEXT_COLOR)
        plt.gca().spines['right'].set_color(STLParser.TEXT_COLOR)

        self.logger.info(f"@{self.__class__.__name__}: Saving preview image...")
        plt.savefig(self.dst_path, bbox_inches='tight', facecolor='#FFFFFF', dpi=dpi)
        self.logger.info(f"@{self.__class__.__name__}: Image saved to {self.dst_path}.")
        