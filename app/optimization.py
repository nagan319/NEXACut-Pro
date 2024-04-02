import os
import re
import math
import copy
from collections import defaultdict
import numpy as np

# for testing
import matplotlib.pyplot as plt
import random

def read_svg(file_path: str) -> list: # format [((x1, y1), (x2, y2)) ...]

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"SVG file {file_path} does not exist")
    
    with open(file_path, 'r') as file:
        svg_data = file.read()

    lines = re.findall(r'<line x1="([^"]+)" y1="([^"]+)" x2="([^"]+)" y2="([^"]+)"', svg_data) # regex expression parsing
    coordinates = [((float(x1), float(y1)), (float(x2), float(y2))) for x1, y1, x2, y2 in lines]

    return coordinates

def get_contours(edges: list) -> list: # input in format [((x1, y1), (x2, y2))...], returns list of np arrays

    points = defaultdict(list) # key: point, value: all linked points

    for edge in edges: # this creates a dictionary that will be traversed later to identify all contours
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

    return contours

def get_bounding_box(contour: np.array) -> np.array:
    x_coords = contour[:, 0]
    y_coords = contour[:, 1]
    min_x = np.min(x_coords)
    max_x = np.max(x_coords)
    min_y = np.min(y_coords)
    max_y = np.max(y_coords)
    return np.array([min_x, max_x, min_y, max_y])

def get_center(contour: np.array) -> list:
    min_x, max_x, min_y, max_y = get_bounding_box(contour)
    x_center = (min_x + max_x) / 2
    y_center = (min_y + max_y) / 2
    return np.array([x_center, y_center])

def get_outermost_contour(contours: list) -> np.array:
    max_area = 0
    outermost_contour = None

    for contour in contours: # area of contour bounding box is calculated, max contour is returned
        min_x, max_x, min_y, max_y = get_bounding_box(contour)
        area = (max_x - min_x) * (max_y - min_y)
        if area > max_area:
            max_area = area
            outermost_contour = contour

    return outermost_contour

def get_radius(contour: np.array) -> float:
    center = get_center(contour)
    max_radius = 0
    for point in contour:
        radius = np.linalg.norm(point - center)
        if radius > max_radius:
            max_radius = radius
    return max_radius

def smooth_contour(contour: np.array) -> np.array: # makes sure contour has even distribution of points (for nfp algorithm)
    threshold1 = 10
    threshold2 = 20
    contour = remove_points(contour, threshold1)
    contour = add_points(contour, threshold2)
    return contour

def remove_points(contour: np.array, threshold: int): # removes points in areas where density is too high
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

def add_points(contour: np.array, threshold: int): # adds points in areas of low density
    
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

def plot_contours(contours: list):
    plt.figure()

    for contour in contours:
        color = random_color()
        for point in contour:
            x, y = point
            plt.scatter(x, y, color=color)

    plt.grid(True)
    plt.gca().set_aspect('equal') 
    plt.grid(False)
    plt.show()

def plot_contour_and_circle(contour: np.array):
    plt.figure()
    color = random_color()

    for point in contour:
        x, y = point
        plt.scatter(x, y, color=color)
    
    center = get_center(contour)
    radius = get_radius(contour)

    color = random_color()
    plt.scatter(center[0], center[1], color=color)

    angle = 0

    color = random_color()
    for _ in range(16):
        angle += math.pi/8
        x, y = center
        x += radius*math.cos(angle)
        y += radius*math.sin(angle)
        plt.scatter(x, y, color=color)

    plt.grid(True)
    plt.gca().set_aspect('equal') 
    plt.grid(False)
    plt.show()


def random_color():
    chars = [str(i) for i in range(10)] + ['a', 'b', 'c', 'd', 'e', 'f']
    color = '#'+''.join(random.choice(chars) for _ in range(6))
    return color

test_coordinates = read_svg("C:\\Users\\Caco Cola\\Desktop\\NEXACut Pro\\test svg files\\RollerConnectorPlate.svg")
contours = get_contours(test_coordinates)

max_contour = get_outermost_contour(contours)
edited_contour = smooth_contour(max_contour)
plot_contour_and_circle(edited_contour)
