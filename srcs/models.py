"""Graph datastructures for the VRP problem.
"""

from __future__ import annotations


class graph_node:
    def __init__(self, input_id, input_demand):
        self.id = input_id
        self.demand = input_demand
        self.edges = []
        self.was_visited = False


class graph_edge:
    def __init__(self, input_id, input_cost):
        self.id = input_id
        self.cost = input_cost
        self.node_1 = None
        self.node_2 = None
        self.was_visited = False


class graph:
    def __init__(self, input_id):
        self.id = input_id
        self.edges = []
        self.nodes = []
        self.root = None

    def total_edge_cost(self):
        running_total = 0
        for edge_ in self.edges:
            running_total += edge_.cost
        return running_total

    def total_node_demand(self):
        running_total = 0
        for node_ in self.nodes:
            running_total += node_.demand
        return running_total

    def reset_nodes_and_edges(self):
        self.reset_nodes()
        self.reset_edges()

    def reset_nodes(self):
        for node_ in self.nodes:
            node_.was_visited = False

    def reset_edges(self):
        for edge_ in self.edges:
            edge_.was_visited = False


def edge_cost(node_a, node_b):
    """Cheapest undirected edge between the two nodes, or None."""
    best = None
    for edge in node_a.edges:
        if edge.node_1 is node_a:
            other = edge.node_2
        elif edge.node_2 is node_a:
            other = edge.node_1
        else:
            continue
        if other is node_b and (best is None or edge.cost < best):
            best = edge.cost
    return best
