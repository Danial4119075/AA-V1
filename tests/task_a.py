# -------------------------------------------------
# Tests for Task A — Adjacency Matrix
# Run with: python tests/task_a.py
#
# __project__ = 'Modelling a Disease Outbreak'
# __copyright__ = 'Copyright 2026, RMIT University'
# -------------------------------------------------

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from graph.adjacency_matrix import AdjacencyMatrix
from graph.vertex import Vertex

# --------------------------------------------------
# Console colours
# --------------------------------------------------
GREEN  = '\033[92m'
YELLOW = '\033[93m'
RED    = '\033[91m'
RESET  = '\033[0m'

passed = 0
failed = 0


def ok(msg: str) -> None:
    global passed
    passed += 1
    print(f"  {GREEN}[PASS]{RESET} {msg}")


def warn(msg: str) -> None:
    print(f"  {YELLOW}[WARN]{RESET} {msg}")


def fail(msg: str) -> None:
    global failed
    failed += 1
    print(f"  {RED}[FAIL]{RESET} {msg}")


def check(condition: bool, pass_msg: str, fail_msg: str) -> None:
    if condition:
        ok(pass_msg)
    else:
        fail(fail_msg)


# --------------------------------------------------
# Build a simple test graph
#
#   V0 ---0.9--- V1
#   |              |
#  0.4            0.6
#   |              |
#   V2 ---0.7--- V3
#
# --------------------------------------------------

def build_graph() -> tuple[AdjacencyMatrix, list[Vertex]]:
    g = AdjacencyMatrix()
    verts = [Vertex(i) for i in range(4)]
    for v in verts:
        g.add_vertex(v)
    return g, verts


# --------------------------------------------------
# Test: add_edge
# --------------------------------------------------

print("\n--- add_edge ---")

g, verts = build_graph()

result = g.add_edge(verts[0], verts[1], 0.9)
check(isinstance(result, bool),
      "add_edge returns a bool",
      f"add_edge should return bool, got {type(result).__name__}")

check(result is True,
      "add_edge returns True on success",
      "add_edge should return True when edge is successfully added")

check((g.num_edges() == 1) is True,
      "add_edge correctly increments self.num_edges for one edge",
      "add_edge does not also increment the edge count num_edges")

g.add_edge(verts[0], verts[2], 0.4)
g.add_edge(verts[1], verts[3], 0.6)
g.add_edge(verts[2], verts[3], 0.7)

# Check both directions stored
check(g._matrix[0][1] == 0.9 and g._matrix[1][0] == 0.9,
      "add_edge stores weight symmetrically (u->v and v->u)",
      f"Expected matrix[0][1]=0.9 and matrix[1][0]=0.9, got {g._matrix[0][1]} and {g._matrix[1][0]}")

check(g._matrix[0][2] == 0.4 and g._matrix[2][0] == 0.4,
      "add_edge stores second edge symmetrically",
      f"Expected matrix[0][2]=0.4 and matrix[2][0]=0.4, got {g._matrix[0][2]} and {g._matrix[2][0]}")

result_invalid = g.add_edge(Vertex(99), verts[0], 0.5)
check(result_invalid is False,
      "add_edge returns False for invalid vertex index",
      "add_edge should return False when vertex index is out of range")

check((g.num_edges() == 4) is True,
      "add_edge correctly increments self.num_edges for multiple edges",
      "add_edge does not also increment the edge count num_edges")

check((g.num_edges()  > 4) is False,
      "add_edge does not increment num_edges when an edge is failed to be added",
      "add_edge incorrectly increments num_edges when an edge fails to be added")


# --------------------------------------------------
# Test: get_edges
# --------------------------------------------------

print("\n--- get_edges ---")

g, verts = build_graph()
g.add_edge(verts[0], verts[1], 0.9)
g.add_edge(verts[0], verts[2], 0.4)
g.add_edge(verts[1], verts[3], 0.6)
g.add_edge(verts[2], verts[3], 0.7)

edges = g.get_edges()

check(isinstance(edges, list),
      "get_edges returns a list",
      f"get_edges should return a list, got {type(edges).__name__}")

check(len(edges) == 4,
      f"get_edges returns correct number of edges (4)",
      f"Expected 4 edges, got {len(edges)}")

weights = sorted([e.weight for e in edges])
check(weights == sorted([0.9, 0.4, 0.6, 0.7]),
      "get_edges returns correct edge weights",
      f"Expected weights [0.4, 0.6, 0.7, 0.9], got {weights}")

# Check no duplicates — each edge should appear once
endpoints = [tuple(sorted([e.u.index, e.v.index])) for e in edges]
check(len(endpoints) == len(set(endpoints)),
      "get_edges returns no duplicate edges",
      f"get_edges returned duplicate edges: {endpoints}")

empty_g = AdjacencyMatrix()
empty_g.add_vertex(Vertex(0))
check(empty_g.get_edges() == [],
      "get_edges returns empty list for graph with no edges",
      "get_edges should return [] for a graph with no edges")


# --------------------------------------------------
# Test: get_neighbours
# --------------------------------------------------

print("\n--- get_neighbours ---")

g, verts = build_graph()
g.add_edge(verts[0], verts[1], 0.9)
g.add_edge(verts[0], verts[2], 0.4)
g.add_edge(verts[1], verts[3], 0.6)
g.add_edge(verts[2], verts[3], 0.7)

neighbours_0 = g.get_neighbours(verts[0])

check(isinstance(neighbours_0, list),
      "get_neighbours returns a list",
      f"get_neighbours should return a list, got {type(neighbours_0).__name__}")

check(len(neighbours_0) == 2,
      "get_neighbours returns correct number of neighbours for V0 (2)",
      f"Expected 2 neighbours for V0, got {len(neighbours_0)}")

check(all(isinstance(n, tuple) and len(n) == 2 for n in neighbours_0),
      "get_neighbours returns list of (Vertex, float) tuples",
      "get_neighbours should return list of (Vertex, float) tuples")

neighbour_indices = sorted([n[0].index for n in neighbours_0])
check(neighbour_indices == [1, 2],
      "get_neighbours returns correct neighbour indices for V0 ([1, 2])",
      f"Expected neighbour indices [1, 2] for V0, got {neighbour_indices}")

neighbour_weights = sorted([n[1] for n in neighbours_0])
check(sorted([round(w, 2) for w in neighbour_weights]) == [0.4, 0.9],
      "get_neighbours returns correct weights for V0 ([0.4, 0.9])",
      f"Expected weights [0.4, 0.9] for V0, got {neighbour_weights}")

isolated = AdjacencyMatrix()
isolated.add_vertex(Vertex(0))
check(isolated.get_neighbours(Vertex(0)) == [],
      "get_neighbours returns [] for isolated vertex",
      "get_neighbours should return [] for a vertex with no neighbours")


# --------------------------------------------------
# Test: get_edge_weight
# --------------------------------------------------

print("\n--- get_edge_weight ---")

g, verts = build_graph()
g.add_edge(verts[0], verts[1], 0.9)
g.add_edge(verts[0], verts[2], 0.4)
g.add_edge(verts[1], verts[3], 0.6)
g.add_edge(verts[2], verts[3], 0.7)

check(isinstance(g.get_edge_weight(verts[0], verts[1]), float),
      "get_edge_weight returns a float",
      f"get_edge_weight should return float, got {type(g.get_edge_weight(verts[0], verts[1])).__name__}")

check(round(g.get_edge_weight(verts[0], verts[1]), 2) == 0.9,
      "get_edge_weight returns correct weight for V0-V1 (0.9)",
      f"Expected 0.9 for V0-V1, got {g.get_edge_weight(verts[0], verts[1])}")

check(round(g.get_edge_weight(verts[1], verts[0]), 2) == 0.9,
      "get_edge_weight is symmetric — V1-V0 same as V0-V1",
      f"Expected 0.9 for V1-V0, got {g.get_edge_weight(verts[1], verts[0])}")

check(g.get_edge_weight(verts[0], verts[3]) == 0.0,
      "get_edge_weight returns 0.0 for non-existent edge",
      f"Expected 0.0 for non-existent edge V0-V3, got {g.get_edge_weight(verts[0], verts[3])}")

check(g.get_edge_weight(Vertex(99), verts[0]) == 0.0,
      "get_edge_weight returns 0.0 for invalid vertex index",
      "get_edge_weight should return 0.0 for out-of-range vertex index")


# --------------------------------------------------
# Summary
# --------------------------------------------------

print(f"\n{'='*45}")
print(f"  Results: {GREEN}{passed} passed{RESET}, {RED}{failed} failed{RESET}")
print(f"{'='*45}\n")
