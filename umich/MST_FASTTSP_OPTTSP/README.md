# Graph Algorithms: MST and TSP

Three graph algorithms on 2-D point sets with region constraints.

## What it does

- **MST** — Minimum Spanning Tree using a Prim-like dense-graph approach with region boundary constraints
- **FASTTSP** — Fast Traveling Salesman Problem heuristic using nearest-neighbor insertion
- **OPTTSP** — Optimal TSP via branch-and-bound with MST lower-bound pruning

## Files

- `zoo.cpp` — main driver and command parsing
- `zoo_mst.h` — MST implementation
- `zoo_fasttsp.h` — fast TSP heuristic
- `zoo_opttsp.h` — optimal TSP with branch-and-bound
- `animal_class.h` — point/region definitions
- `Makefile` — build rules

## Build

```bash
make
./zoo --mode MST < sample-c.txt
./zoo --mode FASTTSP < sample-c.txt
./zoo --mode OPTTSP < sample-e.txt
```

## Key concepts

- Minimum Spanning Tree (Prim's algorithm)
- Traveling Salesman Problem heuristics
- Branch-and-bound optimization
- MST lower-bound pruning
