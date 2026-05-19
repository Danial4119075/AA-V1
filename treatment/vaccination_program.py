# -------------------------------------------------
# DON'T CHANGE THIS FILE.
# Brute-force solution for the antiviral
# allocation program.
#
# __author__ = 'Edward Small'
# __project__ = 'Modelling a Disease Outbreak'
# __copyright__ = 'Copyright 2026, RMIT University'
# -------------------------------------------------
from typing import Tuple, List

from simulation.person import Person


def brute_force_vaccination(eligible: list[Person],
                            total_doses: int) -> tuple[list[Person], float, int, None]:
    """
    Allocates antiviral doses to residents using a brute-force exhaustive
    search over all 2^n subsets of eligible residents.

    The subset with the highest total benefit (prob_of_infection) that
    fits within the total dose capacity is selected.

    Tiebreaking: among all subsets achieving the maximum benefit,
    the one using the minimum number of doses is chosen.

    WARNING: This approach has exponential time complexity O(2^n) and
    is only feasible for very small numbers of residents. It is provided
    as a naive baseline for comparison with the dynamic programming
    solution in task_d.py.

    Time complexity: O(2^n) where n is the number of eligible residents.

    @param eligible: A list of Person objects eligible for vaccination,
                     sorted by benefit descending. Each Person has
                     dosage_requirement (cost) and benefit attributes.
    @param total_doses: The total number of antiviral doses available.
    @returns: A tuple of:
              - list[Person]: all vaccinated persons.
              - float: total benefit achieved.
              - int: total doses used.
    """
    n = len(eligible)
    best_benefit: float = 0.0
    best_doses: int = 0
    best_subset: list[Person] = []

    # Enumerate all 2^n subsets
    for mask in range(1 << n):
        subset: list[Person] = []
        subset_benefit: float = 0.0
        subset_doses: int = 0

        for i in range(n):
            if mask & (1 << i):
                person = eligible[i]
                subset.append(person)
                subset_benefit += person.benefit
                subset_doses += person.dosage_requirement

        # Skip subsets that exceed capacity
        if subset_doses > total_doses:
            continue

        # Update best if this subset is better
        if subset_benefit > best_benefit:
            best_benefit = subset_benefit
            best_doses = subset_doses
            best_subset = subset

        # Tiebreak: same benefit but fewer doses
        elif subset_benefit == best_benefit and subset_doses < best_doses:
            best_doses = subset_doses
            best_subset = subset

    return best_subset, best_benefit, best_doses, None
