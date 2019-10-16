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
    """ Creates a PDAL object for use in PDAL configuration """
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
    
    # Helper functions to generate properly formated strings that we will put into the PDAL file.
    @classmethod
    def make_polygon(cls, points):
        """ Generates a polygon string from a list of points

        >>> points = [
        ...   [262986.2, 53128.25],   # lower right corner of crop area
        ...   [262967.5, 53029.84],   # lower left corner of crop area  
        ...   [262870.1, 53048.72],   # upper left corner of crop area
        ...   [262888.9, 53148.19],   # upper right corner of crop area 
        ... ]
        >>> PDAL.make_polygon(points)
        'POLYGON((262986.2 53128.25, 262967.5 53029.84, 262870.1 53048.72, 262888.9 53148.19, 262986.2 53128.25))'

        """
        # Close the polygon by duplicating the first point at the end of the list.
        poly_points = list(points)
        poly_points.append(poly_points[0])
        return "POLYGON((" + ", ".join(["{x} {y}".format(x=a[0], y=a[1]) for a in poly_points]) + "))"

    @classmethod
    def lower_left(cls, points):
        """ Finds the lower left coordinate in a list of bounding coordinates

        >>> points = [[1,2],[4,5],[1,6],[5,2]]

        >>> PDAL.lower_left(points)
        [1, 2]

        """
        x_min, y_min = list(map(min, zip(*points)))
        # Find the point with the lowest 'Y' value. This is our 
        # pivot point (lower left).
        for point in points:
            if point[1] == y_min:
                return point

    @classmethod
    def lower_right(cls, points):
        """ Find the lower right coordinate in a list of bounding coordinates
        
        >>> points = [[1,2],[4,5],[1,6],[5,2]]

        >>> PDAL.lower_right(points)
        [5, 2]
        
        """
        x_max, y_max = list(map(max, zip(*points)))
        # Find the point with the highest 'X' value. This is our 
        # far corner of the lower bound of the plot (lower right).
        for point in points:
            if point[0] == x_max:
                return point
    
    @classmethod
    def rotation_angle(cls, points, unit='radians'):
        """ Determines the plot rotation angle in radians.
        
        >>> points = [
        ...   [262986.2, 53128.25],   # lower right corner of crop area
        ...   [262967.5, 53029.84],   # lower left corner of crop area  
        ...   [262870.1, 53048.72],   # upper left corner of crop area
        ...   [262888.9, 53148.19],   # upper right corner of crop area 
        ... ]

        >>> PDAL.rotation_angle(points)
        1.3830137845749129

        >>> PDAL.rotation_angle(points, unit="degrees")
        0.8804539207173082

        """
        from math import pi
        ll_point = cls.lower_left(points)
        lr_point = cls.lower_right(points)
        from math import atan, cos, sin
        # Determine the angle the lower left and lower right points make between horizontal.
        angle = atan(
            (lr_point[1]-ll_point[1])/
            (lr_point[0]-ll_point[0]))
        if unit=='degrees':
            return angle/(pi/2)
        return angle

    @classmethod
    def make_matrix(cls, matrix=None):
        """ Create a matrix for inclusion in the JSON configuration file

        >>> points = [
        ...   [262986.2, 53128.25],   # lower right corner of crop area
        ...   [262967.5, 53029.84],   # lower left corner of crop area  
        ...   [262870.1, 53048.72],   # upper left corner of crop area
        ...   [262888.9, 53148.19],   # upper right corner of crop area 
        ... ]

        >>> t_mat = PDAL.transformation_matrix(points)

        >>> PDAL.make_matrix(matrix=t_mat)
        '0.18668087950923754 0.9824206070852024 0 0 -0.9824206070852024 0.18668087950923754 0 0 0 0 1 0 0 0 0 1'
        
        """
        if matrix:
            return ' '.join([' '.join([str(item) for item in row])
                for row in matrix])
        else:
            return 'None'

    @classmethod
    def transformation_matrix(cls, points):
        """ Creates a transformation matrix using an angle, in radians 
        
            The rotation matrix rotates about the origin.

        >>> points = [
        ...   [262986.2, 53128.25],   # lower right corner of crop area
        ...   [262967.5, 53029.84],   # lower left corner of crop area  
        ...   [262870.1, 53048.72],   # upper left corner of crop area
        ...   [262888.9, 53148.19],   # upper right corner of crop area 
        ... ]

        >>> PDAL.transformation_matrix(points)
        [[0.18668087950923754, 0.9824206070852024, 0, 0], [-0.9824206070852024, 0.18668087950923754, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
        """
        from math import cos, sin
        angle = cls.rotation_angle(points)
        return [ 
            [cos(angle), sin(angle), 0, 0], # NOQA
            [-sin(angle), cos(angle), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ]

    @classmethod
    def transform_point(cls, point, M):
        """ Transform a single point using a transformation matrix 
        
        >>> from math import cos, sin, pi
        >>> theta = pi/2
        >>> point = [3,2]
        >>> rotation_matrix = [
        ... [cos(theta), sin(theta), 0, 0],
        ... [-sin(theta), cos(theta), 0, 0],
        ... [0, 0, 1, 0],
        ... [0, 0, 0, 1]]
        >>> PDAL.transform_point(point, rotation_matrix)
        [2.0, -3.0]
        
        >>> translation_matrix= [
        ...  [1, 0, 0, -3],
        ...  [0, 1, 0, -2],
        ...  [0, 0, 1, 0],
        ...  [0, 0, 0, 1]]

        >>> PDAL.transform_point(point, translation_matrix)
        [0, 0]

        """
        P = list(point)
        P.extend([1, 1])
        return list(np.matmul(M,P))[0:2]

    @classmethod
    def translation_matrix(cls, points):
        """ Generates a translation matrix for a set of points.

        This calculation is done "post-rotation", so that the translation
        forces the lower left point to be at the origin

        # Use realistic points. These are taken from some Uhuru data at Mpala

        >>> points = [
        ...   [262986.2, 53128.25],   # lower right corner of crop area
        ...   [262967.5, 53029.84],   # lower left corner of crop area  
        ...   [262870.1, 53048.72],   # upper left corner of crop area
        ...   [262888.9, 53148.19],   # upper right corner of crop area 
        ... ]

        >>> PDAL.translation_matrix(points)
        [[1, 0, 0, -101188.61178877657], [0, 1, 0, 248445.03382224383], [0, 0, 1, 0], [0, 0, 0, 1]]

        # Let's make sure that if we rotate and then translate the lower left
        # corner (ll_point), we end up with that point exactly at the origin [0.0, 0.0]

        >>> ll_point = PDAL.lower_left(points)
        >>> rotation_matrix = PDAL.transformation_matrix(points)
        >>> translation_matrix = PDAL.translation_matrix(points)
        >>> PDAL.transform_point(
        ...     PDAL.transform_point(ll_point,rotation_matrix),
        ...     translation_matrix)
        [0.0, 0.0]
        """
        ll_point = cls.lower_left(points)
        t_mat = cls.transformation_matrix(points)
        [x_shift, y_shift] = cls.transform_point(ll_point, t_mat)
        return [
            [1, 0, 0, -x_shift],
            [0, 1, 0, -y_shift],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ]

    def make_pdal_params(self):
        """
        Create a dictionary of PDAL parameters

        >>> points = [
        ...   [262986.2, 53128.25],   # lower right corner of crop area
        ...   [262967.5, 53029.84],   # lower left corner of crop area  
        ...   [262870.1, 53048.72],   # upper left corner of crop area
        ...   [262888.9, 53148.19],   # upper right corner of crop area 
        ... ]
        >>> pdal = PDAL(points=points)
        >>> params = pdal.make_pdal_params()
        >>> params['matrix']['transformation']
        '0.18668087950923754 0.9824206070852024 0 0 -0.9824206070852024 0.18668087950923754 0 0 0 0 1 0 0 0 0 1'
        >>> params['matrix']['translation']
        '1 0 0 -101188.61178877657 0 1 0 248445.03382224383 0 0 1 0 0 0 0 1'
        >>> params['pipeline']['slope']
        0.08
        >>> params['pipeline']['window']
        15
        >>> params['pipeline']['scalar']
        1.5
        >>> params['crop']['polygon']
        'POLYGON((262986.2 53128.25, 262967.5 53029.84, 262870.1 53048.72, 262888.9 53148.19, 262986.2 53128.25))'
        """
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


if __name__ == "__main__":
    import doctest
    doctest.testmod()


