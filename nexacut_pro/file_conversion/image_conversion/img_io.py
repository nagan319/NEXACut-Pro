import os
import cv2

def read_image(path: str, color: bool = True):
    if not os.path.exists(path):
        raise FileNotFoundError(f"The file {path} does not exist")

    if color:
        image = cv2.imread(path, cv2.IMREAD_COLOR)
    else:
        image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)

    return image

def write_image(path: str, name: str, image):
    if not os.path.exists(path):
        raise FileNotFoundError(f"The file {path} does not exist")

    image_path = os.path.join(path, name)
    cv2.imwrite(image_path, image) 

def clear_all_files(path: str): # clears all files in image preview folder - will move to general util folder
    if not os.path.exists(path):
        raise FileNotFoundError(f"The file {path} does not exist")
    
    files = os.listdir(path)
    
    for file_name in files:
        file_path = os.path.join(path, file_name)
        os.remove(file_path)