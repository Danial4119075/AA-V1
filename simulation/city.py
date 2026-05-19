# -------------------------------------------------
# DON'T CHANGE THIS FILE.
# City class for the disease simulation.
#
# __author__ = 'Edward Small'
# __project__ = 'Modelling a Disease Outbreak'
# __copyright__ = 'Copyright 2026, RMIT University'
# -------------------------------------------------

import random
from graph.graph import Graph
from graph.adjacency_list import AdjacencyList
from graph.adjacency_matrix import AdjacencyMatrix
from simulation.person import Person


class City:
    """
    Represents the city of Metropolis as a weighted contact graph.

    Responsible for building the graph from simulation parameters,
    creating Person objects with randomly generated attributes,
    and assigning patient zero. Does not run any algorithms — that
    is handled externally by the solver and vaccine program.
    """

    def __init__(self,
                 seed: int,
                 num_residents: int,
                 num_edges: int,
                 max_transmission_prob: float,
                 vulnerability_range: tuple[float, float],
                 dosage_range: tuple[int, int],
                 graph_type: str) -> None:
        """
        Initialises the City and builds the contact graph.

        @param seed: Random seed for reproducibility.
        @param num_residents: Number of residents (vertices) in the graph.
        @param num_edges: Exact number of edges to generate. Must be positive
                          and at most num_residents * (num_residents - 1) / 2.
        @param max_transmission_prob: Maximum edge weight (transmission probability).
                                      Edge weights are drawn uniformly from
                                      (0.0002, max_transmission_prob].
        @param vulnerability_range: A (min, max) tuple controlling the range of
                                    vulnerability values assigned to residents.
        @param dosage_range: A (min, max) tuple controlling the range of dosage
                             requirements assigned to residents.
        @param graph_type: The graph representation to use. Either 'list' for
                           an adjacency list or 'matrix' for an adjacency matrix.
        @returns: None
        """
        self._seed = seed
        self._num_residents = num_residents
        self._num_edges = num_edges
        self._max_transmission_prob = max_transmission_prob
        self._vulnerability_range = vulnerability_range
        self._dosage_range = dosage_range
        self._graph_type = graph_type

        self._graph: Graph = None
        self._persons: list[Person] = []
        self._patient_zero: Person = None

        random.seed(self._seed)
        self._build_graph()

    def _build_graph(self) -> None:
        """
        Constructs the contact graph by creating Person objects and
        generating exactly floor(edge_density * num_possible_edges) edges,
        chosen randomly from all possible pairs.

        Edge weights represent daily transmission probabilities, drawn
        uniformly from (0, 1]. Patient zero is assigned randomly.

        @returns: None
        """
        # Initialise the correct graph representation
        if self._graph_type == 'list':
            self._graph = AdjacencyList()
        else:
            self._graph = AdjacencyMatrix()

        # Use separate random instances for reproducible, independent streams
        person_rng = random.Random(self._seed)
        edge_rng = random.Random(self._seed + 1)

        # Create Person objects and add them to the graph
        for i in range(self._num_residents):
            vulnerability = person_rng.uniform(*self._vulnerability_range)
            dosage_requirement = person_rng.randint(*self._dosage_range)
            person = Person(i, vulnerability, dosage_requirement)
            self._persons.append(person)
            self._graph.add_vertex(person)

        # Guarantee exactly num_edges edges, chosen randomly from all possible pairs
        all_pairs = [(i, j) for i in range(self._num_residents)
                     for j in range(i + 1, self._num_residents)]
        selected_pairs = edge_rng.sample(all_pairs, self._num_edges)

        for i, j in selected_pairs:
            weight = edge_rng.uniform(0.0002, self._max_transmission_prob)
            self._graph.add_edge(self._persons[i], self._persons[j], weight)

        # Assign patient zero using person_rng for consistency
        self._patient_zero = person_rng.choice(self._persons)
        self._patient_zero.set_state(True)

    def get_graph(self) -> Graph:
        """
        Returns the contact graph for this city.

        @returns: The Graph object representing the contact network.
        """
        return self._graph

    def get_persons(self) -> list[Person]:
        """
        Returns all residents of the city.

        @returns: A list of all Person objects in the simulation.
        """
        return self._persons

    def get_patient_zero(self) -> Person:
        """
        Returns the patient zero for this simulation.

        @returns: The Person object representing patient zero.
        """
        return self._patient_zero

    def get_eligible_residents(self) -> list[Person]:
        """
        Returns all residents eligible for vaccination — everyone
        except patient zero, sorted by benefit (prob_of_infection)
        descending.

        @returns: A list of Person objects sorted by benefit descending.
        """
        eligible = [p for p in self._persons if p.index != self._patient_zero.index]
        eligible.sort(key=lambda p: p.benefit, reverse=True)
        return eligible
