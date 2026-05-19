# -------------------------------------------------
# DON'T CHANGE THIS FILE.
# Base class for graph vertices.
#
# __author__ = 'Edward Small'
# __project__ = 'Modelling a Disease Outbreak'
# __copyright__ = 'Copyright 2025, RMIT University'
# -------------------------------------------------


class Vertex:
    """
    A generic vertex in a graph.

    This is the base class for all vertices.
    """

    def __init__(self, index: int) -> None:
        """
        Initialises a Vertex with a unique integer index.

        @param index: The unique integer index of this vertex in the graph.
        @returns: None
        """
        self.index = index

    def __repr__(self) -> str:
        """
        Returns a string representation of the vertex.

        @returns: A string of the form 'V0', 'V1', etc.
        """
        return f"V{self.index}"

    def __hash__(self) -> int:
        """
        Returns a hash of the vertex based on its index.
        Allows vertices to be used as dictionary keys and in sets.

        @returns: Hash of the vertex index.
        """
        return hash(self.index)

    def __eq__(self, other: object) -> bool:
        """
        Checks equality between two vertices based on their index.

        @param other: The object to compare against.
        @returns: True if both vertices share the same index, False otherwise.
        """
        if not isinstance(other, Vertex):
            return NotImplemented
        return self.index == other.index
