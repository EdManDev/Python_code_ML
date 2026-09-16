# Path Planning Lab — Dijkstra, A* and Autonomous Robot Navigation

Interactive Jupyter notebooks that teach pathfinding the way robots actually
use it: from a small 4×4 weighted graph to a scalable navigation laboratory
with obstacles, cost maps, dynamic environments, incremental replanning and
continuous-space planning.

The central idea running through everything:

```text
Dijkstra:   f(n) = g(n)            "cheapest so far"
Greedy:     f(n) = h(n)            "looks closest"
A*:         f(n) = g(n) + h(n)     "cheapest overall estimate"
```

Source / original inspiration: [instagram.com/p/DagKd4iyni-](https://www.instagram.com/p/DagKd4iyni-/)

## Repository contents

| File | What it is |
|---|---|
| `robot_navigation_lab.ipynb` | **The main lab.** 32 sections, 10 hand-implemented grid algorithms, RRT/RRT*/PRM demos, interactive explorer, robot simulation with D* Lite replanning, benchmarks and a 168-check validation suite. |
| `astar_grid_visualizer.ipynb.txt` | The earlier standalone A* vs Dijkstra visualizer for the 4×4 graph (rename to `.ipynb` to open it in Jupyter). Its content also lives on as Section 2 of the lab. |
| `img1.png` | The original 4×4 weighted-graph diagram both notebooks build from. |
| `.venv/` | Local Python environment used for development/testing (can be deleted). |

## Quickstart

```bash
# any Python 3.10+ environment
pip install numpy pandas matplotlib ipywidgets networkx

jupyter lab robot_navigation_lab.ipynb   # or: jupyter notebook
```

The notebook's first cell runs `%pip install` for anything missing, so
opening it and running top-to-bottom in a fresh kernel also works.

## The learning progression

```text
GRID NAVIGATION → WEIGHTED PATH PLANNING → HEURISTIC SEARCH
→ OBSTACLE NAVIGATION → LARGE MAPS → DYNAMIC ENVIRONMENTS
→ REPLANNING → CONTINUOUS-SPACE MOTION PLANNING → LOCAL PLANNING
```

## Algorithms (all implemented by hand)

| Algorithm | Formula / idea | Where |
|---|---|---|
| BFS | FIFO queue, fewest edges | §5 |
| DFS | LIFO stack, deep traversal | §6 |
| Dijkstra | `f = g` | §7 |
| Greedy Best-First | `f = h` | §8 |
| A* | `f = g + h`, 4 heuristics | §9–10 |
| Bidirectional Dijkstra / A* | two searches meet in the middle | §11–12 |
| Jump Point Search | uniform-grid A* with jump points | §13 |
| Theta* | any-angle paths via line of sight | §14 |
| D* Lite | incremental replanning after world changes | §19 |
| RRT / RRT* / PRM | continuous-space motion planning demos | §22–24 |
| DWA / MPC | local planning (conceptual + sketch) | §25 |

NetworkX is never used for the teaching algorithms — it appears only in the
validation suite as an independent judge of the hand-written results.

## Interactive features

- **Algorithm Explorer (§15)** — choose map preset, size, seed, density,
  start/goal, algorithm, heuristic and 4/8-connected movement; then
  Step / Run / Play–Pause through the search, add or remove obstacles,
  replan, or run a one-click comparison table.
- **Robot Simulation (§20)** — a robot with separate *known* and *true*
  maps, a short-range sensor, obstacle drops mid-route, and a side-by-side
  choice of replanning with fresh A* or a D* Lite repair (expansion counts
  for both).
- Consistent visualization everywhere: START, GOAL, ROBOT, OPEN, CLOSED,
  CURRENT, PATH states drawn by a single routine that consumes one shared
  search-state model.

## Validation

Every execution runs a regression suite: paths are mechanically validated
(neighbors, passable cells, cost arithmetic), A* with an admissible
heuristic must match Dijkstra's optimal cost on every map, `h = 0` must
reproduce Dijkstra exactly, sealed-off goals must report `no path` without
crashing, D* Lite repairs and JPS results must equal fresh A* runs, and
smaller maps are cross-checked against `networkx.dijkstra_path_length`.

## Key teaching points

- Edge weights are **costs**, not geographic distances — grid geometry ≠
  traversal cost.
- A heuristic is only safe if it never overestimates (**admissible**);
  the lab builds a cost-aware admissible heuristic from the map's own cost
  structure and shows inadmissible heuristics returning suboptimal paths.
- No algorithm is "best": expansion counts are **measured**, not asserted,
  and depend on map structure, obstacle layout and heuristic quality.

## Limitations

JPS and Theta* assume uniform-cost grids; the RRT* demo uses simplified
rewiring; Theta* assumes free space between cells; bidirectional and D* Lite
savings are map-dependent; 500×500 grids work but are omitted from
benchmarks to keep runtimes short.
