import polygonrep
from sys import float_info
from shapely.geometry import Polygon, Point, LineString
from shapely import affinity
from math import sqrt, exp
import numpy as np
import random
import polyplacement

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
    diff_polygon = polyplacement.merge_corners(diff_polygon)
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
        
    diff_polygon = polyplacement.merge_corners(diff_polygon)
    return diff_polygon, diff_check

def add_polygon_to_target(polygons, target_polygon):
    pass

def get_next_solution(polygons, target_polygon, solution):
    pass

def backtrack_solve(polygons, target_polygon):
    pass

def backtracking_sol(polygons, target_polygon):
    sequence = [0]*(3*len(polygons))

    if(len(polygons) == 1):
        poly_placed, solution, overlap_check = polyplacement.place_polygon_by_edge(target_polygon, polygons[0], flip=True)
        if overlap_check:
            print(list(target_polygon.exterior.coords))
            print(solution)
            return True
        else :
            return False
    
    else:
        for index in range(0, len(polygons)):
            index = len(polygons)-1-index
            poly_placed, solution, overlap_check = polyplacement.place_polygon_by_edge(target_polygon, polygons[0], flip=True)
            if overlap_check:
                rest_polygons = polygons[:index] + polygons[index+1:]
                diff_polygon, diff_check = get_diff_polygon(poly_placed, target_polygon)
                diff_polygon = polyplacement.merge_corners(diff_polygon)
                if (backtracking_sol(rest_polygons, diff_polygon)):
                    print(list(diff_polygon.exterior.coords))
                    print(solution)
                    return True
        return False

    

def backtracking_solve(polygons, target_polygon, sequence = 0):
    
    if sequence == 0:
        sequence = [0]*(3*len(polygons))
    if len(polygons) == 1:
        poly_placed, solution, overlap_check = polyplacement.place_polygon_by_edge(target_polygon, polygons[0], flip=True)
        print("found")
        print(solution)
        if not(overlap_check):
            return 
        return solution

    if polygonrep.loss_function(sequence, polygons, target_polygon) <= 0.1:
        return sequence
    else:
        for index in range(0, len(polygons)):
            index = len(polygons)-1-index
            poly_placed, solution, overlap_check = polyplacement.place_polygon_by_edge(target_polygon, polygons[index], flip=True)
            print(target_polygon.intersection(poly_placed).area)
            # print(solution)
            if not(overlap_check):
                print("skipped")
                continue
            
            sequence[3*index: 3*index+3] = solution
            # print("inbetween")
            # print(solution)
            # print(index)

            rest_polygons = polygons[:index] + polygons[index+1:]
            # diff_polygon, diff_check = difference_polygon([polygons[index]], target_polygon, solution)
            diff_polygon, diff_check = get_diff_polygon(poly_placed, target_polygon)
            diff_polygon = polyplacement.merge_corners(diff_polygon)
            # print(list(diff_polygon.exterior.coords))

            if not(diff_check):
                rec_seq = backtracking_solve(rest_polygons, diff_polygon)

                if rec_seq is None:
                    continue
                if len(rec_seq) <= 3*index:
                    final_solution = rec_seq + solution
                else:
                    final_solution = rec_seq[:3*index] + solution + rec_seq[3*index:]
                return final_solution