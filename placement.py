import polygonrep
from shapely.geometry import Polygon, Point, LineString
from shapely import affinity
from math import sqrt, atan, degrees, acos
import numpy as np
import random
import copy
from more_itertools import unique_everseen
from shapely.ops import transform
from shapely.validation import make_valid

def cross_sign(x1, y1, x2, y2):
    return x1 * y2 > x2 * y1

def calc_rot_angle(rot_line_point_a, rot_line_point_b, ref_line_point_a, ref_line_point_b):
    line_rot = LineString([rot_line_point_a, rot_line_point_b])
    line_ref = LineString([ref_line_point_a, ref_line_point_b])

    length_rot = line_rot.length
    length_ref = line_ref.length

    x_diff_rot = rot_line_point_b[0] - rot_line_point_a[0]
    y_diff_rot = rot_line_point_b[1] - rot_line_point_a[1]

    x_diff_ref = ref_line_point_b[0] - ref_line_point_a[0]
    y_diff_ref = ref_line_point_b[1] - ref_line_point_a[1]

    dot_product = x_diff_rot*x_diff_ref + y_diff_rot*y_diff_ref
    cos_theta = (dot_product)/(length_rot*length_ref)

    if cos_theta > 1:
        cos_theta = 1
    elif cos_theta < -1:
        cos_theta = -1
    
    angle = degrees(acos(cos_theta))

    ## check for convex polygon and return the inside angle
    if cross_sign(x_diff_rot, y_diff_rot, x_diff_ref, y_diff_ref):
        return angle
    else:
        return 360-angle


def edge_match(polygon_to_shift, point_rot_a, point_rot_b, point_ref_a, point_ref_b):

    rotateangle = calc_rot_angle(point_rot_a, point_rot_b, point_ref_a, point_ref_b)
    polygon_shifted = affinity.rotate(polygon_to_shift, rotateangle, origin=(0,0))

    return polygon_shifted, rotateangle

'''
Corner Heuristic
'''
def corner_match(polygon_to_shift, reference_corner, shift_corner):

    x_shift = reference_corner[0] - shift_corner[0]
    y_shift = reference_corner[1] - shift_corner[1]
    polygon_shifted = affinity.translate(polygon_to_shift, xoff= x_shift, yoff= y_shift)
    
    return polygon_shifted, x_shift,y_shift

def makevaild(polygon):
    if not(polygon.is_valid):
        polygon.buffer(0)
    return polygon
    

def get_corner_list(polygon):
    # print(polygon.geom_type)
    # print(polygon.wkt)
    if(polygon.geom_type == 'GeometryCollection'):
        return list([])
    polygon = transform(lambda x,y: (round(x,3),round(y,3)), polygon)
    corners = list(polygon.exterior.coords)
    if len(polygon.interiors):
        interiors = polygon.interiors
        for interior in list(interiors):
            interior_corners = list(interior.coords)
            corners.extend(interior_corners)
    return list(unique_everseen(corners))

def get_angles_list(polygon):
    corners = list(polygon.exterior.coords)
    angle = calc_rot_angle(corners[0], corners[-2],corners[0], corners[1])
    angle_list = [angle]
    for index in range(1,len(corners)-1): 
        angle = calc_rot_angle(corners[index], corners[index-1],corners[index], corners[index +1])
        angle_list.append(angle)
    
    if len(polygon.interiors):
        for interior in list(polygon.interiors):
            angles = get_angles_list(Polygon(list(interior.coords)))
            angle_list.extend(angles)
    return angle_list

def get_edge_list(polygon):
    corners = get_corner_list(polygon)
    edge_mat = []
    for itr in range(0,len(corners)):
        edgelist = []
        for next_itr in range(0,len(corners)):
            coords = [corners[itr], corners[next_itr]]
            line = LineString(coords)
            edge = line.length
            edgelist.append(edge)
        edge_mat.append(edgelist)
    edge_mat = list(np.around(np.array(edge_mat),3))
    
    return edge_mat, len(corners)

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

def select_possible_edges(polygon_to_place, base_point, point_ref):
    edges = get_edge_list(polygon_to_place)

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
    if not(len(corners)):
        return polygon
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
    interiors = []
    if len(polygon.interiors) != 0:
        for interior in list(polygon.interiors):
            merge_corners_interior = merge_corners(Polygon(list(interior.coords)))
            interiors.append(list(merge_corners_interior.exterior.coords))
            coordinates = list(np.around(np.array(coordinates),3))
            interiors = list(np.around(np.array(interiors),3))
        return Polygon(coordinates, interiors)
    
    coordinates = list(np.around(np.array(coordinates),3))
    return Polygon(coordinates)

def remove_lines(polygon):
    corners = list(polygon.exterior.coords)
    corners = list(np.around(np.array(corners),3))
    if (len(corners) < 3):
        return polygon
    coordinates = []
    for index in range(0,len(corners)-2):
        coordinates.append(corners[index])
        if(corners[index][0] == corners[index+2][0] and corners[index][1] == corners[index+2][1]):
            index = index+2
    coordinates.append(corners[-2])
    coordinates.append(corners[-1])
    return Polygon(coordinates)

def get_diff_polygon(polygon_to_place, target_polygon, sequence):

    polygon_transformed = polygonrep.transform_polygon(polygon_to_place, sequence)
    diff_polygon = target_polygon.difference(polygon_transformed)
    diff_check = False
    # diff_polygon = transform(lambda x,y: (round(x,3),round(y,3)), diff_polygon)
    diff_polygon = make_valid(diff_polygon)
    if diff_polygon.geom_type == 'MultiPolygon' or diff_polygon.geom_type == 'GeometryCollection':
        max_area = 0
        for polygon in diff_polygon:
            diff_poly_area = polygon.area
            if(diff_poly_area > max_area):
                max_area = diff_poly_area
                diff_polygon = polygon
        diff_check = True
    # diff_polygon = merge_corners(diff_polygon)
    # diff_polygon = remove_lines(diff_polygon)
    if not(diff_polygon.is_valid):
        diff_polygon.buffer(0)

    return diff_polygon

def pre_process(target_polygon, polygon_to_place, not_edge_match= False):
    corners_to_place = get_corner_list(polygon_to_place)
    edge_mat, corner_len = get_edge_list(target_polygon)

    corners_place_at = []
    corners_place_to = []
    for corner_ind in range(0,len(corners_to_place)):
        base_point = corners_to_place[corner_ind]
        if corner_ind == (len(corners_to_place) -1) :
            next_ind = 0
        else:
            next_ind = corner_ind+1
        next_point = corners_to_place[next_ind]
        line_ref = LineString([base_point, next_point])
        edge_length = line_ref.length
        corners_place_to.append((corner_ind, next_ind))

        possible_corner = []
        if not_edge_match:
            for itr in range(0, corner_len):
                for next_itr in range(itr,corner_len):
                    if(edge_length <= edge_mat[itr][next_itr]):
                        possible_corner.append((itr, next_itr))
                        possible_corner.append((next_itr, itr))
            corners_place_at.append(possible_corner)
        else:
            for itr in range(0, corner_len):
                if itr == (corner_len-1):
                    next_itr = 0
                else:
                    next_itr = itr+1
                if(edge_length <= edge_mat[itr][next_itr]):
                    possible_corner.append((itr, next_itr))
                    possible_corner.append((next_itr, itr))
            corners_place_at.append(possible_corner)
    
    if(len(corners_place_at) != len(corners_to_place)):
        print("Can't place the polygon as target can't contain given polygon")
    
    return corners_place_to, corners_place_at

def flip_polygon(polygon):
    return transform(lambda x,y: (x,-y), polygon)

def place_polygon_by_edge_helper(target_polygon, polygon_to_place, pres= 0.00001, flip= False, check_overlap=False):
    corners_toplace, corners_placeat = pre_process(target_polygon, polygon_to_place) 
    corners_toplace_list = get_corner_list(polygon_to_place)
    corners_placeat_list = get_corner_list(target_polygon)
    sequence_list = []
    check_flip = 0
    max_overlap = 0

    for index in range(0,len(corners_toplace)):
        (base_ind, next_ind) = corners_toplace[index]
        base_point = corners_toplace_list[base_ind]
        next_point = corners_toplace_list[next_ind]
        for (ref_base_ind, ref_next_ind) in corners_placeat[index]:
            ref_base_point = corners_placeat_list[ref_base_ind]
            ref_next_point = corners_placeat_list[ref_next_ind]
            poly_placed, rot_angle = edge_match(polygon_to_place, base_point, next_point, ref_base_point, ref_next_point)
            placed_list = get_corner_list(poly_placed)
            poly_placed_shifted, x_shift, y_shift = corner_match(poly_placed, ref_base_point, placed_list[base_ind])
            intersect_area = poly_placed_shifted.intersection(target_polygon).area
            polygon_area = poly_placed_shifted.area
            if check_overlap:
                if(polygon_area - intersect_area) <= pres:
                    max_overlap = intersect_area
                    sequence = [x_shift, y_shift, rot_angle]
                    sequence = list(np.around(np.array(sequence),3))
                    sequence_list.append(sequence)
            else :
                if(intersect_area) > max_overlap:
                    max_overlap = intersect_area
                    sequence = [x_shift, y_shift, rot_angle]
                    sequence = list(np.around(np.array(sequence),3))
                    sequence_list = [sequence]
                elif(intersect_area) == max_overlap:
                    max_overlap = intersect_area
                    sequence = [x_shift, y_shift, rot_angle]
                    sequence = list(np.around(np.array(sequence),3))
                    sequence_list.append(sequence)

    if flip:
        flip_poly = flip_polygon(polygon_to_place)
        sequence_list_flip, flip_check = place_polygon_by_edge_helper(target_polygon, flip_poly, flip=False, check_overlap=check_overlap)
        if(len(sequence_list) == 0):
            check_flip = 1
            sequence_list = sequence_list_flip

    # print("max_overlap")
    # print(max_overlap)

    
    return sequence_list, check_flip

def place_polygon_by_edge(target_polygon, polygon_to_place, pres= 0.00001, flip= False, check_overlap=False):
    sequence_list, check_flip = place_polygon_by_edge_helper(target_polygon, polygon_to_place, pres, flip, check_overlap)
    # print("sequence_list")
    # print(len(sequence_list))

    if(len(sequence_list) == 0):
        # print("No sequence possible with full overlap")
        sequence_list, check_flip = place_polygon_by_edge_helper(target_polygon, polygon_to_place, pres, flip, check_overlap=False)
        if(len(sequence_list) == 0):
            return [0,0,0],0
        return sequence_list[0], check_flip
    else:
        rand_ind = random.randrange(0,len(sequence_list))
        return sequence_list[rand_ind], check_flip

def place_polygons_on_target(polygons, target_polygon):
    solution = [0]*(3*len(polygons))
    polygons_placed = []
    for index in range(0, len(polygons)):
        sequence, flip_check = place_polygon_by_edge(target_polygon, polygons[index])
        if flip_check:
            flip_poly = flip_polygon(polygons[index])
            polygons[index] = flip_poly

        solution[3*index: 3*index+3] = sequence
        # polygonrep.filled_poly_vizualize(polygon_transformed)

        target_polygon_diff = get_diff_polygon(polygons[index], target_polygon,sequence)
        target_polygon = target_polygon_diff
        # target_polygon = merge_corners(target_polygon_diff)
        # target_polygon = remove_lines(target_polygon)
        # polygonrep.filled_poly_vizualize(target_polygon_diff)
        # polygonrep.filled_poly_vizualize(target_polygon)
    
    return polygons_placed, solution, flip_check
