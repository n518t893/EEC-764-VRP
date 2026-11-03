"""randomized graph tests, test for maximum graph size that our systems can solve
"""

import math
import random
import unittest
import time

from brute_force import solve
from models import edge_cost, graph, graph_edge, graph_node
from generator import generate_graph, generate_fleet

#Configure these manually to see different types of graphs in testing, and to test the limits that your system has before things start to get really slow
TARGET_NUM_NODES=5
NUM_NODES_RANGE=3
AVERAGE_EDGE_COST=5
EDGE_COST_RANGE=3
MAX_EXTRA_EDGES_PER_NODE=1
MAX_EXTRA_EDGES_PER_NODE_CHANCE=50
AVERAGE_NODE_DEMAND=3
NODE_DEMAND_RANGE=2

AVERAGE_FLEET_SIZE=3
FLEET_SIZE_RANGE=1
FLEET_CAPACITY_AVERAGE_MULTIPLIER=2.5
FLEET_CAPACITY_MULTIPLIER_RANGE=1.0

MAX_GRAPH_REATTEMPTS = 1
MAX_SINGLE_ATTEMPTS = 10

#note: Setting this to true will override the above parameters
RANDOMLY_GENERATE_PARAMETERS = True
#10 should be the "baseline" amount of points, more means you are scaling up the graph to be bigger in every way that it could make sense to do so
RANDOM_PARAMETERS_POINT_LEVEL = 100

#This will make the test run repeatedly until it takes some certian amount of time. Needs points enabled otherwise it does nothing
RUN_SCALING_TESTS = True
#this is how many more points each sequential test gets
SCALING_TEST_POINT_SCALING = 10
#this is the time needed to pass before a test point value is decided to be correct and no more tests should be run
SCALING_TEST_TIME_TARGET = 30
MAX_SCALING_TEST_REATTEMPTS = 10

def generate_parameters(point_level):
    global TARGET_NUM_NODES, NUM_NODES_RANGE, AVERAGE_EDGE_COST, EDGE_COST_RANGE, MAX_EXTRA_EDGES_PER_NODE, MAX_EXTRA_EDGES_PER_NODE_CHANCE, AVERAGE_NODE_DEMAND, NODE_DEMAND_RANGE
    global AVERAGE_FLEET_SIZE, FLEET_SIZE_RANGE, FLEET_CAPACITY_AVERAGE_MULTIPLIER, FLEET_CAPACITY_MULTIPLIER_RANGE
    global RANDOMLY_GENERATE_PARAMETERS, RANDOM_PARAMETERS_POINT_LEVEL

    #some variables for configuration/baselines
    percentage_variation = 0.01
    #Other than the above line, these are NOT supposed to be configurable
    baseline_points = 100
    
    baseline_target_nodes = 5
    baseline_num_nodes_range = 3
    baseline_average_edge_cost = 5
    baseline_edge_cost_range = 3
    baseline_max_extra_edges_per_node = 1
    baseline_max_extra_edges_per_node_chance = 50
    baseline_average_node_demand = 3
    baseline_node_demand_range = 2
    baseline_average_fleet_size = 3
    baseline_fleet_size_range = 1
    baseline_fleet_capacity_average_multiplier = 2.5
    baseline_fleet_capacity_multiplier_range = 1.0

    #this randomly sets the parameters in a scaling way. Some scale with how "big" the graph to test is, some do not.
    #parameters that scale normally with points
    TARGET_NUM_NODES = int((point_level + (random.randint(-1 * point_level, point_level) * percentage_variation)) * (baseline_target_nodes / baseline_points))
    NUM_NODES_RANGE = int((point_level + (random.randint(-1 * point_level, point_level) * percentage_variation)) * (baseline_num_nodes_range / baseline_points))
    AVERAGE_EDGE_COST = int((point_level + (random.randint(-1 * point_level, point_level) * percentage_variation)) * (baseline_average_edge_cost / baseline_points))
    EDGE_COST_RANGE = int((point_level + (random.randint(-1 * point_level, point_level) * percentage_variation)) * (baseline_edge_cost_range / baseline_points))
    MAX_EXTRA_EDGES_PER_NODE = int((point_level + (random.randint(-1 * point_level, point_level) * percentage_variation)) * (baseline_max_extra_edges_per_node / baseline_points))
    AVERAGE_NODE_DEMAND = int((point_level + (random.randint(-1 * point_level, point_level) * percentage_variation)) * (baseline_average_node_demand / baseline_points))
    NODE_DEMAND_RANGE = int((point_level + (random.randint(-1 * point_level, point_level) * percentage_variation)) * (baseline_node_demand_range / baseline_points))
    AVERAGE_FLEET_SIZE = int((point_level + (random.randint(-1 * point_level, point_level) * percentage_variation)) * (baseline_average_fleet_size / baseline_points))
    FLEET_SIZE_RANGE = int((point_level + (random.randint(-1 * point_level, point_level) * percentage_variation)) * (baseline_fleet_size_range / baseline_points))

    #parameters that do not scale normally with points
    MAX_EXTRA_EDGES_PER_NODE_CHANCE = int((point_level + (random.randint(-1 * point_level, point_level) * percentage_variation)) * (baseline_max_extra_edges_per_node / point_level))
    FLEET_CAPACITY_AVERAGE_MULTIPLIER = int((point_level + (random.randint(-1 * point_level, point_level) * percentage_variation)) * (baseline_fleet_capacity_average_multiplier / point_level))
    FLEET_CAPACITY_MULTIPLIER_RANGE = int((point_level + (random.randint(-1 * point_level, point_level) * percentage_variation)) * (baseline_fleet_capacity_multiplier_range / point_level))

def run_single_test():
    global TARGET_NUM_NODES, NUM_NODES_RANGE, AVERAGE_EDGE_COST, EDGE_COST_RANGE, MAX_EXTRA_EDGES_PER_NODE, MAX_EXTRA_EDGES_PER_NODE_CHANCE, AVERAGE_NODE_DEMAND, NODE_DEMAND_RANGE
    global AVERAGE_FLEET_SIZE, FLEET_SIZE_RANGE, FLEET_CAPACITY_AVERAGE_MULTIPLIER, FLEET_CAPACITY_MULTIPLIER_RANGE
    global RANDOMLY_GENERATE_PARAMETERS, RANDOM_PARAMETERS_POINT_LEVEL

    if RANDOMLY_GENERATE_PARAMETERS:
        generate_parameters(RANDOM_PARAMETERS_POINT_LEVEL)

    #first, the generator doesn't randomize node count, so do that here
    generated_node_count = TARGET_NUM_NODES - (NUM_NODES_RANGE / 2) + random.randint(0, NUM_NODES_RANGE)
    if generated_node_count < 1:
        generated_node_count = 1

    #now, randomly generate the graph to be used
    generated_graph = generate_graph(num_nodes=generated_node_count, average_edge_cost=AVERAGE_EDGE_COST, edge_cost_range=EDGE_COST_RANGE, max_extra_edges_per_node=MAX_EXTRA_EDGES_PER_NODE, max_extra_edges_per_node_chance=MAX_EXTRA_EDGES_PER_NODE_CHANCE, average_node_demand=AVERAGE_NODE_DEMAND, node_demand_range=NODE_DEMAND_RANGE, has_root=True)

    #randomly generate a fleet to navigate this graph
    generated_fleet = generate_fleet(generated_graph, average_fleet_size=AVERAGE_FLEET_SIZE, fleet_size_range=FLEET_SIZE_RANGE, fleet_capacity_average_multiplier=FLEET_CAPACITY_AVERAGE_MULTIPLIER, fleet_capacity_multiplier_range=FLEET_CAPACITY_MULTIPLIER_RANGE)

    #display graph and parameter info
    print("--------------------")
    print("Tested parameters:")
    print("Using point-generated parameters?:", str(RANDOMLY_GENERATE_PARAMETERS))
    print("Point-generated parameters cost:", str(RANDOM_PARAMETERS_POINT_LEVEL))
    print()
    print("Average number of nodes:", str(TARGET_NUM_NODES))
    print("Possible number of nodes range:", str(NUM_NODES_RANGE))
    print("Average edge cost:", str(AVERAGE_EDGE_COST))
    print("Edge cost range:", str(EDGE_COST_RANGE))
    print("Possible additional edges beyond 2 generated on/for each node:", str(MAX_EXTRA_EDGES_PER_NODE))
    print("Chance of maximum additional edge quantity being added to each node:", str(MAX_EXTRA_EDGES_PER_NODE_CHANCE))
    print("Average demand per node:", str(AVERAGE_NODE_DEMAND))
    print("Demand range:", str(NODE_DEMAND_RANGE))
    print()
    print("Average number of Vehicles in fleet:", str(AVERAGE_FLEET_SIZE))
    print("Range for number of Vehicles in fleet:", str(FLEET_SIZE_RANGE))
    print("Average percentage of total needed demand that is distributed among fleet's Vehicles:", str(FLEET_CAPACITY_AVERAGE_MULTIPLIER))
    print("Range for percentage of total needed demand that is distributed among fleet's Vehicles:", str(FLEET_CAPACITY_MULTIPLIER_RANGE))
    print()
    print("--------------------")
    print("Tested graph:")
    print("Total graph node count:", str(len(generated_graph.nodes)))
    print("Total graph demand:", str(generated_graph.total_node_demand()))
    print("Total graph edge count:", str(len(generated_graph.edges)))
    print("Total graph edge cost:", str(generated_graph.total_edge_cost()))
    print("Graph root node id:", str(generated_graph.root.id))
    #perhaps in the future, add things here to display more facts about the graph?
    print()
    print("--------------------")
    print("Tested fleet:")
    print("Total fleet size:", str(len(generated_fleet)))
    print("Each Vehicle is 1 of the ints from the following list, which represents that vehicle's capacity.")
    print(str(generated_fleet))
    print()
    print("--------------------")

    #Set up timing and run brute force solver
    print("Beginning solve")
    valid_solution_found = False
    current_graph_attempt = 0

    while not valid_solution_found:
        current_graph_attempt += 1
        if current_graph_attempt > MAX_GRAPH_REATTEMPTS:
            print("Too many failures in a row. Aborting solve attempt.")
            return None

        solve_begin_time = time.time()
        generated_solution = solve(generated_graph, generated_fleet)
        solve_ending_time = time.time()

        if generated_solution is None:
            print("Invalid graph was generated, re-attempting solve.")
        
        else:
            valid_solution_found = True
            print("Solve completed.")

    #display normal results
    solve_time = solve_ending_time - solve_begin_time
    print(f"Solved in: {solve_time:.6f} seconds")

    return solve_time

def main():
    global RANDOM_PARAMETERS_POINT_LEVEL

    if not RANDOMLY_GENERATE_PARAMETERS or not RUN_SCALING_TESTS:
        current_single_attempt = 0
        while True:
            current_single_attempt += 1
            result = run_single_test()

            if result is None and current_single_attempt > MAX_SINGLE_ATTEMPTS:
                print("Too many failed attempts, aborting tests.")
                break 

            elif result is None:
                print("Invalid setup, reattempting.")

            else:
                break

    else:
        prev_time = -1
        current_scaling_test_attempt = 0

        while prev_time < SCALING_TEST_TIME_TARGET:
            current_scaling_test_attempt += 1
            if current_scaling_test_attempt > MAX_SCALING_TEST_REATTEMPTS:
                print("Too many failed scaling tests, aborting.")
                return 
            
            #scale points each time after the 1st
            if not prev_time == -1:
                RANDOM_PARAMETERS_POINT_LEVEL += SCALING_TEST_POINT_SCALING

            print("Running test with points:", str(RANDOM_PARAMETERS_POINT_LEVEL))
            print("===================================")
            prev_time = run_single_test()
            print("===================================")

            if prev_time is None:
                prev_time = -1
                print("Failed scaling test, reattempting.")
                continue

            if (prev_time < SCALING_TEST_TIME_TARGET):
                print("Not enough time elapsed. Continuing scaling tests.")
                current_scaling_test_attempt = 0

            else:
                print("Scaling tests completed with a satisfactory time with a final point value of:", str(RANDOM_PARAMETERS_POINT_LEVEL))
                current_scaling_test_attempt = 0
                return RANDOM_PARAMETERS_POINT_LEVEL

#main function caller
if __name__ == "__main__":
    main()