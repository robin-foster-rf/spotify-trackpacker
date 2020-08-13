""" 
Implement solution to the knapsack problem

we have a set of tracks each with a certain duration and want to choose a subset
of these such that the sum of the durations is close to our desired total 
playlist length

minimise |\Sum w_j x_j - W|

where W is total desired length, w_j is length of jth track, and x_j \in {0,1}
is the indicator variable for whether jth track is included or not
"""

from mip import Model, xsum, minimize, BINARY
from mip.constants import OptimizationStatus

class SolverException(Exception):
    pass

def solve(W, w):
    """

    inputs:
        W : target sum
        w : list of weights of each item
    returns:
        list of indices of items in w chosen
        solution error (solution total weight minus target)
    """
    I = range(len(w))
    m = Model('targetsum')
    # indicator variables for whether track included or not
    x = [m.add_var(var_type=BINARY) for i in I]
    # minimise difference between sum of track lengths and desired total length
    # since this would be minimised by including zero tracks, add a positivity
    # constraint. 
    # It seems that no solvers can do the min(sum(w_i)-W)^2 problem, but this 
    # version works pretty well
    m.objective = minimize(xsum(x[i]*w[i] for i in I) - W)
    m += (xsum(x[i]*w[i] for i in I) - W) >= 0
    
    m.optimize()

    if m.status==OptimizationStatus.OPTIMAL:
        selected = [i for i in I if x[i].x>=0.99]
        return selected, m.objective_value
    else:
        raise SolverException


def print_solution(tracks, selected, error):
    for i, t in enumerate(tracks):
        if i in selected:
            print(t)
    print(error)
