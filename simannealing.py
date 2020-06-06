import polygonrep
from sys import float_info
from shapely.geometry import Polygon, Point, LineString
from shapely import affinity
from math import sqrt, exp
import numpy as np
import random

import polyplacement

# • Compute the difference polygon D between the target and the current solution.
# • Consider the tentative solution S
# 0
# formed by taking a random polygon P and placing it
# on D using the corner heuristic.
# • With some probability p(S, S0
# , i) (where i is the number of iterations completed so far),
# and their costs, we move from S to S
# 0

'''
Need to think about deep copy probs in simannealing solution
'''
'''

###################################### NEED TO WORK ON THIS ####################
'''
def get_initial_solution(polygons, target_polygon):
    polygons_placed, initial_sol = polyplacement.place_polygons_on_target(polygons, target_polygon)
    return initial_sol

def temperature_function(iteration):
    return 0.01/(iteration)


def get_next_solution(polygons, target_polygon, solution):

    index = random.randrange(len(polygons))
    solution[3*index:3*index+3] = [0]*3
    diff_polygon = difference_polygon(polygons, target_polygon, solution)
    poly_placed, sequence, overlap_check = polyplacement.place_polygon_by_edge(diff_polygon, polygons[index])
    solution[3*index: 3*index+3] = sequence
    return solution

'''
############ code from here done #######################
'''
def prob_function(polygons, target_polygon, initial_solution, next_solution, iteration):
    loss_initial_solution = polygonrep.loss_function(initial_solution, polygons, target_polygon)
    loss_next_solution = polygonrep.loss_function(next_solution, polygons, target_polygon)
    prob = exp((loss_initial_solution - loss_next_solution) / (temperature_function(iteration)))

    if prob > 1:
        return 1
    else:
        return prob


def difference_polygon(polygons, target_polygon, solution):
    transformed_polygons = polygonrep.perform_sequence(polygons, solution)
    overlay_polygons = polygonrep.union_polygons(transformed_polygons)

    diff_polygon = target_polygon.difference(overlay_polygons)

    if diff_polygon.geom_type == 'MultiPolygon':
        random_index = random.randrange(len(diff_polygon))
        diff_polygon = diff_polygon[random_index]

    return diff_polygon

def simannealing_solve(polygons, target_polygon, initial_solution):
    iteration = 1
    solution = initial_solution
    eps = float_info.epsilon
    itr = 0
    loss = polygonrep.loss_function(solution, polygons, target_polygon)
    min_loss = loss
    while loss > eps:
        if loss < min_loss:
            print("min loss: " + str(min_loss))
            print("solution: " + str(solution))
            min_loss = loss
        # print(min_loss)
        itr += 1
        # print(itr)
        next_solution = get_next_solution(polygons, target_polygon, solution)
        prob = prob_function(polygons, target_polygon, solution, next_solution, iteration)
        random_num = random.random()
        # print(next_solution)
        if random_num < prob :
            solution = next_solution
        iteration +=1
        loss = polygonrep.loss_function(solution, polygons, target_polygon)

    return solution



def solve_target(polygons, target_polygon):
    initial_sol = get_initial_solution(polygons, target_polygon)
    solution_simanneal = simannealing_solve(polygons, target_polygon, initial_sol)
    print(solution_simanneal)

    # polygonrep.vizualizer(solution_simanneal, polygons, target_polygon)

    return True