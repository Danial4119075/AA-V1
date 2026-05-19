# -------------------------------------------------
# DON'T CHANGE THIS FILE.
# Monte Carlo simulation for estimating infection
# risk over a planning horizon of T days.
#
# __author__ = 'Edward Small'
# __project__ = 'Modelling a Disease Outbreak'
# __copyright__ = 'Copyright 2026, RMIT University'
# -------------------------------------------------

import random
from graph.graph import Graph
from graph.vertex import Vertex


def monte_carlo(graph: Graph,
                source: Vertex,
                T: int,
                simulations: int) -> list[list[float]]:
    """
    Estimates the infection risk for every resident at each day t in
    [0, T] using a Monte Carlo simulation approach.

    Returns the full risk table where table[t][i] is the estimated
    infection risk for vertex V_i at day t.

    This implementation is deliberately inefficient — for each time
    step t, it runs a completely fresh set of simulations from scratch
    rather than carrying forward infection state from t-1. This means
    the work is repeated T times unnecessarily, giving O(T * simulations
    * T * |E|) overall instead of O(simulations * T * |E|). It is
    provided as a naive baseline for students to compare against their
    dynamic programming solution in task_b.py.

    @param graph: The contact graph (works with any Graph implementation).
    @param source: The source vertex (patient zero).
    @param T: The planning horizon in days.
    @param simulations: The number of simulations to run per time step.
    @returns: A 2D list where table[t][i] is the estimated infection
              risk for vertex V_i at day t, for t in [0, T].
              table[0][source] = 1.0, all others at t=0 are 0.0.
    """
    n = graph.num_vertices()
    vertices = graph.get_vertices()

    # Initialise full table with zeros
    table = [[0.0] * n for _ in range(T + 1)]

    # Base case: t = 0
    table[0][source.index] = 1.0

    # For each time step, run simulations independently from scratch
    for t in range(1, T + 1):
        infected_count = [0] * n

        for _ in range(simulations):
            # Start fresh — only source is infected
            infected = [False] * n
            infected[source.index] = True

            # Simulate exactly t days from scratch (inefficient — repeats work)
            for _ in range(t):
                new_infected = infected[:]

                for vertex in vertices:
                    if infected[vertex.index]:
                        continue

                    for neighbour, weight in graph.get_neighbours(vertex):
                        if infected[neighbour.index]:
                            if random.random() < weight:
                                new_infected[vertex.index] = True
                                break

                infected = new_infected

            for i in range(n):
                if infected[i]:
                    infected_count[i] += 1

        # Convert counts to probabilities for this time step
        for i in range(n):
            table[t][i] = infected_count[i] / simulations

        # Enforce patient zero is always 1.0
        table[t][source.index] = 1.0

    return table
