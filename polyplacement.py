import polygonrep
from shapely.geometry import Polygon, Point, LineString
from shapely import affinity
from math import sqrt, atan, degrees, acos
import numpy as np
import random
import copy

'''
TO _ DO LIST

1) flip polygon placement
2) flip the polygon after placing along the edge

'''

def cross_sign(x1, y1, x2, y2):
    return x1 * y2 > x2 * y1

def cal_angle(base_point, point_ref, point_a):
    line_a = LineString([base_point, point_a])
    line_ref = LineString([base_point, point_ref])

    length_a = line_a.length
    length_ref = line_ref.length

    x_diff_a = point_a[0] - base_point[0]
    y_diff_a = point_a[1] - base_point[1]

    x_diff_ref = point_ref[0] - base_point[0]
    y_diff_ref = point_ref[1] - base_point[1]

    dot_product = x_diff_a*x_diff_ref + y_diff_a*y_diff_ref
    cos_theta = (dot_product)/(length_a*length_ref)

    if cos_theta > 1:
        # print(cos_theta)
        cos_theta = 1
    elif cos_theta < -1:
        # print(cos_theta)
        cos_theta = -1

    angle = degrees(acos(cos_theta))

    ## check for convex polygon and return the inside angle
    if cross_sign(x_diff_a, y_diff_a, x_diff_ref, y_diff_ref):
        return angle
    else:
        return 360-angle


def cal_slope(base_point, end_point):
    y_diff = end_point[1] - base_point[1]
    x_diff = end_point[0] - base_point[0]

    if x_diff == 0:
        return 90
    else:
        return degrees(atan(y_diff/x_diff))

'''
If slope of later is higher results in negative angle
'''

def inbetween(point_to_check, base_point, point_ref):

    if (cal_slope(base_point, point_ref) != cal_slope(base_point, point_to_check)):
        return False

    if((point_to_check[0] - base_point[0])* (point_ref[0] - base_point[0]) > 0):
        return True
    else:
        return False


def index_dict(list_ref):
    ind_dict = {}
    for index in range(0, len(list)):
        ind_dict[index] = list_ref[index]
    
    return ind_dict

def difference_polygon(polygons, target_polygon, solution):
    polygon_used = copy.deepcopy(polygons)
    transformed_polygons = polygonrep.perform_sequence(polygon_used, solution)
    overlay_polygons = polygonrep.union_polygons(transformed_polygons)

    diff_polygon = target_polygon.difference(overlay_polygons)

    return diff_polygon

''' 
Place by edge with respect to base_point
Edge Heuristic

'''
def match_edge(polygon_to_shift, base_point, point_ref, shift_point):

    rotateangle = cal_angle(base_point, point_ref, shift_point)
    polygon_shifted = affinity.rotate(polygon_to_shift, rotateangle, base_point)

    return polygon_shifted, rotateangle

'''
Corner Heuristic
'''
def match_corner(polygon_to_shift, reference_corner, shift_corner):

    x_shift = reference_corner[0] - shift_corner[0]
    y_shift = reference_corner[1] - shift_corner[1]
    polygon_shifted = affinity.translate(polygon_to_shift, xoff= x_shift, yoff= y_shift)
    
    return polygon_shifted, x_shift,y_shift

def get_corner_list(polygon):
    corners = list(polygon.exterior.coords)

    return corners[:-1]

def get_angles_list(polygon):
    corners = list(polygon.exterior.coords)
    angle = cal_angle(corners[0], corners[-2], corners[1])
    angle_list = [angle]
    for index in range(1,len(corners)-1): 
        angle = cal_angle(corners[index], corners[index-1], corners[index +1])
        angle_list.append(angle)
    return angle_list

def get_edge_list(polygon):
    corners = list(polygon.exterior.coords)
    edgelist = []
    for itr in range(0,len(corners)-1):
        coords = [corners[itr], corners[itr+1]]
        line = LineString(coords)
        edge = line.length
        edgelist.append(edge)
    
    return edgelist

def select_random_corner(polygon):
    corners = get_corner_list(polygon)
    index = random.randint(0, len(corners)-1)

    return corners[index], index

def select_random_egde(polygon):
    corners = get_corner_list(polygon)
    corner, index = select_random_corner(polygon)

    if index == 0 :
        next_index_list = [1, len(corners)-1]
    elif index == len(corners)-1:
        next_index_list = [0, len(corners)-2]
    else:
        next_index_list = [index-1, index+1]
    
    next_index = random.choice(next_index_list)

    return corner, corners[next_index]

def select_possible_edges(polygon_to_shift, base_point, point_ref):
    edges = get_edge_list(polygon_to_shift)

    line_ref = LineString([base_point, point_ref])
    edge_length = line_ref.length

    choice_index_list = []
    for index in range(0, len(edges)):
        if edges[index] <= edge_length:
            choice_index_list.append(index)

    return choice_index_list

def get_edge_order(polygon_to_shift, base_point, point_ref):

    edges = get_edge_list(polygon_to_shift)
    choice_edge = select_possible_edges(polygon_to_shift, base_point, point_ref)

    suitable_edge_dict = {}

    for index in range(0, len(choice_edge)):
        suitable_edge_dict[choice_edge[index]] = edges[choice_edge[index]]
    
    closest_to_edge_length = sorted(suitable_edge_dict.items(), key=lambda x: x[1], reverse=True)

    order_of_edges_to_try = []

    for element in closest_to_edge_length:
        order_of_edges_to_try.append(element[0])

    return order_of_edges_to_try

def get_suitable_corner(polygon_to_shift, base_point, point_ref):

    corners = list(polygon_to_shift.exterior.coords)

    order_of_edges = get_edge_order(polygon_to_shift, base_point, point_ref)

    if len(order_of_edges) == 0:
        return 0, 0

    return corners[order_of_edges[0]], order_of_edges[0]

def select_corner_at_index(polygon_to_shift, order_of_edges, index = 0):
    
    if len(order_of_edges) == 0:
        return 0,0
    
    corners = list(polygon_to_shift.exterior.coords)
    
    return corners[order_of_edges[index]], order_of_edges[index]

def merge_corners(polygon, precision = 0.00001):
    corners = list(polygon.exterior.coords)
    new_coordinates = []
    merged_corner = list(corners[0])
    for index in range(0, len(corners)-1):
        line = LineString([corners[index], corners[index+1]])
        if line.length <= precision:
            merged_corner[0] = (corners[index][0]+ corners[index+1][0])/2
            merged_corner[1] = (corners[index][1]+ corners[index+1][1])/2
            new_coordinates.append(tuple(merged_corner))
            corners[index+1] = tuple(merged_corner)
        else:
            new_coordinates.append(corners[index])
    coordinates = []
    for index in range(0, len(new_coordinates)-1):
        if new_coordinates[index] != new_coordinates[index+1]:
            coordinates.append(new_coordinates[index])
    
    coordinates.append(new_coordinates[-1])
    
    return Polygon(coordinates)
            


def place_polygon_by_edge(polygon_ref, polygon_to_shifted, index = 0, flip = False):
    corners = list(polygon_ref.exterior.coords)
    max_intersect_area = 0
    overlap_check = False

    possible_sequences = []
    possible_positions = []
    for ind in range(0, len(corners)-1):
        polygon_to_shift = copy.deepcopy(polygon_to_shifted)
        base_point, point_ref = corners[ind], corners[ind+1]
        order_of_edges = get_edge_order(polygon_to_shift, base_point, point_ref)

        point_shift, point_shift_index = select_corner_at_index(polygon_to_shift, order_of_edges, index)

        if point_shift == 0:
            point_shift, point_shift_index = select_random_corner(polygon_to_shift)

        polygon_shifted, x_shift, y_shift = match_corner(polygon_to_shift, base_point, point_shift)

        
        shift_point = list(polygon_shifted.exterior.coords)[point_shift_index + 1]
        polygon_placed, rotateangle = match_edge(polygon_shifted, base_point, point_ref, shift_point)
        intersect_area = polygon_placed.intersection(polygon_ref).area

        # point_shift_new = list(polygon_shifted.exterior.coords)[point_shift_index]

        # x_shift = base_point[0] - point_shift_new[0]
        # y_shift = base_point[1] - point_shift_new[1]
        
        if flip :
            mid_point = list(base_point)
            if(intersect_area <= 0.0000001):
                mid_point[0] = (base_point[0] + shift_point[0])/2
                mid_point[1] = (base_point[1] + shift_point[1])/2
                polygon_placed = affinity.rotate(polygon_placed, 180, tuple(mid_point))
                rotateangle +=180
                x_shift += mid_point[0]*2
                y_shift += mid_point[1]*2

            intersect_area = polygon_placed.intersection(polygon_ref).area

        if(intersect_area > max_intersect_area):
            max_intersect_area = intersect_area
            sequence = [x_shift, y_shift, rotateangle]
            possible_positions = [polygon_placed]
            possible_sequences = [sequence]
        
        if(abs(intersect_area - max_intersect_area) <= 0.00000001):
            sequence = [x_shift, y_shift, rotateangle]
            possible_positions.append(polygon_placed)
            possible_sequences.append(sequence)
        

    if(abs(max_intersect_area - polygon_to_shifted.area) <= 0.0000001):
        overlap_check = True
    
    random_index = random.randrange(0, len(possible_sequences))
    
    return possible_positions[random_index], possible_sequences[random_index], overlap_check

def place_polygon_by_random_edge(polygon_ref, polygon_to_shifted, index = 0):
    #need to change this randomness to remove the case where return 0, [0,0,0]
    #need to check all the possible corners and if at no-corners is possible, then return 0, [0,0,0]
    polygon_to_shift = copy.deepcopy(polygon_to_shifted)
    base_point, point_ref = select_random_egde(polygon_ref)


    order_of_edges = get_edge_order(polygon_to_shift, base_point, point_ref)

    point_shift, point_shift_index = select_corner_at_index(polygon_to_shift, order_of_edges, index)

    if point_shift == 0:
        point_shift, point_shift_index = select_random_corner(polygon_to_shift)

    polygon_shifted, x_shift, y_shift = match_corner(polygon_to_shift, base_point, point_shift)

    shift_point = list(polygon_shifted.exterior.coords)[point_shift_index + 1]
    polygon_placed, rotateangle = match_edge(polygon_shifted, base_point, point_ref, shift_point)

    return polygon_placed, [x_shift, y_shift, rotateangle]



def place_polygons_on_target(polygons, target_polygon):
    solution = [0]*(3*len(polygons))
    polygons_placed = []
    for index in range(0, len(polygons)):
        poly_placed, sequence, overlap_check = place_polygon_by_edge(target_polygon, polygons[index])
        polygons_placed.append(poly_placed)
        solution[3*index: 3*index+3] = sequence
    
    return polygons_placed, solution






