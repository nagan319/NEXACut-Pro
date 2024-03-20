# NEXACut Pro: A standalone application for automating and optimizing the CAM process on 3-axis CNC routers

## Outline:

- Standalone cross-platform application
- CNC stock stored in SVG format
- Use of OpenCV allows for easy addition of already used stock
- Files for new parts converted from STL to SVG format
- Part placement is optimized by a genetic nesting algorithm
- Possible integration of Fusion 360 and/or SolidWorks API for full automation

## Notes:

- Manual path extension prior to all local imports is done to avoid creating a custom launch.json file with "type": "python", a feature that will soon be deprecated and may create issues, as well as to avoid creating an os-dependent absolute path in the same file.