# NEXACut Pro: A standalone application for automating and optimizing the CAM process on 3-axis CNC routers

![logo](https://github.com/nagan319/NEXACut-Pro/assets/147287567/e3962669-4dee-49f1-879c-7f65fb409fa7)

## Outline:

- Standalone cross-platform application
- CNC stock stored in SVG format
- Use of OpenCV allows for easy addition of already used stock
- Files for new parts converted from STL to SVG format
- Part placement is optimized by a genetic nesting algorithm
- Integration with Fusion 360 API for full automation

## Why SVG?

SVG is the format of choice for performing optimization calculations since it is universally supported, is relatively straightforward to convert both CAD and image files into, and is highly compatible with the NFP algorithm (see 'Optimization Algorithm').

## CAD to SVG
![cad conversion](https://github.com/nagan319/NEXACut-Pro/assets/147287567/2986d8b4-7201-49c4-ae9f-c8305ca8250e)

The conversion process for CAD files is relatively straightforward. It receives an STL file, which consists of a list of facets with their respective points, identifies the axis along which there are the fewest unique coordinates (as a prerequesite, CAD files must be 'flat' pieces situated parallel a coordinate axis), 'flattens' the file by filtering out facets with all points on the target plane, and filters outside edges. All outside edges, by definition, only belong to one facet and as such can be easily filtered. 

## Image to SVG
![plate_conversion](https://github.com/nagan319/NEXACut-Pro/assets/147287567/01402912-f3c6-4d32-857d-f4a2ca78a3b4)

The conversion process for image files consists of four stages and makes use of the OpenCV library for Python. First, the raw image file is resized to a certain resolution and converted to binary using thresholding. After additional filtering, it is passed into a feature detection algorithm which detects outlines and corners in the image. I tried using the CV library's default corner detection method but found that it was not ideal for the situation and instead wrote a method that uses dot products to determine the change in angle between two points. After corners are found, the image is 'flattened' and can be converted to SVG.

![router configuration](https://github.com/nagan319/NEXACut-Pro/assets/147287567/00fa6c2e-f65b-4b30-8763-2655c05b06e1)

