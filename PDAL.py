# File to generate PDAL configuration for a sfm point cloud
from jinja2 import Template, Environment, FileSystemLoader
import numpy as np 

points = [
    [262986.2, 53128.25],   # lower right corner of crop area
    [262967.5, 53029.84],   # lower left corner of crop area  
    [262870.1, 53048.72],   # upper left corner of crop area
    [262888.9, 53148.19],   # upper right corner of crop area 
]

# The translation matrix must be defined according to this:
translation_matrix = [
    [1, 0, 0, -98173.73],
    [0, 1, 0, 233065.4],
    [0, 0, 1, 0],
    [0, 0, 0, 1]
]

class PDAL():

    def __init__(self,
        template_file="sfm_cloudprocess.template",
        output_file="sfm_cloudprocess.json",
        points=None):
        # Define the files
        self.pdal_template_file = template_file
        self.output_file = output_file

        # Load up the PDAL template file that we will use to make our PDAL json file. 
        self.env = Environment(loader=FileSystemLoader('templates'),     # Look for templates in templates/ folder                                                                                                      
                            trim_blocks=True)
        self.template = self.env.get_template(self.pdal_template_file) # Jinja2 will find the template.
        # Points used to define the cropping polygon must be defined as an 
        # array of points, with x, y values:
        if points:
            self.points = points

    def set_boundary(self, points):
        """ Creates a boundary around a point cloud based on an array of [x,y] pairs. 
        
            It does not matter which point begins the array, so long as the order of 
            points proceeds in a clockwise direction from the first point.

            points = [[x1, y1], [x2, y2], ... [xn, yn]]

         """
        self.points = list(points)
    
    # Helper functions to generate properly formated strings that we will put into the PDAL file.
    @classmethod
    def make_polygon(cls, points):
        # Close the polygon by duplicating the first point at the end of the list.
        poly_points = list(points)
        poly_points.append(poly_points[0])
        return "POLYGON((" + ", ".join(["{x} {y}".format(x=a[0], y=a[1]) for a in poly_points]) + "))"

    @classmethod
    def translation_matrix(cls, points):
        angle = cls.rotation_angle(points)


    @classmethod
    def rotation_angle(cls, points):
        """ Determines the plot rotation angle in radians.
        
        Requires that set_boundary() has been called or PDAL 
        object has been initialized with points.
        
        """
        x_min, y_min = list(map(min, zip(*points)))
        x_max, y_max = list(map(max, zip(*points)))
        # Find the point with the lowest 'Y' value. This is our pivot point (lower left).
        for point in points:
            if point[1] == y_min:
                ll_point = point
                break
        # Find the point with the largest 'X' value. This is the lower right point.
        for point in points:
            if point[0] == x_max:
                lr_point = point
                break
        from math import atan, cos, sin
        # Determine the angle the lower left and lower right points make between horizontal.
        angle = atan(
            (lr_point[1]-ll_point[1])/
            (lr_point[0]-ll_point[0]))
        return angle

    @classmethod
    def make_matrix(cls, matrix=None):
        if matrix:
            return ' '.join([' '.join([str(item) for item in row])
                for row in matrix])
        else:
            return 'None'

    @classmethod
    def transformation_matrix(cls, points):
        """ Creates a transformation matrix using an angle, in radians """
        from math import cos, sin
        angle = cls.rotation_angle(points)
        return [ 
            [cos(-angle), -sin(angle), 0, 0], # NOQA
            [sin(angle), cos(angle), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ]

    @classmethod
    def transform_point(cls, points, transformation_matrix):
        """ Transform a point using a transformation matrix """
        new_points = []
        for point in points:
            P = point.extend([1, 1])
            M = transformation_matrix
            new_points.append(np.matmul(M,P))[0:1]
        return new_points
    
    def make_pdal_params(self):
        pdal_params = {
            "pipeline": {
                "slope": 0.08,
                "window": 15,
                "threshold": 0.05,
                "scalar": 1.5
            },
            "crop": {
                "polygon": self.make_polygon(points)
            },
            "matrix":{
                "transformation": self.make_matrix(
                    matrix=self.transformation_matrix(points)
                ),
                "translation": self.make_matrix(matrix=self.translation_matrix(points))
            }
        } 
        return pdal_params

    def write_json(self, output_file=None):
        """ Writes PDAL configuration as a JSON file """
        if output_file:
            filename = output_file
        else:
            filename = self.output_file
        pdal_params = self.make_pdal_params()

        rendered_template = self.template.render(
            pipeline=pdal_params['pipeline'],
            crop=pdal_params['crop'],
            matrix=pdal_params['matrix'])

        with open(filename, 'w') as f:
            print(rendered_template, file=f)





