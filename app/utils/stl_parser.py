import os
import json
import math
import random
import numpy as np
from collections import defaultdict
from stl import mesh
import matplotlib.pyplot as plt

MIN_QUANTIZED_VALUE = .01
MIN_VALUE_DECIMAL_DIGITS = 2

class STLParser: # convertes stl to polygon

    SUPPORTED_PART_FORMATS = ['stl']

    def __init__(self, src_path: str, cad_preview_dst: str = None, bg_color: str='#ffffff', text_color: str='#000000', plot_color: str='#000000'):

        self.stl_filepath = src_path

        if cad_preview_dst:
            self.png_name = os.path.basename(src_path)[:-4] + ".png" 
            self.preview_path = os.path.join(cad_preview_dst, self.png_name)
        else:
            self.preview_path = None

        self.bg_color = bg_color
        self.text_color = text_color
        self.plot_color = plot_color

        if not os.path.exists(self.stl_filepath):
            raise FileNotFoundError(f"STL file {self.stl_filepath} does not exist")
        
        if not self.is_valid_stl(self.stl_filepath):
            raise ValueError(f"STL file {self.stl_filepath} is invalid")
        
        self.stl_mesh = mesh.Mesh.from_file(self. stl_filepath)
        self.stl_mesh_vector_format = np.array(self.stl_mesh.vectors)
        
        if not self.is_stl_format_valid():
            raise ValueError(f"STL file {self.stl_filepath} must be in vector format")
        
        self.__init_properties__()

    def __init_properties__(self):
        self.flat_axis = self.determine_axis_to_flatten()
        self.thickness = self.get_thickness()
        self.flattened_mesh = self.flatten_stl()
        self.outer_edges = self.get_outer_edges(self.flat_axis)
        self.contours = self.get_contours()
        self.outer_contour = self.get_outermost_contour()
        self.outer_contour = self.get_smooth_contour(self.outer_contour)

    def is_valid_stl(self, file_path) -> bool:
        try: 
            stl_mesh = mesh.Mesh.from_file(file_path)
            return True
        except Exception as e:
            return False
    
    def is_valid_axis(self, axis: int) -> bool:
        return axis >= 0 and axis <= 2

    def is_stl_format_valid(self) -> bool:
        for facet in self.stl_mesh_vector_format:
            if facet.shape != (3, 3):  # Check the shape of the mesh, should be (Nfacets, Nvertices == 3, Ncoordinates == 3)
                return False
        return True

    def determine_axis_to_flatten(self, tolerance: int = MIN_VALUE_DECIMAL_DIGITS) -> tuple: # returns thickness and axis to flatten
        coordinates = np.round([self.stl_mesh_vector_format[:, :, i] for i in range(3)], tolerance) # get all rounded coordinate arrays
        unique_counts = [np.unique(coordinates[i]).size for i in range(3)] # get length of arrays
        flat_axis = np.argmin(unique_counts)
        return flat_axis

    def get_thickness(self, tolerance: int = MIN_VALUE_DECIMAL_DIGITS) -> float:
        flat_axis_coordinates = np.round(self.stl_mesh_vector_format[:, :, self.flat_axis], tolerance)
        unique_points = np.unique(flat_axis_coordinates)
        thickness = max(unique_points)-min(unique_points)
        return thickness

    def flatten_stl(self, axis: int = 2, tolerance: float = MIN_QUANTIZED_VALUE) -> np.array: # returns all facets completely on flattened plane
        if axis not in range(3):
            raise ValueError("Axis must be in range 0-2")
        if tolerance <= 0:
            raise ValueError("Tolerance must be positive value")
        
        absolute_values = np.abs(self.stl_mesh_vector_format[:, :, axis])
        mask = np.all(absolute_values <= tolerance, axis=1)
        flattened_mesh = self.stl_mesh_vector_format[mask]  # applies mask to all facets
        return flattened_mesh

    def get_outer_edges(self, flat_axis: int = 2, tolerance:int = MIN_VALUE_DECIMAL_DIGITS):
        if flat_axis not in range(3):
            raise ValueError("Axis must be in range 0-2")

        edges = []
        for facet in self.flattened_mesh:
            for i in range(3): # all edges (lines between 2 points) across all facets
                point1 = [round(facet[i][j], tolerance) for j in range(3) if j != flat_axis] # doesn't include flat axis coordinate
                point2 = [round(facet[(i+1)%3][j], tolerance) for j in range(3) if j != flat_axis]
                edge = tuple(sorted([tuple(point1), tuple(point2)]))
                edges.append(edge)

        edge_counts = defaultdict(int)
        for edge in edges:
            edge_counts[edge] += 1
        
        outer_edges = [edge for edge, count in edge_counts.items() if count == 1] # all outer edges only appear in one facet
        return outer_edges

    def save_preview_image(self, scale_factor: float = 1, figsize: tuple = (3.9, 3.75), dpi: int = 80): # scalefactor necessary for metric/imperial mode display

        if not self.preview_path: # testing run
            return

        if os.path.exists(self.preview_path): # no need to waste time
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
        plt.gca().set_facecolor(self.bg_color) # bg color
        plt.gca().set_aspect('equal') 
        plt.grid(False)
        plt.tick_params(axis='x', colors=self.text_color)  # tick color
        plt.tick_params(axis='y', colors=self.text_color) 

        plt.gca().spines['top'].set_color(self.text_color) # graph borders
        plt.gca().spines['bottom'].set_color(self.text_color)
        plt.gca().spines['left'].set_color(self.text_color)
        plt.gca().spines['right'].set_color(self.text_color)

        plt.savefig(self.preview_path, bbox_inches='tight', facecolor='#FFFFFF', dpi=dpi) # image bg color (around graph)

    def get_contours(self) -> list: # input in format [((x1, y1), (x2, y2))...], returns list of np arrays

        points = defaultdict(list) # key: point, value: all linked points

        for edge in self.outer_edges: # this creates a dictionary that will be traversed later to identify all contours
            for i, point in enumerate(edge): # both connecting points are stored
                if points[point]:
                    points[point].append(edge[(i+1)%2])
                else:
                    points[point] = [edge[(i+1)%2]]

        contours = []
        iter_list = list(points)
        while iter_list: # cycle through dictionary to find all contours
            point = iter_list[0]
            current_contour = []
            while True:
                current_contour.append(list(point))
                next_point_options = points[point] # check connected points
                next_point = next_point_options[0] # pick first one
                points.pop(point) # get rid of current point in dict
                iter_list.remove(point)
                if not points[next_point]: # reached end of contour
                    break
                points[next_point].remove(point) # remove current point from options
                point = next_point
            contours.append(np.array(current_contour))

        if len(contours) == 0:
            raise ValueError("No contours detected")

        return contours

    def get_outermost_contour(self) -> np.array: 
        max_area = 0
        outermost_contour = None

        for contour in self.contours: # area of contour bounding box is calculated, max contour is returned
            min_x, max_x, min_y, max_y = self.get_bounding_box(contour)
            area = (max_x - min_x) * (max_y - min_y)
            if area > max_area:
                max_area = area
                outermost_contour = contour

        return outermost_contour
    
    def get_smooth_contour(self, contour: np.array) -> np.array: # makes sure contour has even distribution of points for faster/more accurate comparison
        threshold1 = 10
        threshold2 = 20
        contour = self.remove_points(contour, threshold1)
        contour = self.add_points(contour, threshold2)
        return contour

    def remove_points(self, contour: np.array, threshold: int): # removes points in areas where density is too high
        if threshold <= 0:
            raise ValueError("Invalid threshold value")

        new_contour = []

        point_a = contour[0]
        for point_b in contour[1:]:
            if np.linalg.norm(point_b - point_a) > threshold:
                new_contour.append(point_a)
                point_a = point_b

        if np.linalg.norm(contour[-1] - contour[0]) > threshold:
            new_contour.append(contour[-1])

        return np.array(new_contour)

    def add_points(self, contour: np.array, threshold: int): # adds points in areas of low density
        
        delta = threshold/2

        new_contour = []

        contour = tuple(map(tuple, contour)) # prevents weird data mutation

        for i in range(len(contour)):
            point_a = np.array(contour[i])
            point_b = np.array(contour[0]) if i == len(contour)-1 else np.array(contour[i+1])
            angle = math.atan2(point_b[1]-point_a[1], point_b[0]-point_a[0])

            curr_point = point_a
            while True:
                distance =  np.linalg.norm(point_b-curr_point)
                if distance < threshold:
                    new_contour.append(tuple(point_b))
                    break
                curr_point += (delta*math.cos(angle), delta*math.sin(angle))
                new_contour.append(tuple(curr_point)) # creates copy, otherwise inserts pointer

        return np.array(new_contour)

    def get_bounding_box(self, contour: np.array) -> np.array:
        x_coords = contour[:, 0]
        y_coords = contour[:, 1]
        min_x = np.min(x_coords)
        max_x = np.max(x_coords)
        min_y = np.min(y_coords)
        max_y = np.max(y_coords)
        return np.array([min_x, max_x, min_y, max_y])

test_stl_path = "C:\\Users\\Caco Cola\\Desktop\\NEXACut Pro\\tests\\test stl parser\\test stl files"