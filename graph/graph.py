# -------------------------------------------------
# DON'T CHANGE THIS FILE.
# Abstract base class for graph implementations.
#
# __author__ = 'Edward Small'
# __project__ = 'Modelling a Disease Outbreak'
# __copyright__ = 'Copyright 2026, RMIT University'
# -------------------------------------------------

from abc import ABC, abstractmethod
from graph.vertex import Vertex
from graph.edge import Edge


class Graph(ABC):
    """
    Abstract base class for all graph representations.

    Defines the interface that all graph implementations must follow.
    Algorithms should program against this interface only, so that they
    work correctly with any concrete representation (e.g. adjacency matrix
    or adjacency list) without modification.
    """

    @abstractmethod
    def add_vertex(self, vertex: Vertex) -> None:
        """
        Adds a vertex to the graph.

        @param vertex: The vertex to add.
        @returns: None
        """
        pass

    @abstractmethod
    def add_edge(self, u: Vertex, v: Vertex, weight: float) -> bool:
        """
        Adds an undirected edge to the graph between vertices u and v.
        Since the graph is undirected, both directions must be recorded
        by the concrete implementation.

        @param u: The first vertex.
        @param v: The second vertex.
        @param weight: The weight of the edge (e.g. transmission probability).
        @returns: True if the edge was added successfully, False otherwise.
        """
        pass

    @abstractmethod
    def get_vertices(self) -> list[Vertex]:
        """
        Returns a list of all vertices in the graph.

        @returns: A list of all Vertex objects in the graph.
        """
        pass

    @abstractmethod
    def get_edges(self) -> list[Edge]:
        """
        Returns a list of all edges in the graph.
        Each undirected edge should appear only once.

        @returns: A list of all Edge objects in the graph.
        """
        pass

    @abstractmethod
    def get_neighbours(self, vertex: Vertex) -> list[tuple[Vertex, float]]:
        """
        Returns all neighbours of a given vertex, along with the
        weight of the connecting edge.

        @param vertex: The vertex whose neighbours are to be returned.
        @returns: A list of (neighbour, weight) tuples.
        """
        pass

    @abstractmethod
    def has_edge(self, u: Vertex, v: Vertex) -> bool:
        """
        Checks whether an edge exists between two vertices.

        @param u: The first vertex.
        @param v: The second vertex.
        @returns: True if an edge exists between u and v, False otherwise.
        """
        pass

    @abstractmethod
    def get_edge_weight(self, u: Vertex, v: Vertex) -> float:
        """
        Returns the weight of the edge between two vertices.

        @param u: The first vertex.
        @param v: The second vertex.
        @returns: The edge weight as a float, or 0.0 if no edge exists.
        """
        pass

    @abstractmethod
    def num_vertices(self) -> int:
        """
        Returns the number of vertices in the graph.

        @returns: The number of vertices as an integer.
        """
        pass

    @abstractmethod
    def num_edges(self) -> int:
        """
        Returns the number of edges in the graph.
        Each undirected edge is counted once.

        @returns: The number of edges as an integer.
        """
        pass
