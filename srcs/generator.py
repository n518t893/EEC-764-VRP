"""Random graphs and fleets generator.
"""

import random

from srcs.models import graph, graph_edge, graph_node

node_id_counter = 0
edge_id_counter = 0
graph_id_counter = 0


def generate_graph(
    num_nodes=5,
    average_edge_cost=5,
    edge_cost_range=3,
    max_extra_edges_per_node=1,
    max_extra_edges_per_node_chance=50,
    average_node_demand=3,
    node_demand_range=2,
    has_root=True,
):
    global node_id_counter, edge_id_counter, graph_id_counter

    if num_nodes < 0:
        print("Error: num_nodes must be 0 at minimum.")
        return None

    output_graph = graph(graph_id_counter)
    graph_id_counter += 1

    if num_nodes == 0:
        return output_graph

    def new_demand():
        return (
            average_node_demand
            - (node_demand_range / 2)
            + random.randint(0, int(node_demand_range))
        )

    def new_cost():
        return (
            average_edge_cost
            - (edge_cost_range / 2)
            + random.randint(0, int(edge_cost_range))
        )

    def add_node():
        global node_id_counter
        created = graph_node(node_id_counter, new_demand())
        node_id_counter += 1
        output_graph.nodes.append(created)
        return created

    def add_edge(node_a, node_b):
        global edge_id_counter
        created = graph_edge(edge_id_counter, new_cost())
        edge_id_counter += 1
        created.node_1 = node_a
        created.node_2 = node_b
        node_a.edges.append(created)
        node_b.edges.append(created)
        output_graph.edges.append(created)

    if num_nodes == 1:
        add_node()
        if has_root:
            output_graph.root = output_graph.nodes[0]
        return output_graph

    add_node()
    add_node()
    add_edge(output_graph.nodes[0], output_graph.nodes[1])

    remaining = num_nodes - 2
    while remaining > 0:
        remaining -= 1
        created = add_node()
        roll = random.randint(int(max_extra_edges_per_node_chance), 100) / 100.0
        extra = int(max_extra_edges_per_node * roll)
        selected = []
        for i in range(min(2 + extra, len(output_graph.nodes) - 1)):
            choice = random.randint(0, len(output_graph.nodes) - 2 - i)
            while choice in selected:
                choice += 1
            selected.append(choice)
        for index in selected:
            # The new node is last. An incremented index can walk onto it.
            if index >= len(output_graph.nodes) - 1:
                continue
            add_edge(created, output_graph.nodes[index])

    if has_root:
        output_graph.root = output_graph.nodes[random.randint(0, len(output_graph.nodes) - 1)]

    return output_graph


def generate_fleet(
    graph_to_cover,
    average_fleet_size=2,
    fleet_size_range=2,
    fleet_capacity_average_multiplier=1.5,
    fleet_capacity_multiplier_range=1.0,
):
    graph_cost_to_consider = graph_to_cover.total_node_demand()

    fleet_size = (
        average_fleet_size
        - (fleet_size_range / 2)
        + random.randint(0, int(fleet_size_range))
    )
    if fleet_size < 1:
        fleet_size = 1
    fleet_size = int(fleet_size)

    fleet_capacity_multiplier = (
        fleet_capacity_average_multiplier
        - (fleet_capacity_multiplier_range / 2)
        + random.randint(0, int(fleet_capacity_multiplier_range))
    )
    if fleet_capacity_multiplier < 1.5:
        fleet_capacity_multiplier = 1.5

    fleet_capacity_total = int(graph_cost_to_consider * fleet_capacity_multiplier)

    fleet_list = []
    for i in range(fleet_size):
        if i == fleet_size - 1:
            fleet_list.append(fleet_capacity_total)
            continue

        vehicle_capacity = random.randint(0, fleet_capacity_total)
        fleet_capacity_total -= vehicle_capacity
        fleet_list.append(vehicle_capacity)

    return fleet_list
