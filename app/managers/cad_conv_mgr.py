import os
import json
import numpy as np
from collections import defaultdict
from stl import mesh
import matplotlib.pyplot as plt

MIN_QUANTIZED_VALUE = .01
MIN_VALUE_DECIMAL_DIGITS = 2

class CADConversionManager:
    SUPPORTED_PART_FORMATS = ['stl']

    def __init__(self, stl_filepath: str, cad_preview_data_folder: str, part_import_data_folder: str, bg_color: str='#1e1e1e', text_color: str='#efefef', plot_color: str='#cc0000'):

        self.stl_filepath = stl_filepath
        self.png_name = os.path.basename(stl_filepath)[:-4] + ".png" 
        self.preview_path = os.path.join(cad_preview_data_folder, self.png_name)
        self.svg_name = os.path.basename(stl_filepath)[:-4] + ".svg" 
        self.svg_path = os.path.join(part_import_data_folder, self.svg_name)

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
        
        self.flat_axis = self.determine_axis_to_flatten()
        self.flattened_mesh = self.flatten_stl()
        self.outer_edges = self.get_outer_edges(self.flat_axis)

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

    def determine_axis_to_flatten(self, tolerance: int = MIN_VALUE_DECIMAL_DIGITS) -> int: 
        coordinates = np.round([self.stl_mesh_vector_format[:, :, i] for i in range(3)], tolerance) # get all rounded coordinate arrays
        unique_counts = [np.unique(coordinates[i]).size for i in range(3)] # get length of arrays
        return np.argmin(unique_counts)

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

    def save_preview_image(self, scale_factor: float = 1): # scalefactor necessary for metric/imperial mode display

        if os.path.exists(self.preview_path): # no need to waste time
            return

        plt.figure()

        for edge in self.outer_edges:
            x_values, y_values = zip(*edge)
            if scale_factor != 1:
                x_values = tuple([x * scale_factor for x in x_values])
                y_values = tuple([y * scale_factor for y in y_values])
            plt.plot(x_values, y_values, color=self.plot_color)

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

        plt.savefig(self.preview_path, bbox_inches='tight', facecolor='#1E1E1E') # image bg color (around graph)

    def save_as_svg(self):
        with open(self.svg_path, 'w') as f:
            f.write('<?xml version="1.0" encoding="UTF-8" ?>\n')
            f.write('<svg xmlns="http://www.w3.org/2000/svg" version="1.1">\n')
            for line in self.outer_edges:
                x1, y1 = line[0]
                x2, y2 = line[1]
                svg_line = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="black" stroke-width="2"/>\n'
                f.write(svg_line)
            f.write('</svg>\n')
