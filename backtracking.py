import polygonrep
from sys import float_info
from shapely.geometry import Polygon, Point, LineString
from shapely import affinity
from math import sqrt, exp
import numpy as np
import random
import placement

def get_diff_polygon(polygon_placed, target_polygon):

    diff_polygon = target_polygon.difference(polygon_placed)
    diff_check = False
    
    if diff_polygon.geom_type == 'MultiPolygon':
        # random_index = random.randrange(len(diff_polygon))
        max_area = 0
        for polygon in diff_polygon:
            diff_poly_area = polygon.area
            if(diff_poly_area > max_area):
                max_area = diff_poly_area
                diff_polygon = polygon
        diff_check = True
    diff_polygon = placement.merge_corners(diff_polygon)
    return diff_polygon, diff_check

def difference_polygon(polygons, target_polygon, solution):
    transformed_polygons = polygonrep.perform_sequence(polygons, solution)
    overlay_polygons = polygonrep.union_polygons(transformed_polygons)

    diff_polygon = target_polygon.difference(overlay_polygons)
    diff_check = False
    if diff_polygon.geom_type == 'MultiPolygon':
        random_index = random.randrange(len(diff_polygon))
        diff_polygon = diff_polygon[random_index]
        diff_check = True
        
    diff_polygon = placement.merge_corners(diff_polygon)
    return diff_polygon, diff_check

def add_polygon_to_target(polygons, target_polygon):
    pass

def get_next_solution(polygons, target_polygon, solution):
    pass

# def backtrack_solve(polygons, target_polygon, pres= 0.0001):

#     if(len(polygons) == 1):
#         if(abs(polygons[0].area - target_polygon.area) <= pres):
#             sequence, flip_check = placement.place_polygon_by_edge(target_polygon, polygons[0], pres, flip=True)   
#             return sequence
#         else:
#             return 0

#     for index in range(0,len(polygons)):
#         print(index)
#         poly = polygons[index]
#         sequence_list, flip_check = placement.place_polygon_by_edge_helper(target_polygon, poly, flip=True)

#         for sequence in sequence_list:
#             print("sequence_check " + str(index))
#             if flip_check:
#                 poly = placement.flip_polygon(poly)
#             diff_target_poly = placement.get_diff_polygon(poly, target_polygon, sequence)

#             seq_rest = backtrack_solve(polygons[index:], diff_target_poly)

#             if (seq_rest != 0):
#                 final_sequence = sequence + seq_rest
#                 return final_sequence
#     return 0

def backtrack_solve(polygons, target_polygon, pres= 0.0001):

    if(len(polygons) == 1):
        if(abs(polygons[0].area - target_polygon.area) <= pres):
            sequence, flip_check = placement.place_polygon_by_edge(target_polygon, polygons[0], pres, flip=True)   
            return sequence
        else:
            return 0

    for index in range(0,len(polygons)):
        print(index)
        poly = polygons[index]
        sequence_list, flip_check = placement.place_polygon_by_edge_helper(target_polygon, poly, flip=True)

        for sequence in sequence_list:
            print("sequence_check " + str(index))
            print("length_sequence" + str(len(sequence_list)))
            if flip_check:
                poly = placement.flip_polygon(poly)
            diff_target_poly = placement.get_diff_polygon(poly, target_polygon, sequence)

            seq_rest = backtrack_solve(polygons[index:], diff_target_poly)

            if (seq_rest != 0):
                final_sequence = sequence + seq_rest
                return final_sequence
    return 0





