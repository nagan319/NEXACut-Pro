# NEXACut Pro: A standalone application for automating and optimizing the CAM process on 3-axis CNC routers

![logo](https://github.com/nagan319/NEXACut-Pro/assets/147287567/e3962669-4dee-49f1-879c-7f65fb409fa7)

## Outline:

- Standalone cross-platform application
- CNC stock is stored in SVG format, ensuring compatibility and easy integration
- Use of OpenCV facilitates the addition of previously used stock materials, streamlining workflow efficiency
- New part files are seamlessly converted from STL to SVG format
- Part placement optimization is achieved through a genetic nesting algorithm, minimizing wasted material and maximizing production efficiency.
- Integration with the Fusion 360 API enables full automation of CNC workflows

## Why SVG?

SVG is the format of choice for performing optimization calculations since it is universally supported, is relatively straightforward to convert both CAD and image files into, and is highly compatible with the NFP algorithm (see 'Optimization Algorithm').

## CAD to SVG
![cad conversion](https://github.com/nagan319/NEXACut-Pro/assets/147287567/2986d8b4-7201-49c4-ae9f-c8305ca8250e)

The conversion process for CAD files follows a straightforward approach. Initially, it receives an STL file consisting of a list of facets with their respective points. The process identifies the axis with the fewest unique coordinates, assuming the CAD files are flat and parallel to a coordinate axis. It then 'flattens' the file by filtering out facets lying directly on the target plane, discarding unnecessary geometric data. Outside edges are then filtered out based on the fact that they, by definition, only belong to one facet.

## Image to SVG
![plate_conversion](https://github.com/nagan319/NEXACut-Pro/assets/147287567/01402912-f3c6-4d32-857d-f4a2ca78a3b4)

The image conversion process consists of four key stages, achieved via the OpenCV image processing library in Python. Initially, the raw image undergoes resizing and binary conversion via thresholding. Then, additional filtering is applied to reduce noise and refine the binary representation. 

Next, a feature detection algorithm is used to determine the key features of the image, including corners and edges. Although I attempted using OpenCV's default corner detection method, it proved cumbersome for the task, leading to a custom method leveraging dot product computations to evaluate changes in angles between points.

Once features are detected, the image is 'flattened' and resized to appropriate dimensions. This image is then converted to SVG and can be used in the optimization algorithm.

## Built-in System for Organizing Digitized CNC Stock
![stock](https://github.com/nagan319/NEXACut-Pro/assets/147287567/560f59bf-28ef-4eee-938b-70b62dcd01e8)

Intuitive digitization of CNC stock allows for easily viewing available plates without wasting valuable production time. Each plate file within the stock is characterized by its material type and dimensions along with an optional SVG file. Stock files consist of a list of plates and are used during optimization calculations.

## Optimization Algorithm
![optimization algorithm](https://github.com/nagan319/NEXACut-Pro/assets/147287567/3e4c8641-22fb-4da7-b1b6-73e4e0635df2)

The optimization algorithm utilizes the concept of the no-fit polygon (NFP). Essentially, an NFP is the union of the area created by a polygon (A) and all possible positions of a polygon (B) around it. Random placements consisting of parts placed on possible NFP locations of existing plates in order of decreasing size are fed through a genetic algorithm, which filters out better placements based on the amount of wasted material and returns the heuristic ideal.

## In-App Screenshots
![home screen](https://github.com/nagan319/NEXACut-Pro/assets/147287567/0baff21f-711f-4207-a7ae-c543458f7cdd)
![part import](https://github.com/nagan319/NEXACut-Pro/assets/147287567/a12b3348-5d89-4fec-85fc-f865ae9c6a3a)
![router configuration](https://github.com/nagan319/NEXACut-Pro/assets/147287567/00fa6c2e-f65b-4b30-8763-2655c05b06e1)
![inventory management](https://github.com/nagan319/NEXACut-Pro/assets/147287567/3587b292-817e-4bd8-b274-bf74fa8fd690)



