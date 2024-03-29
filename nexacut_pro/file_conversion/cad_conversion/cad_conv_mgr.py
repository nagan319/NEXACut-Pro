import os
import sys
from stl import mesh

import stl_proc

class CADConversionManager:

    def __init__(self, filepath):

        self.filepath = filepath

        if stl_proc.is_valid_stl(filepath):
            stl_mesh = mesh.Mesh.from_file(filepath)
            stl_mesh_vector_format = stl_mesh.vectors # vectors form has lists for point coordinates within facet list
        else:
            raise FileNotFoundError("STL file does not exist")
        
        if stl_proc.is_stl_format_valid(stl_mesh_vector_format):
            self.mesh = stl_mesh_vector_format
        else:
            raise ValueError("STL file is corrupt")
        
        self.flat_axis  = stl_proc.determine_axis_to_flatten(self.mesh)
        self.flattened_mesh = stl_proc.flatten_stl(self.mesh, self.flat_axis)
        self.outlines = stl_proc.get_outer_edges(self.flattened_mesh)

current_directory = os.path.dirname(os.path.abspath(__file__))
absolute_path  = os.path.join(current_directory, 'toyota_corolla_ae86_trueno.stl')
new_manager = CADConversionManager(absolute_path)
    