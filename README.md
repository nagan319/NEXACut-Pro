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

# CAD to SVG
![part import](https://github.com/nagan319/NEXACut-Pro/assets/147287567/e0e13fff-369a-4dd7-a7b2-21f58d3ee016)

The conversion algorithm for CAD files is relatively straightforward - it takes an STL file, which consists of a list of facets with their respective points, identifies the axis along which there are the fewest unique coordinates (as a prerequesite, CAD files must be 'flat' pieces situated parallel a coordinate axis), 'flattens' the file by filtering out facets with all points on the target plane, and filters outside edges. All outside edges, by definition, only belong to one facet and as such can be easily filtered. 

![image0](https://github.com/nagan319/NEXACut-Pro/assets/147287567/d3b5c36e-e39b-4766-a7fb-59e699ce40d1)
![image0bin](https://github.com/nagan319/NEXACut-Pro/assets/147287567/caf17195-fa46-40f6-97db-d9f28f347276)
![image0ctr](https://github.com/nagan319/NEXACut-Pro/assets/147287567/13ef41b7-30fa-4739-b512-e4a238bfcd79)
![image0flat](https://github.com/nagan319/NEXACut-Pro/assets/147287567/367f3be0-03d7-4f30-bc19-792074e6e676)
![router configuration](https://github.com/nagan319/NEXACut-Pro/assets/147287567/00fa6c2e-f65b-4b30-8763-2655c05b06e1)

