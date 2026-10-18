# 3 algorithms
1. Nearest Neighbor
2. Clarke-Wright Savings
3. Sweep

## Nearest Neighbor

Start at the depot. Go to the closest unvisited customer. Repeat until the vehicle is full or all customers are served.

| | |
| --- | --- |
| Time | `O(n^2)` |
| Space | `O(n)` |
| Correctness | Repeatedly selects the closest unvisited customer that the current vehicle can still serve. Each customer is visited at most once and removed from the unvisited set after selection. The algorithm stops when every customer is on a route and every route returns to the depot. When the fleet has enough capacity, the result is a feasible routing. It is not guaranteed to be optimal. |
| Error bound | No fixed worst-case approximation bound for general VRP. A locally close stop can force a much longer route later. Quality has to be measured on instances. |
| Pros | Very simple, easy to implement, fast. |
| Cons | Often produces poor routes. Can get trapped in local decisions. |

```
NearestNeighbor(graph, depot)
  route <- [depot]
  mark depot as visited
  current <- depot
  while unvisited customers remain
    nearest_customer <- null
    best_distance <- infinity
    for each customer
      if customer not visited and
         distance(current, customer) < best_distance
        nearest_customer <- customer
        best_distance <- distance(current, customer)
    add nearest_customer to route
    mark nearest_customer as visited
    current <- nearest_customer
  add depot to route
  return route
```

## Clarke-Wright Savings

Start with one route per customer. Merge routes when doing so saves travel cost.

| | |
| --- | --- |
| Time | `O(n^2 log n)` |
| Space | `O(n)` |
| Correctness | The start is one route per customer, which is feasible aside from the fleet count. A merge is accepted only when it keeps the route structure and the combined demand fits in a vehicle. Every accepted merge stays feasible, so the result is a feasible VRP solution. It does not guarantee the minimum travel cost. |
| Error bound | No general worst-case error bound is known for arbitrary VRP instances. In practice it is usually much better than a simple greedy tour, and it is a common production heuristic. |
| Pros | Famous VRP heuristic. Usually much better than Nearest Neighbor. Handles vehicle capacities naturally. |
| Cons | More complex implementation. Not guaranteed optimal. |

The saving of joining customers `i` and `j` is the two depot legs you drop minus the new edge between them:

```
saving(i, j) = distance(depot, i) + distance(depot, j) - distance(i, j)
```

```
ClarkeWright(graph, depot)
  routes <- one route per customer
  savings_list <- empty list
  for each customer i
    for each customer j where j > i
      savings <- distance(depot, i)
               + distance(depot, j)
               - distance(i, j)
      add (i, j, savings) to savings_list
  sort savings_list in descending order
  for each entry (i, j, savings)
    if routes containing i and j can be merged
       without violating capacity constraints
      merge the two routes
  return routes
```

## Sweep

Convert customer coordinates to angles around the depot. Sweep clockwise. Assign customers to vehicles until capacity is reached.

| | |
| --- | --- |
| Time | `O(n log n)` |
| Space | `O(n^2)` |
| Correctness | Customers are ordered by angle around the depot and assigned while capacity holds. Each customer is assigned once, and every route begins and ends at the depot. When the fleet has enough capacity, the result is feasible. It is not guaranteed to be optimal. |
| Error bound | No fixed worst-case approximation bound for general VRP. Quality depends on how customers sit around the depot, so it is judged by experiment against an exact solution. |
| Pros | Very fast. Good clustering behavior. Common VRP benchmark algorithm. |
| Cons | Requires 2D coordinates. Quality depends on customer distribution. |

```
Sweep(graph, depot, vehicle_capacity)
  for each customer
    angle(customer) <- angle from depot
  sort customers by angle
  routes <- empty list
  current_route <- empty
  current_load <- 0
  for each customer in sorted order
    if current_load + demand(customer) <= vehicle_capacity
      add customer to current_route
      current_load <- current_load + demand(customer)
    else
      add current_route to routes
      current_route <- [customer]
      current_load <- demand(customer)
  if current_route not empty
    add current_route to routes
  return routes
```
