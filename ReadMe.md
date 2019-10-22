# SfM Workflow

Libraries and notebooks for processing SfM `xyzrgb` data.

## PDAL Configuration (PDAL.py)

The PDAL.py file contains the `PDAL` Object specification. This object provides functions for generating `json`-formatted PDAL workflows that will crop, rotate, and translate an sfm point cloud.

### Creating a PDAL object

Here's an example that demonstrates how a PDAL configuration can be generated from a set of points. The points are provided as a list of [x,y] pairs (i.e. a list of lists):

```
points = [
    [262986.2, 53128.25],   # lower right corner of crop area
    [262967.5, 53029.84],   # lower left corner of crop area  
    [262870.1, 53048.72],   # upper left corner of crop area
    [262888.9, 53148.19],   # upper right corner of crop area 
]
```

*Note: The points supplied must be in circular (clockwise or counterclockwise) order for the correct configuration file to be generated.*


Using these `points`, we can import the PDAL class, and initialize a PDAL object:

```
from PDAL import PDAL

my_pdal = PDAL(points=points)

```

The `my_pdal` object can now be used to generate the appropriate `PDAL` configuration file.

### Creating a PDAL configuration file

The `PDAL` configuration file is a `JSON`-formatted file created using the `PDAL.write_json()` function. The defaut name for this file is `sfm_cloudprocess.json`, but this can be overridden by passing an `output_file` argument when generating a pdal object:

```
my_pdal = PDAL(points=points, output_file=`name_of_output_file.json`)

my_pdal.write_json()

```

Alternatively, it is possible to specify the output file when calling  `write_json()`:

```

my_pdal.write_json(output_file='name_of_output_file.json')

```

### Writing output files with one-liners:

It is possible to write out a PDAL configutation file using only an array of points:

```

points = [
    [262986.2, 53128.25],   # lower right corner of crop area
    [262967.5, 53029.84],   # lower left corner of crop area  
    [262870.1, 53048.72],   # upper left corner of crop area
    [262888.9, 53148.19],   # upper right corner of crop area 
]

PDAL(points=points).write_json()

```

Note: As with the note above, these points supplied must be in circular (clockwise or counterclockwise) order for the correct configuration file to be generated.

### Additional Class functions

The PDAL class has a suite of functions that assist in working with PDAL calculations these include:

* `PDAL.rotation_angle(points)`: Determines the necessary rotation angle, given a list of bounding coordinates.

* `PDAL.rotation_matrix(points)`: Generates the appropriate transformation matrix necessary to rotate a set of points into an orthogonal coordinate system.

* `PDAL.translation_matrix(points)`: Generates the transformation matrix necessary to re-center a transformed matrix so that the lower left corner of the point cloud is at the origin (0,0)

* `PDAL.transform_point(point, matrix)`: Re-projects a single point according to a specified transformation matrix (use `PDAL.rotation_matrix()` or `PDAL.translation_matrix()` to generate this `matrix`)

TODOS:

1. Probably could combine the `rotation` and `translation` matrixes into a single `transformation` matrix within `PDAL`. A  these transformations are linear, so they do not need to be in separate matricies.

1. We need a test `.csv` file with all the points so we can start benchmarking the speed of our affine transformations in PDAL vs. python. 

1. We should explore the implementation of the ground-finding algorithm in PDAL and see if we can build it here in python.

1. Is github working in slack?




