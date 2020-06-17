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
        polygonrep.vizualize_overlap(target_polygon, [poly_placed])
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
            polygonrep.filled_poly_vizualize(diff_polygon)
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