# -------------------------------------------------
# Tests for Task D — Knapsack Vaccination
# Run with: python tests/task_d.py
#
# __project__ = 'Modelling a Disease Outbreak'
# __copyright__ = 'Copyright 2026, RMIT University'
# -------------------------------------------------

import sys
import os
import random
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulation.person import Person
from treatment.task_d import task_d
from treatment.vaccination_program import brute_force_vaccination

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


def check_close(actual: float, expected: float, pass_msg: str, fail_msg: str) -> None:
    diff = abs(actual - expected)
    if diff < TOLERANCE:
        ok(pass_msg)
    elif diff < 0.01:
        warn(f"{pass_msg} — close but not exact (got {actual:.6f}, expected {expected:.6f})")
    else:
        fail(f"{fail_msg} (got {actual:.6f}, expected {expected:.6f})")


def make_person(index: int, benefit: float, dosage: int) -> Person:
    p = Person(index, vulnerability=0.5, dosage_requirement=dosage)
    p.set_prob_of_infection(benefit)
    return p


# --------------------------------------------------
# Case 1: Return types
# --------------------------------------------------

print("\n--- Case 1: Return types ---")

p0 = make_person(0, 0.8, 3)
p1 = make_person(1, 0.6, 4)
vaccinated, benefit, doses, memo = task_d([p0, p1], 5)

check(isinstance(vaccinated, list),
      "task_d returns a list as first element",
      f"First return value should be list, got {type(vaccinated).__name__}")

check(isinstance(benefit, (int, float)),
      "task_d returns a number as second element (benefit)",
      f"Second return value should be numeric, got {type(benefit).__name__}")

check(isinstance(doses, int),
      "task_d returns an int as third element (doses)",
      f"Third return value should be int, got {type(doses).__name__}")

check(memo is not None,
      "task_d returns a memo table as fourth element (not None)",
      "Fourth return value should not be None — return your DP memo table")

if memo is not None:
    check(len(memo) == 3,
          "memo table has n+1=3 rows",
          f"memo table should have 3 rows, got {len(memo)}")
    check(len(memo[0]) == 6,
          "memo table has C+1=6 columns for capacity=5",
          f"memo table should have 6 columns, got {len(memo[0])}")


# --------------------------------------------------
# Case 2: Zero capacity — nobody can be vaccinated
# --------------------------------------------------

print("\n--- Case 2: Zero capacity ---")

p0 = make_person(0, 0.9, 2)
p1 = make_person(1, 0.7, 3)
vaccinated, benefit, doses, _ = task_d([p0, p1], 0)

check(len(vaccinated) == 0,
      "Case 2: no one vaccinated with zero capacity",
      f"Case 2: Expected 0 vaccinated, got {len(vaccinated)}")

check_close(benefit, 0.0,
            "Case 2: benefit is 0.0",
            "Case 2: benefit should be 0.0")

check(doses == 0,
      "Case 2: doses used is 0",
      f"Case 2: Expected 0 doses, got {doses}")


# --------------------------------------------------
# Case 3: One fits, one does not
# --------------------------------------------------

print("\n--- Case 3: One fits, one does not ---")

p0 = make_person(0, 0.8, 3)
p1 = make_person(1, 0.6, 10)
vaccinated, benefit, doses, _ = task_d([p0, p1], 5)

check(doses <= 5,
      "Case 3: doses do not exceed capacity",
      f"Case 3: doses ({doses}) exceed capacity (5) — CONSTRAINT VIOLATED")

check_close(benefit, 0.8,
            "Case 3: correct total benefit (0.8)",
            "Case 3: incorrect total benefit")

check(doses == 3,
      "Case 3: correct doses used (3)",
      f"Case 3: Expected 3 doses, got {doses}")


# --------------------------------------------------
# Case 4: All residents fit
# --------------------------------------------------

print("\n--- Case 4: All residents fit ---")

p0 = make_person(0, 0.9, 2)
p1 = make_person(1, 0.7, 3)
p2 = make_person(2, 0.5, 1)
vaccinated, benefit, doses, _ = task_d([p0, p1, p2], 10)

check(len(vaccinated) == 3,
      "Case 4: all 3 residents vaccinated",
      f"Case 4: Expected 3 vaccinated, got {len(vaccinated)}")

check_close(benefit, 2.1,
            "Case 4: correct total benefit (2.1)",
            "Case 4: incorrect total benefit")

check(doses == 6,
      "Case 4: correct doses used (6)",
      f"Case 4: Expected 6 doses, got {doses}")


# --------------------------------------------------
# Case 5: Correctness vs brute force reference
# --------------------------------------------------

print("\n--- Case 5: Correctness vs brute force ---")

random.seed(42)
persons = [make_person(i, round(random.uniform(0.1, 0.9), 4),
                       random.randint(1, 5)) for i in range(10)]
capacity = 15

_, bf_benefit, bf_doses, _ = brute_force_vaccination(persons, capacity)
vaccinated, stu_benefit, stu_doses, _ = task_d(persons, capacity)

check(stu_doses <= capacity,
      f"Case 5: doses ({stu_doses}) do not exceed capacity ({capacity})",
      f"Case 5: doses ({stu_doses}) exceed capacity ({capacity}) — CONSTRAINT VIOLATED")

check_close(stu_benefit, bf_benefit,
            f"Case 5: benefit matches reference ({bf_benefit:.4f})",
            f"Case 5: benefit {stu_benefit:.4f} does not match reference {bf_benefit:.4f}")

if stu_benefit >= bf_benefit - TOLERANCE and stu_doses > bf_doses:
    warn("Case 5: correct benefit achieved but more doses used than necessary — "
         "consider whether your solution always uses the minimum doses possible.")


# --------------------------------------------------
# Cases 5a-5c: Tiebreaker stress tests
# Each case has multiple selections achieving the same
# maximum benefit. The correct solution uses fewer doses.
# --------------------------------------------------

print("\n--- Cases 5a-5c: Tiebreaker stress tests ---")

# 5a: simple guaranteed tie
# P0 alone: benefit=0.5, doses=6
# P1+P2:    benefit=0.5, doses=3  <- minimum doses, should be selected
p0 = make_person(0, 0.5, 6)
p1 = make_person(1, 0.3, 2)
p2 = make_person(2, 0.2, 1)
_, stu_benefit_5a, stu_doses_5a, _ = task_d([p0, p1, p2], 6)
_, bf_benefit_5a, bf_doses_5a, _ = brute_force_vaccination([p0, p1, p2], 6)
check_close(stu_benefit_5a, bf_benefit_5a,
            f"Case 5a: correct benefit ({bf_benefit_5a:.4f})",
            f"Case 5a: incorrect benefit")
if stu_benefit_5a >= bf_benefit_5a - TOLERANCE and stu_doses_5a > bf_doses_5a:
    warn(f"Case 5a: correct benefit but used {stu_doses_5a} doses instead of minimum {bf_doses_5a}")

# 5b: three-way guaranteed tie
# P0 alone:  benefit=0.9, doses=9
# P1+P2:     benefit=0.9, doses=7
# P3+P4:     benefit=0.9, doses=4  <- minimum doses, should be selected
p0 = make_person(0, 0.9, 9)
p1 = make_person(1, 0.5, 4)
p2 = make_person(2, 0.4, 3)
p3 = make_person(3, 0.6, 2)
p4 = make_person(4, 0.3, 2)
_, stu_benefit_5b, stu_doses_5b, _ = task_d([p0, p1, p2, p3, p4], 9)
_, bf_benefit_5b, bf_doses_5b, _ = brute_force_vaccination([p0, p1, p2, p3, p4], 9)
check_close(stu_benefit_5b, bf_benefit_5b,
            f"Case 5b: correct benefit ({bf_benefit_5b:.4f})",
            f"Case 5b: incorrect benefit")
if stu_benefit_5b >= bf_benefit_5b - TOLERANCE and stu_doses_5b > bf_doses_5b:
    warn(f"Case 5b: correct benefit but used {stu_doses_5b} doses instead of minimum {bf_doses_5b}")

# 5c: chain of guaranteed ties across different capacities
# At each capacity, two selections tie on benefit — one uses fewer doses
tiebreak_warnings = 0
tie_cases = [
    # (persons, capacity, description)
    ([make_person(0, 0.4, 5), make_person(1, 0.25, 2), make_person(2, 0.15, 1)], 5,
     "0.4 in 5 doses vs 0.4 in 3 doses"),
    ([make_person(0, 0.7, 8), make_person(1, 0.4, 3), make_person(2, 0.3, 2)], 8,
     "0.7 in 8 doses vs 0.7 in 5 doses"),
    ([make_person(0, 1.0, 10), make_person(1, 0.6, 4), make_person(2, 0.4, 2)], 10,
     "1.0 in 10 doses vs 1.0 in 6 doses"),
]
for tc_persons, tc_capacity, tc_desc in tie_cases:
    _, tc_bf_benefit, tc_bf_doses, _ = brute_force_vaccination(tc_persons, tc_capacity)
    _, tc_stu_benefit, tc_stu_doses, _ = task_d(tc_persons, tc_capacity)
    if tc_stu_benefit >= tc_bf_benefit - TOLERANCE and tc_stu_doses > tc_bf_doses:
        tiebreak_warnings += 1

if tiebreak_warnings == 0:
    ok("Case 5c: tiebreaking correct across all guaranteed-tie cases")
else:
    warn(f"Case 5c: tiebreaking incorrect in {tiebreak_warnings}/3 guaranteed-tie cases")


# --------------------------------------------------
# Case 6: Sub-optimal implementation warning
# --------------------------------------------------

print("\n--- Case 6: Implementation efficiency ---")

random.seed(99)
perf_eligible = [make_person(i, round(random.uniform(0.1, 0.9), 4),
                             random.randint(1, 5)) for i in range(12)]
_, _, _, perf_memo = task_d(perf_eligible, 20)

if perf_memo is None:
    fail("Case 6: memo table is None — not yet implemented")
else:
    total_cells = (len(perf_eligible) + 1) * 21
    filled = sum(1 for row in perf_memo for cell in row if cell is not None)

    if filled == 0:
        fail("Case 6: memo table is entirely empty — not yet implemented")
    elif filled / total_cells >= 0.75:
        warn("Case 6: solution may be sub-optimal — consider a more efficient approach")
    else:
        ok("Case 6: solution appears efficient")


# --------------------------------------------------
# Summary
# --------------------------------------------------

print(f"\n{'='*45}")
print(f"  Results: {GREEN}{passed} passed{RESET}, {RED}{failed} failed{RESET}")
print(f"{'='*45}\n")
