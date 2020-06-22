import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point, LineString
from shapely import affinity
from math import sqrt
import numpy as np
import copy
from scipy.optimize import minimize
from descartes import PolygonPatch
import placement
from statistics import mean

'''
Basic line parallel to x-axis or along the initial point and origin
'''
def create_line(initial_point, length, paralleltox = True):
    
    if len(initial_point) != 2:
        print("Initial point should be a list of [x-coord,y-coord]")

    start_point = Point(initial_point[0], initial_point[1])
    origin = Point(0.0,0.0)
    
    if paralleltox :
        end_point = Point(initial_point[0]+length, initial_point[1])
    
    else :
        base_line = LineString([origin, start_point])
        scale_factor = (length/base_line.length)+1
        base_line_scaled = affinity.scale(base_line, xfact=scale_factor, yfact=scale_factor, origin= origin)
        end_point = list(base_line_scaled.coords)[1]
    
    return LineString([start_point, end_point])


''' 
    takes in base_line for angle reference and spilts out next point
'''
def add_next_point(base_line, length, angletobase):
    if base_line.geom_type != 'LineString':
        print("LineString is required as base_line")
    
    origin = list(base_line.coords)[0]
    start_point = list(base_line.coords)[1]
    scale_factor = (length/base_line.length)+1
    base_line_scaled = affinity.scale(base_line, xfact=scale_factor, yfact=scale_factor, origin= origin)
    end_point = list(base_line_scaled.coords)[1]

    line_created = LineString([start_point, end_point])
    line_to_add = affinity.rotate(line_created, angletobase, origin=start_point)
    end_point = list(line_to_add.coords)[1]

    return end_point

'''
create polygons whose center is origin
'''
def create_polygon(sides, angles):
    if len(sides) != len(angles):
        print("mismatch of number of sides with number of angles")
    
    origin = [0.0, 0.0]
    base_line = create_line(origin, sides[0])
    points = list(base_line.coords)
    for index in range(1,len(sides)-1):
        start_point = points[index]
        end_point = add_next_point(base_line, sides[index], 180 - angles[index-1])
        points.append(end_point)
        base_line = LineString([start_point,end_point])
    
    return Polygon(points)

'''
Translate to defined coordinates
'''
def translate_polygon(polygon, translate_coordinates):

    polygon_translated = affinity.translate(polygon, xoff = translate_coordinates[0],
                                                     yoff = translate_coordinates[1])
    return polygon_translated

'''
Rotate about the centroid
'''
def rotate_polygon(polygon, angle, rotation_about = (0,0)):
    
    polygon_rotated = affinity.rotate(polygon, angle, origin=rotation_about)

    return polygon_rotated

def union_polygons(polygons):
    
    polygons_overlayed = copy.deepcopy(polygons[0])

    for polygon in polygons[1:]:
        polygons_overlayed = polygons_overlayed.union(polygon)
    
    return polygons_overlayed
    
def overlay_polygons(polygons, target_polygon):
    
    polygons_overlayed = union_polygons(polygons)
    
    return target_polygon.union(polygons_overlayed)

def transform_polygon(polygon, transform_sequence):
    x_disp = transform_sequence[0]
    y_disp = transform_sequence[1]
    rot_angle = transform_sequence[2]

    rotated_polygon = rotate_polygon(polygon, rot_angle)
    translated_polygon = translate_polygon(rotated_polygon, [x_disp, y_disp])

    return translated_polygon

def perform_sequence(polygons, sequence):
    if len(polygons)*3 != len(sequence):
        print("Sequence length mismatch with number of polygons")
    
    transformed_polygons = copy.deepcopy(polygons)
    for index in range(0, len(polygons)):
        transform_sequence = sequence[3*index: 3*index+3]
        transformed_polygons[index] = transform_polygon(transformed_polygons[index], transform_sequence)
    
    return transformed_polygons

def loss_function(sequence, polygons, target_polygon):
    transformed_polygons = perform_sequence(polygons, sequence)
    polygon_union = union_polygons(transformed_polygons)

    symmetrical_diff_polygon = target_polygon.symmetric_difference(polygon_union)

    area_difference = symmetrical_diff_polygon.area

    return area_difference


def regular_right_isoscles_triangle(side_length, hypotenuse=False):
    
    origin = Point(0.0,0.0)
    first_point = Point(side_length,0.0)

    base_line = LineString([origin,first_point])

    if hypotenuse:
        next_point = Point(side_length/2, side_length/2)    
    else:
        next_point = Point(0.0,side_length)

    points = list(base_line.coords)
    points.append(next_point)  

    return Polygon(points)

def regular_parallelogram(a, b, angle):

    return create_polygon([a,b,a,b], [angle, 180-angle, angle, 180-angle])


def create_tanpieces():
    small_triangle = regular_right_isoscles_triangle(1)
    intermediate_triangle = regular_right_isoscles_triangle(2, True)
    big_triangle = regular_right_isoscles_triangle(2)
    parallelogram = regular_parallelogram(1, sqrt(2), 135)
    square = regular_parallelogram(1,1,90)

    polygons = [big_triangle, big_triangle,intermediate_triangle, parallelogram, square, small_triangle, small_triangle]

    return polygons

# def objective_function(sequence):
#     polygons = create_tanpieces()
#     target_polygon = regular_parallelogram(sqrt(8),sqrt(8), 90)

#     return loss_function(sequence,polygons,target_polygon)

def objective_function(sequence, polygons, target_polygon):
    return loss_function(sequence,polygons,target_polygon)

def plot_polygon(polygon):
    x,y = polygon.exterior.xy
    plt.plot(x,y)

def vizualizer(sequence, polygons, target_polygon):
    fig,ax =  plt.subplots(3)
    union_tan_pieces = union_polygons(perform_sequence(polygons, sequence))
    x,y = union_tan_pieces.exterior.xy
    ax[0].plot(x,y)
    ax[0].set_title('union of tan pieces')

    x_target, y_target = target_polygon.exterior.xy
    ax[1].plot(x_target, y_target,color='#6699cc', alpha=0.7,
    linewidth=3, solid_capstyle='round', zorder=2)
    ax[1].set_title('target_polygon')

    overlayed_poly = target_polygon.union(union_tan_pieces)
    x_overlay, y_overlay = overlayed_poly.exterior.xy

    ax[2].plot(x_overlay, y_overlay)
    ax[2].set_title('overlay')
    plt.show()

def vizualize(polygon):
    fig,ax =  plt.subplots()
    x,y = polygon.exterior.xy
    ax.plot(x,y)
    for interior in polygon.interiors:
        x,y = interior.xy
        ax.plot(x,y)
    ax.set_title('vizualize')
    plt.show()

def filled_poly_vizualize(polygon):
    fig = plt.figure(1, dpi=90)
    bounds = list(polygon.bounds)
    ax = fig.add_subplot(111)
    
    x_range = [bounds[0]-1, bounds[2]+1]
    y_range = [bounds[1]-1, bounds[3]+1]
    ax.set_xlim(*x_range)
    ax.set_ylim(*y_range)
    exterior_polygon = Polygon(list(polygon.exterior.coords))
    patch = PolygonPatch(exterior_polygon)
    ax.add_patch(patch)
    if len(list(polygon.interiors)) != 0:
        for interior in list(polygon.interiors):
            interior_hole = Polygon(list(interior.coords))
            interior_patch = PolygonPatch(interior_hole, fc='#FFFFFF')
            ax.add_patch(interior_patch)
    plt.show()

def vizualize_overlap(sequence, polygons, polygon):
    overlay_polygons = perform_sequence(polygons, sequence)
    fig = plt.figure(1, dpi=90)
    bounds = list(polygon.bounds)
    ax = fig.add_subplot(111)
    
    x_range = [bounds[0]-1, bounds[2]+1]
    y_range = [bounds[1]-1, bounds[3]+1]
    ax.set_xlim(*x_range)
    ax.set_ylim(*y_range)
    exterior_polygon = Polygon(list(polygon.exterior.coords))
    patch = PolygonPatch(exterior_polygon,fc='#000000')
    ax.add_patch(patch)
    if len(list(polygon.interiors)) != 0:
        for interior in list(polygon.interiors):
            interior_hole = Polygon(list(interior.coords))
            interior_patch = PolygonPatch(interior_hole, fc='#FFFFFF')
            ax.add_patch(interior_patch)

    nfloors = np.random.rand(len(overlay_polygons)) 
    cmap = plt.get_cmap('Spectral')
    colors = cmap(nfloors)

    for index in range(0,len(overlay_polygons)):
        poly = overlay_polygons[index]
        overlay_poly = Polygon(list(poly.exterior.coords))
        overlay_patch = PolygonPatch(overlay_poly, fc=colors[index])
        ax.add_patch(overlay_patch)
    plt.show()


if __name__ == "__main__":

    polygons = create_tanpieces()
    target_polygon_2 = regular_parallelogram(sqrt(8),sqrt(8), 90)
    coords = [(2-sqrt(2),0),(2+sqrt(2),0),(2+sqrt(1/2), sqrt(1/2)),(2+sqrt(2), sqrt(2)),(2+sqrt(1/2), sqrt(9/2)),(4,2+sqrt(2)),
            (0,2+sqrt(2)),(2-sqrt(1/2), sqrt(9/2)),(2-sqrt(2), sqrt(2)),(2-sqrt(1/2), sqrt(1/2))]
    target_polygon = Polygon(coords)

    # sequence0 = np.random.rand(21)
    _, sequence0, _ = placement.place_polygons_on_target(polygons, target_polygon)

    slsqp = []
    neldermead = []
    powell = []
    cobyla = []
    for i in range(0,1):
        res_SLSQP = minimize(objective_function, x0 = sequence0, args=(polygons, target_polygon), method = "SLSQP")
        res_Nelder_Mead = minimize(objective_function, x0 = sequence0, args=(polygons, target_polygon), method = "Nelder-Mead")
        res_Powell = minimize(objective_function, x0 = sequence0, args=(polygons, target_polygon), method = "Powell")
        res_COBYLA = minimize(objective_function, x0 = sequence0, args=(polygons, target_polygon), method = "COBYLA")

        slsqp.append(objective_function(res_SLSQP.x, polygons, target_polygon))
        neldermead.append(objective_function(res_Nelder_Mead.x, polygons, target_polygon))
        powell.append(objective_function(res_Powell.x, polygons, target_polygon))
        cobyla.append(objective_function(res_COBYLA.x, polygons, target_polygon))
        
        print(res_SLSQP.fun)
        print(res_Nelder_Mead.fun)
        print(res_Powell.fun)
        print(res_COBYLA.fun)
    
    print(slsqp)
    print(neldermead)
    print(powell)
    print(cobyla)
    print(mean(slsqp))
    print(mean(neldermead))
    print(mean(powell))
    print(mean(cobyla))
    vizualize_overlap(res_SLSQP.x, polygons, target_polygon)
    vizualize_overlap(res_Nelder_Mead.x, polygons, target_polygon)
    vizualize_overlap(res_Powell.x, polygons, target_polygon)
    vizualize_overlap(res_COBYLA.x, polygons, target_polygon)