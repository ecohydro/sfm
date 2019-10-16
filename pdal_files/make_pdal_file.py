# File to generate PDAL configuration for a sfm point cloud
from jinja2 import Template, Environment, FileSystemLoader
import numpy as np 

# Define the files
pdal_template_file = "p01_to_p04_sfmcloudprocess.template"
output_file = "p01_to_p04_sfmcloudprocess.json"

# Load up the PDAL template file that we will use to make our PDAL json file. 
env = Environment(loader=FileSystemLoader('templates'),     # Look for templates in templates/ folder                                                                                                      
                     trim_blocks=True)
template = env.get_template(pdal_template_file) # Jinja2 will find the template.

# Helper functions to generate properly formated strings that we will put into the PDAL file.
def make_polygon(points):
    return "POLYGON((" + ", ".join(["{x} {y}".format(x=a[0], y=a[1]) for a in points]) + "))"

def rotation_angle(ll_point, lr_point):
    " Point 1 and Point 2 are x,y pairs"
    from math import atan, cos, sin
    angle = atan((lr_point[1]-ll_point[1])/(lr_point[0]-ll_point[0]))
    return cos(-angle), sin(angle)


def make_matrix(matrix):
    return ' '.join([' '.join([str(item) for item in row])
        for row in matrix])

# Points used to define the cropping polygon must be defined as an 
# array of points, with x, y values:
default_crop_points = [
    [262986.2, 53128.25],   # lower right corner of crop area
    [262967.5, 53029.84],   # lower left corner of crop area  
    [262870.1, 53048.72],   # upper left corner of crop area
    [262888.9, 53148.19],   # upper right corner of crop area 
    [262870.1, 53048.72]
]

(theta_cos, theta_sin) = rotation_angle(default_crop_points[0], default_crop_points[1])

# The transformation matrix must be defined according to this:
default_transformation_matrix = [ 
        [theta_cos, -theta_sin, 0, 0], # NOQA
        [theta_sin, theta_cos, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
]

# Eventually determine translation matrix from crop points using np.matmul:
np.matmul(M,P)


# The translation matrix must be defined according to this:
default_translation_matrix = [
        [1, 0, 0, -98173.73],
        [0, 1, 0, 233065.4],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
]

default_pdal_params = {
    "pipeline": {
        "slope": 0.08,
        "window": 15,
        "threshold": 0.05,
        "scalar": 1.5
    },
    "crop": {
        "polygon": make_polygon(default_crop_points)
    },
    "matrix":{
        "transformation": make_matrix(default_transformation_matrix),
        "translation": make_matrix(default_translation_matrix)
    }

} 

pdal_params = default_pdal_params


rendered_template = template.render(
    pipeline=pdal_params['pipeline'],
    crop=pdal_params["crop"],
    matrix=pdal_params["matrix"],
)

with open(output_file, "w") as f:
    print(rendered_template, file=f)




