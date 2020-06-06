import polygonrep
import polyplacement
from shapely.geometry import Polygon, Point, LineString
from shapely import affinity
from math import sqrt, atan
import numpy as np
import polyplacement

'''
GUI For creating new pieces using pygame maybe?
'''

def create_tangram(polygons):
    target_polygon = polygonrep.regular_parallelogram(sqrt(8),sqrt(8), 90)
    polygons_placed, sequence = polyplacement.place_polygons_on_target(polygons, target_polygon)
    print(polygons_placed)
    return polygonrep.union_polygons(polygons_placed)

def slide_along_line(polygon_ref, polygon_to_shift, line_ref):
    pass


def place_polygons(polygon_ref, polygon_to_shift, line_ref, lies_outside = True):  
    bounds = list(polygon_to_shift.bounds)
    line_mid_point = list(LineString(line_ref).centroid)

    if lies_outside:  
        minx = bounds[0]
        miny = bounds[1]
        x_shift = line_mid_point[0] - minx
        y_shift = line_mid_point[1] - miny
        polygon_shifted = affinity.translate(polygon_to_shift, x_shift, y_shift)
    else :
        maxx = bounds[2]
        maxy = bounds[3]
        x_shift = line_mid_point[0] - maxx
        y_shift = line_mid_point[1] - maxy
        polygon_shifted = affinity.translate(polygon_to_shift, x_shift, y_shift)

    return polygon_ref, polygon_shifted

def place_polygons_ref_point(polygon_ref, polygon_to_shift, reference_point, lies_outside = True):
    pass