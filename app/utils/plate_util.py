import os
import matplotlib.pyplot as plt

# create generic class to combine with RouterUtil, functionality very similar

class PlateUtil:

    MAX_DIMENSION = 5000

    DEFAULT_X = 1000
    DEFAULT_Y = 1000
    DEFAULT_Z = 10

    DEFAULT_MATERIAL = "Aluminum"

    def __init__(self, plate_preview_folder_path: str):

        self.plate_preview_folder_path = plate_preview_folder_path
        self.editable_keys = self._get_editable_keys()
        self.value_ranges=  self._get_value_ranges()

        self.plot_bg_color: str='#ffffff' 
        self.plot_text_color: str='#000000'
        self.plot_line_color: str='#000000'

    def _get_editable_keys(self):
        return [
            "width_(x)",
            "height_(y)",
            "thickness_(z)",
            "material"
        ]
    
    def _get_value_ranges(self):
        return {
            "width_(x)": (0, self.MAX_DIMENSION),
            "height_(y)": (0, self.MAX_DIMENSION),
            "thickness_(z)": (0, self.MAX_DIMENSION),
            "material": None
        }
    
    def get_new_plate(self, plate_data: list) -> dict:
        filename =  self._get_next_plate_filename(plate_data)
        preview_path = self.get_preview_path(filename)

        return {
            "filename": filename,
            "preview_path": preview_path,
            "width_(x)": self.DEFAULT_X,
            "height_(y)": self.DEFAULT_Y,
            "thickness_(z)": self.DEFAULT_Z,
            "material": self.DEFAULT_MATERIAL,
            "contours": None
        }
     
    def _get_next_plate_filename(self, plate_data: list) -> str: 

        plate_filenames = [plate['filename'] for plate in plate_data]

        if len(plate_filenames) == 0:
            return "PLATE-0.json"  
        
        plate_name_values = [int(plate_filename.split('-')[1].split('.')[0]) for plate_filename in plate_filenames]

        sorted_values = sorted(plate_name_values)

        for i, value in enumerate(sorted_values[:-1]):
            next_value = sorted_values[i+1]
            if next_value != value+1:
                return "PLATE-"+str(value+1)+'.json'

        return "PLATE-"+str(sorted_values[-1]+1)+".json"
 
 
    def get_preview_path(self, plate_filename: str) -> str:

        filename_no_extension = os.path.splitext(plate_filename)[0]
        preview_path = os.path.join(self.plate_preview_folder_path, filename_no_extension+'.png')
        return preview_path
    
    def save_preview_image(self, plate_data: dict, figsize: tuple = (3.5, 3.5), dpi: int = 80):

        try: 
            image_path = plate_data['preview_path']
            image_contours = plate_data['contours']
            plate_xy =  plate_data['width_(x)'], plate_data['height_(y)']
        except KeyError as e:
            print(e)
            return

        plate_rect_x, plate_rect_y = self._generate_rectangle_coordinates(*plate_xy)
    
        plt.figure(figsize=figsize)
        
        plt.plot(plate_rect_x, plate_rect_y, color = self.plot_line_color)

        if image_contours is not None:    
            for contour in enumerate(image_contours):
                x_vals = contour[:, 0]
                y_vals=  contour[:, 1] 
                plt.plot(x_vals, y_vals, color = self.plot_line_color)
 
        plt.grid(True)
        plt.gca().set_facecolor(self.plot_bg_color) # bg color
        plt.gca().set_aspect('equal') 
        plt.grid(False)
        plt.tick_params(axis='x', colors=self.plot_text_color)  # tick color
        plt.tick_params(axis='y', colors=self.plot_text_color) 

        plt.gca().spines['top'].set_color(self.plot_text_color) # graph borders
        plt.gca().spines['bottom'].set_color(self.plot_text_color)
        plt.gca().spines['left'].set_color(self.plot_text_color)
        plt.gca().spines['right'].set_color(self.plot_text_color)

        plt.savefig(image_path, bbox_inches='tight', facecolor='#FFFFFF', dpi=dpi)

    def _generate_rectangle_coordinates(self, width, height, offset_x=0, offset_y=0):

        x_coordinates = [offset_x, offset_x + width, offset_x + width, offset_x, offset_x]
        y_coordinates = [offset_y, offset_y, offset_y + height, offset_y + height, offset_y]
        return x_coordinates, y_coordinates
    


        


     



