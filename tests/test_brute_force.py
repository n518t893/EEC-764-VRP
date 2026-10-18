"""brute force baseline tests
"""

import math
import random
import unittest

from srcs.brute_force import solve
from srcs.models import edge_cost, graph, graph_edge, graph_node


class Instance:
    def __init__(self, dep_dem=0):  
        self.graph = graph(0)
        self._e_id = 0  
        self.depot = self.add(dep_dem)
        self.graph.root = self.depot

    def add(self, dem): 
        n = graph_node(len(self.graph.nodes), dem)
        self.graph.nodes.append(n)
        return n

    def link(self, a, b, cost):
        e = graph_edge(self._e_id, cost)  
        self._e_id += 1
        e.node_1 = a
        e.node_2 = b
        a.edges.append(e)
        b.edges.append(e)
        self.graph.edges.append(e)
        return e


def r_cost(depot, route):
    # cost of depot -> route -> depot, or None if an edge is missing
    total = 0
    prev = depot 
    for n in route:
        step = edge_cost(prev, n)
        if step is None:
            return None
        total += step
        prev = n
    if route:
        back = edge_cost(prev, depot) 
        if back is None:
            return None
        total += back
    return total


def asgns(n, v_count):
    # every way to give n customers a vehicle index
    if n == 0:
        return [[]]
    out = []
    for v in range(v_count):
        for tail in asgns(n - 1, v_count):
            out.append([v] + tail)
    return out


def ords(grp):
    # every visit order of the customers in grp
    if not grp:
        return [[]]
    out = []
    for i, n in enumerate(grp):
        rest = grp[:i] + grp[i + 1 :]
        for tail in ords(rest):
            out.append([n] + tail)
    return out


def picks(opts):
    # one order from each vehicle
    if not opts:
        return [[]]
    out = []
    for head in opts[0]:
        for tail in picks(opts[1:]):
            out.append([head] + tail)
    return out


def enum_opt(host, fleet):
    """Every assignment and every order, priced from the edges."""
    depot = host.root
    cus = [n for n in host.nodes if n is not depot] 
    if not cus:
        return 0
    if not fleet:
        return None
    best = math.inf
    for assign in asgns(len(cus), len(fleet)):
        buckets = [[] for _ in fleet]
        legal = True
        for c, v in zip(cus, assign): 
            buckets[v].append(c)
            if sum(n.demand for n in buckets[v]) > fleet[v]:
                legal = False
                break
        if not legal:
            continue
        orders = [ords(bucket) for bucket in buckets]
        for choice in picks(orders): 
            total = 0
            ok = True 
            for order in choice:
                if not order:
                    continue
                cost = r_cost(depot, order)
                if cost is None:
                    ok = False
                    break
                total += cost
            if ok and total < best:
                best = total
    if best is math.inf:
        return None
    return best


class BruteForceTests(unittest.TestCase):
    def check(self, inst, fleet, result):
        self.assertIsNotNone(result)
        cost, routes = result
        self.assertEqual(len(routes), len(fleet))
        seen = []
        total = 0
        for route, cap in zip(routes, fleet): 
            self.assertLessEqual(sum(n.demand for n in route), cap)
            priced = r_cost(inst.depot, route)
            self.assertIsNotNone(priced)
            total += priced
            seen.extend(route)
        cus = [n for n in inst.graph.nodes if n is not inst.depot] 
        self.assertCountEqual(seen, cus)
        self.assertEqual(cost, total)
        return cost, routes

    def test_out_and_back(self):
        inst = Instance()
        cus = inst.add(1)
        inst.link(inst.depot, cus, 6)

        cost, routes = self.check(inst, [5], solve(inst.graph, [5]))

        self.assertEqual(cost, 12)
        self.assertEqual(routes, [[cus]])

    def test_full_cap(self):
        inst = Instance()
        cus = inst.add(4)
        inst.link(inst.depot, cus, 2)

        cost, routes = self.check(inst, [4], solve(inst.graph, [4]))

        self.assertEqual(cost, 4)
        self.assertEqual(routes, [[cus]])

    def test_over_cap(self):
        inst = Instance()
        cus = inst.add(4)
        inst.link(inst.depot, cus, 2)

        self.assertIsNone(solve(inst.graph, [3]))

    def test_cheap_cycle(self):
        inst = Instance()
        a = inst.add(1)
        b = inst.add(1)
        c = inst.add(1)
        inst.link(inst.depot, a, 1)
        inst.link(inst.depot, b, 100)
        inst.link(inst.depot, c, 1)
        inst.link(a, b, 1)
        inst.link(b, c, 1)
        inst.link(a, c, 100)

        cost, routes = self.check(inst, [3], solve(inst.graph, [3]))

        self.assertEqual(cost, 4)
        self.assertIn(routes[0], ([a, b, c], [c, b, a]))

    def test_not_greedy(self):
        inst = Instance()
        a = inst.add(1)
        b = inst.add(1)
        c = inst.add(1)
        inst.link(inst.depot, a, 5)
        inst.link(inst.depot, b, 5)
        inst.link(inst.depot, c, 9)
        inst.link(a, b, 1)
        inst.link(a, c, 1)
        inst.link(b, c, 100)

        cost, routes = self.check(inst, [3], solve(inst.graph, [3]))

        self.assertEqual(cost, 16)
        self.assertIn(routes[0], ([b, a, c], [c, a, b]))

    def test_cheap_pair(self):
        inst = Instance()
        a = inst.add(1)
        b = inst.add(1)
        c = inst.add(1)
        inst.link(inst.depot, a, 1)
        inst.link(inst.depot, b, 1)
        inst.link(inst.depot, c, 10)
        inst.link(a, b, 1)
        inst.link(a, c, 10)
        inst.link(b, c, 10)

        cost, routes = self.check(inst, [2, 2], solve(inst.graph, [2, 2]))

        self.assertEqual(cost, 23)
        grps = [set(route) for route in routes if route] 
        self.assertCountEqual(grps, [{a, b}, {c}])
        self.assertEqual(r_cost(inst.depot, next(route for route in routes if set(route) == {a, b})), 3)
        self.assertEqual(r_cost(inst.depot, next(route for route in routes if route == [c])), 20)

    def test_heavy_cus(self):  
        inst = Instance()
        lite = inst.add(1)  
        hvy = inst.add(5)  
        inst.link(inst.depot, lite, 1)
        inst.link(inst.depot, hvy, 4)
        inst.link(lite, hvy, 1)

        cost, routes = self.check(inst, [1, 5], solve(inst.graph, [1, 5]))

        self.assertEqual(cost, 10)
        self.assertEqual(routes[0], [lite])
        self.assertEqual(routes[1], [hvy])

    def test_missing_edge(self):
        inst = Instance()
        a = inst.add(1)
        b = inst.add(1)
        inst.link(inst.depot, a, 3)
        inst.link(inst.depot, b, 4)

        self.assertIsNone(solve(inst.graph, [2]))

        cost, routes = self.check(inst, [1, 1], solve(inst.graph, [1, 1]))

        self.assertEqual(cost, 14)
        self.assertCountEqual([set(route) for route in routes], [{a}, {b}])

    def test_blocked_cus(self):
        inst = Instance()
        gate = inst.add(3)
        hid = inst.add(3)  
        inst.link(inst.depot, gate, 2)
        inst.link(gate, hid, 1)

        self.assertIsNone(solve(inst.graph, [3, 3]))

    def test_no_edge(self):
        inst = Instance()
        linked = inst.add(1)
        inst.add(1)
        inst.link(inst.depot, linked, 3)

        self.assertIsNone(solve(inst.graph, [5, 5]))

    def test_depot_demand(self):
        # depot demand 9 is not a delivery; capacity 1 still serves the customer
        inst = Instance(dep_dem=9)
        cus = inst.add(1)
        inst.link(inst.depot, cus, 5)

        cost, routes = self.check(inst, [1], solve(inst.graph, [1]))

        self.assertEqual(cost, 10)
        self.assertEqual(routes, [[cus]])

    def test_zero_demand(self):
        # demand 0 still has to be visited
        inst = Instance()
        cus = inst.add(0)
        inst.link(inst.depot, cus, 7)

        cost, routes = self.check(inst, [0], solve(inst.graph, [0]))

        self.assertEqual(cost, 14)
        self.assertEqual(routes, [[cus]])

    def test_cheap_edge(self):
        # two edges to the same customer; the route uses cost 3, not 10
        inst = Instance()
        cus = inst.add(1)
        inst.link(inst.depot, cus, 10)
        inst.link(inst.depot, cus, 3)

        cost, routes = self.check(inst, [1], solve(inst.graph, [1]))

        self.assertEqual(cost, 6)
        self.assertEqual(routes, [[cus]])

    def test_spare_v(self):
        # second vehicle is unused and stays an empty route
        inst = Instance()
        cus = inst.add(1)
        inst.link(inst.depot, cus, 4)

        cost, routes = self.check(inst, [5, 5], solve(inst.graph, [5, 5]))

        self.assertEqual(cost, 8)
        self.assertEqual(sorted(len(route) for route in routes), [0, 1])
        self.assertIn([cus], routes)

    def test_no_customer(self):
        inst = Instance()

        cost, routes = solve(inst.graph, [4, 4])

        self.assertEqual(cost, 0)
        self.assertEqual(routes, [[], []])

    def test_no_root(self):
        host = graph(1)
        host.nodes.append(graph_node(0, 1))

        with self.assertRaises(ValueError):
            solve(host, [1])

    def test_no_fleet(self):
        inst = Instance()
        cus = inst.add(1)
        inst.link(inst.depot, cus, 1)

        self.assertIsNone(solve(inst.graph, []))

    def test_matches_enum(self):
        # small random graphs must match enum_opt
        for seed in range(8):
            rng = random.Random(seed)
            for cus_count in (1, 2, 3):  # cus_count: how many customers
                inst = Instance()
                nodes = [inst.add(rng.randint(1, 3)) for _ in range(cus_count)]
                for n in nodes:
                    if rng.random() < 0.8:
                        inst.link(inst.depot, n, rng.randint(1, 9))
                for i, left in enumerate(nodes):
                    for right in nodes[i + 1 :]:
                        if rng.random() < 0.7:
                            inst.link(left, right, rng.randint(1, 9))
                fleet = [rng.randint(1, 7) for _ in range(rng.randint(1, 2))]
                want = enum_opt(inst.graph, fleet)  
                got = solve(inst.graph, fleet)  
                if want is None:
                    self.assertIsNone(got)
                    continue
                cost, _routes = self.check(inst, fleet, got)
                self.assertEqual(cost, want)


if __name__ == "__main__":
    unittest.main()
