import os
import re
import math
import copy
from collections import defaultdict
import numpy as np

# for testing
import matplotlib.pyplot as plt
import random

class SVGParser: # converts SVG into polygon with reasonable point distribution

    def __init__(self, file_path: str):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"SVG file {file_path} does not exist")
        
        self.file_path = file_path

        try: 
            self.svg_lines = self.read_svg()
            self.contours = self.get_contours()
            self.outer_contour = self.get_outermost_contour()
            self.outer_contour = self.smooth_contour(self.outer_contour)
        except Exception as e:
            print(e)

    def read_svg(self) -> list: # format [((x1, y1), (x2, y2)) ...] (returns edges)
        
        with open(self.file_path, 'r') as file:
            svg_data = file.read()

        lines = re.findall(r'<line x1="([^"]+)" y1="([^"]+)" x2="([^"]+)" y2="([^"]+)"', svg_data) # regex expression parsing

        if len(lines) == 0:
            raise ValueError("No lines found")

        coordinates = [((float(x1), float(y1)), (float(x2), float(y2))) for x1, y1, x2, y2 in lines]

        return coordinates

    def get_contours(self) -> list: # input in format [((x1, y1), (x2, y2))...], returns list of np arrays

        points = defaultdict(list) # key: point, value: all linked points

        for edge in self.svg_lines: # this creates a dictionary that will be traversed later to identify all contours
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
    
    def smooth_contour(self, contour: np.array) -> np.array: # makes sure contour has even distribution of points for faster/more accurate comparison
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

    # svg helper methods

    def get_bounding_box(self, contour: np.array) -> np.array:
        x_coords = contour[:, 0]
        y_coords = contour[:, 1]
        min_x = np.min(x_coords)
        max_x = np.max(x_coords)
        min_y = np.min(y_coords)
        max_y = np.max(y_coords)
        return np.array([min_x, max_x, min_y, max_y])

    def get_center(self, contour: np.array) -> list:
        min_x, max_x, min_y, max_y = self.get_bounding_box(contour)
        x_center = (min_x + max_x) / 2
        y_center = (min_y + max_y) / 2
        return np.array([x_center, y_center])

    def get_bounding_circle(self, contour: np.array) -> tuple: # returns bounding circle for given shape
        center = self.get_center(contour)
        max_radius = 0
        for point in contour:
            radius = np.linalg.norm(point - center)
            if radius > max_radius:
                max_radius = radius
        return (center, max_radius)

    # for testing

    def plot_contours(self, contours: list):
        plt.figure()

        for contour in contours:
            color = self._random_color()
            for point in contour:
                x, y = point
                plt.scatter(x, y, color=color)

        plt.grid(True)
        plt.gca().set_aspect('equal') 
        plt.grid(False)
        plt.show()

    def _random_color(self):
        chars = [str(i) for i in range(10)] + ['a', 'b', 'c', 'd', 'e', 'f']
        color = '#'+''.join(random.choice(chars) for _ in range(6))
        return color
    
class NoFitPolygon: # creates NFP based on two polygons

    def __init__(self, polygon1: np.array, polygon2: np.array, inside: bool = False):

        if len(polygon1) < 3 or len(polygon2) < 3:
            raise ValueError("Polygons must be of length 3 or greater")
        
        


parser = SVGParser("C:\\Users\\Caco Cola\\Desktop\\NEXACut Pro\\test svg files\\RollerConnectorPlate.svg")
contour = parser.outer_contour