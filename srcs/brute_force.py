import math

from srcs.models import edge_cost


def assign(n, v_count):
    # every way to give n customers a vehicle index
    if n == 0:
        return [[]]
    out = []
    for v in range(v_count):
        for tail in assign(n - 1, v_count):
            out.append([v] + tail)
    return out


def orders(grp):
    # every visit order of the customers in grp
    if not grp:
        return [[]]
    out = []
    for i, n in enumerate(grp):
        rest = grp[:i] + grp[i + 1 :]
        for tail in orders(rest):
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


def solve(graph, fleet):
    depot = graph.root  # depot: start and end of every route
    if depot is None:
        raise ValueError("graph has no root")
    cus = [n for n in graph.nodes if n is not depot]  # cus: customers
    if not cus:
        return 0, [[] for _ in fleet]
    if not fleet:
        return None

    best_c = math.inf  
    best_r = None  
    v_count = len(fleet)  
    for assign in assign(len(cus), v_count):
        grps = [[] for _ in fleet]  
        loads = [0 for _ in fleet]  
        fits = True
        for c, v in zip(cus, assign):  
            loads[v] += c.demand
            if loads[v] > fleet[v]:
                fits = False
                break
            grps[v].append(c)
        if not fits:
            continue
        opts = [orders(grp) for grp in grps]
        for choice in picks(opts):  
            total = 0
            ok = True  
            for order in choice:
                if not order:
                    continue
                prev = depot  
                for n in order:
                    step = edge_cost(prev, n)
                    if step is None:
                        ok = False
                        break
                    total += step
                    prev = n
                if not ok:
                    break
                back = edge_cost(prev, depot)  
                if back is None:
                    ok = False
                    break
                total += back
            if ok and total < best_c:
                best_c = total
                best_r = [list(order) for order in choice]
    if best_r is None:
        return None
    return best_c, best_r
