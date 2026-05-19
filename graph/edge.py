# -------------------------------------------------
# DON'T CHANGE THIS FILE.
# Base class for graph edges.
#
# __author__ = 'Edward Small'
# __project__ = 'Modelling a Disease Outbreak'
# __copyright__ = 'Copyright 2025, RMIT University'
# -------------------------------------------------

from graph.vertex import Vertex


class Edge:
    """
    A generic weighted edge in an undirected graph.

    This is the base class for all edges.
    """

    def __init__(self, u: Vertex, v: Vertex, weight: float) -> None:
        """
        Initialises an Edge between two vertices with a given weight.

        @param u: The first vertex of the edge.
        @param v: The second vertex of the edge.
        @param weight: The weight of the edge.
        @returns: None
        """
        self.u = u
        self.v = v
        self.weight = weight

    def __repr__(self) -> str:
        """
        Returns a string representation of the edge.

        @returns: A string of the form 'V0 -- 0.9 -- V1'.
        """
        return f"{self.u} -- {self.weight} -- {self.v}"

    def __hash__(self) -> int:
        """
        Returns a hash of the edge based on its two vertices.
        Since the graph is undirected, the hash is symmetric —
        Edge(u, v) and Edge(v, u) produce the same hash.

        @returns: Hash of the frozenset of the two vertex indices.
        """
        return hash(frozenset({self.u.index, self.v.index}))

    def __eq__(self, other: object) -> bool:
        """
        Checks equality between two edges based on their vertices.
        Since the graph is undirected, Edge(u, v) == Edge(v, u).

        @param other: The object to compare against.
        @returns: True if both edges connect the same pair of vertices, False otherwise.
        """
        if not isinstance(other, Edge):
            return NotImplemented
        return frozenset({self.u.index, self.v.index}) == frozenset({other.u.index, other.v.index})
