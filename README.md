# Capacitated Vehicle Routing

[Google doc](https://docs.google.com/document/d/1Rf0rwMX98U-IdQzmQTOf3c43Hc8d0Kif1owEiC_FnJ4/edit)

[docs/algorithms.md](docs/algorithms.md) keep the 3 algos info. 

[docs/timeline.md](docs/timeline.md) have the timeline

```bash
python -m unittest discover -s tests -v
```

`srcs/models.py` cvrp model

`srcs/generator.py` generate a random graph and a fleet sized from the total node demand.

`srcs/brute_force.py` tries every vehicle assignment and every customer order and returns the cheapest feasible routes.

`tests/test_brute_force.py` checks routes, capacity, missing edges, and that the search matches an independent enumeration on small random graphs.
