# -------------------------------------------------
# Tests for Task B — Infection Risk DP
# Run with: python tests/task_b.py
#
# __project__ = 'Modelling a Disease Outbreak'
# __copyright__ = 'Copyright 2026, RMIT University'
# -------------------------------------------------

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from graph.adjacency_list import AdjacencyList
from graph.vertex import Vertex
from transmission.task_b import task_b

# --------------------------------------------------
# Console colours
# --------------------------------------------------
GREEN  = '\033[92m'
YELLOW = '\033[93m'
RED    = '\033[91m'
RESET  = '\033[0m'

passed = 0
failed = 0
TOLERANCE = 1e-6


def ok(msg: str) -> None:
    global passed
    passed += 1
    print(f"  {GREEN}[PASS]{RESET} {msg}")


def close(msg: str) -> None:
    print(f"  {YELLOW}[CLOSE]{RESET} {msg}")


def fail(msg: str) -> None:
    global failed
    failed += 1
    print(f"  {RED}[FAIL]{RESET} {msg}")


def check(condition: bool, pass_msg: str, fail_msg: str) -> None:
    if condition:
        ok(pass_msg)
    else:
        fail(fail_msg)


def check_close(actual: float, expected: float, pass_msg: str, fail_msg: str) -> None:
    diff = abs(actual - expected)
    if diff < TOLERANCE:
        ok(pass_msg)
    elif diff < 0.01:
        close(f"{pass_msg} — close but not exact (got {actual:.6f}, expected {expected:.6f})")
    else:
        fail(f"{fail_msg} (got {actual:.6f}, expected {expected:.6f})")


# --------------------------------------------------
# Case 1: Chain of 2 residents, T=1
#
#   V0 ---0.8--- V1
#
# V0 is patient zero.
# r[0][0] = 1.0, r[1][0] = 0.0
# r[1][1] = 1 - (1 - 0.0) * (1 - 1.0 * 0.8) = 1 - 1.0 * 0.2 = 0.8
# --------------------------------------------------

print("\n--- Case 1: Chain of 2, T=1 ---")

g1 = AdjacencyList()
v0, v1 = Vertex(0), Vertex(1)
g1.add_vertex(v0)
g1.add_vertex(v1)
g1.add_edge(v0, v1, 0.8)

table = task_b(g1, v0, 1)

check(isinstance(table, list),
      "task_b returns a list",
      f"task_b should return a list, got {type(table).__name__}")

check(len(table) == 2,
      "table has T+1=2 rows for T=1",
      f"Expected 2 rows, got {len(table)}")

check(all(isinstance(row, list) for row in table),
      "each row of the table is a list",
      "each row of the table should be a list")

check(all(len(row) == 2 for row in table),
      "each row has |V|=2 entries",
      f"Expected 2 entries per row, got {[len(r) for r in table]}")

check_close(table[0][0], 1.0,
            "r[0][0] = 1.0 (patient zero at t=0)",
            "r[0][0] should be 1.0")

check_close(table[0][1], 0.0,
            "r[1][0] = 0.0 (V1 healthy at t=0)",
            "r[1][0] should be 0.0")

check_close(table[1][0], 1.0,
            "r[0][1] = 1.0 (patient zero stays infected)",
            "r[0][1] should be 1.0")

check_close(table[1][1], 0.8,
            "r[1][1] = 0.8 (V1 risk at t=1)",
            "r[1][1] should be 0.8")


# --------------------------------------------------
# Case 2: Chain of 3 residents, T=2
#
#   V0 ---0.8--- V1 ---0.6--- V2
#
# V0 is patient zero.
# t=0: r = [1.0, 0.0, 0.0]
# t=1: r[1] = 1 - (1-0.0)*(1-1.0*0.8)*(1-0.0*0.6) = 0.8
#       r[2] = 1 - (1-0.0)*(1-0.0*0.6) = 0.0
# t=2: r[1] = 1 - (1-0.8)*(1-1.0*0.8)*(1-0.0*0.6) = 1-(0.2*0.2*1.0) = 0.96
#       r[2] = 1 - (1-0.0)*(1-0.8*0.6) = 1 - 1.0*0.52 = 0.48
# --------------------------------------------------

print("\n--- Case 2: Chain of 3, T=2 ---")

g2 = AdjacencyList()
va, vb, vc = Vertex(0), Vertex(1), Vertex(2)
g2.add_vertex(va)
g2.add_vertex(vb)
g2.add_vertex(vc)
g2.add_edge(va, vb, 0.8)
g2.add_edge(vb, vc, 0.6)

table2 = task_b(g2, va, 2)

check(len(table2) == 3,
      "table has T+1=3 rows for T=2",
      f"Expected 3 rows, got {len(table2)}")

check(all(len(row) == 3 for row in table2),
      "each row has |V|=3 entries",
      f"Expected 3 entries per row, got {[len(r) for r in table2]}")

check_close(table2[1][1], 0.8,
            "r[1][1] = 0.8",
            "r[1][1] should be 0.8")

check_close(table2[1][2], 0.0,
            "r[2][1] = 0.0 (V2 unreachable at t=1)",
            "r[2][1] should be 0.0")

check_close(table2[2][1], 0.96,
            "r[1][2] = 0.96",
            "r[1][2] should be 0.96")

check_close(table2[2][2], 0.48,
            "r[2][2] = 0.48",
            "r[2][2] should be 0.48")


# --------------------------------------------------
# Case 3: Isolated patient zero (no edges), T=3
#
# V0 is patient zero with no neighbours.
# All other residents stay at risk 0.0 for all t.
# --------------------------------------------------

print("\n--- Case 3: Isolated patient zero, T=3 ---")

g3 = AdjacencyList()
p0, p1, p2 = Vertex(0), Vertex(1), Vertex(2)
g3.add_vertex(p0)
g3.add_vertex(p1)
g3.add_vertex(p2)
# No edges added

table3 = task_b(g3, p0, 3)

check(len(table3) == 4,
      "table has T+1=4 rows for T=3",
      f"Expected 4 rows, got {len(table3)}")

check(all(len(row) == 3 for row in table3),
      "each row has |V|=3 entries",
      f"Expected 3 entries per row")

for t in range(4):
    check_close(table3[t][0], 1.0,
                f"r[0][{t}] = 1.0 (patient zero always infected)",
                f"r[0][{t}] should be 1.0")

for t in range(4):
    for i in [1, 2]:
        check_close(table3[t][i], 0.0,
                    f"r[{i}][{t}] = 0.0 (isolated, no path from patient zero)",
                    f"r[{i}][{t}] should be 0.0")


# --------------------------------------------------
# Summary
# --------------------------------------------------

print(f"\n{'='*45}")
print(f"  Results: {GREEN}{passed} passed{RESET}, {RED}{failed} failed{RESET}")
print(f"{'='*45}\n")
