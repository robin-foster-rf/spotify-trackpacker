""" 
Implement solution to the packing problem

we have a set of tracks each with a certain duration and want to choose a subset
of these such that the sum of the durations is close to our desired total 
playlist length

minimise abs(Sum(w_j*x_j) - W)

where W is total desired length, w_j is length of jth track, and x_j in {0,1}
is the indicator variable for whether jth track is included or not
"""

from mip import Model, xsum, minimize, BINARY
from mip.constants import OptimizationStatus

class SolverException(Exception):
    pass

def solve(W, w):
    """
    Solve the packing problem: choose subset of w which sums closest to W.

    parameters:
        W : target sum
        w : list of weights of each item
    returns:
        list of indices of items in w chosen
        solution error (solution total weight minus target)
    raises:
        SolverException if optimiser has not found optimal solution
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

# TODO: find pleasing order for playlist by key.
# possible good transitions:
#  - major to relative minor
#  - minor to relative major
#  - up 5th
#  - down 5th
# If we start with a given list of tracks with no constraints on which keys they
# have then it won't be possible in general to solve an optimum order satisfying
# all these transition constraints, but it should be possible to come up with a 
# decent solution. 

cycle_5 = [i*7%12 for i in range(12)]
pitches = dict(
    zip(range(12),
    ['C', 'Db', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B'])
)

def solve_key_order(keys):
    """
    Solve the track ordering problem: find order with pleasing key transitions

    arguments:
        keys : list of keys of tracks to reorder int integer pitch notation
    returns:
        list of indices in optimal order 
    """
    pass