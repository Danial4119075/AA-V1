# -------------------------------------------------
# DON'T CHANGE THIS FILE.
# Adjacency list implementation of the Graph ABC.
#
# __author__ = 'Edward Small'
# __project__ = 'Modelling a Disease Outbreak'
# __copyright__ = 'Copyright 2026, RMIT University'
# -------------------------------------------------

from graph.graph import Graph
from graph.vertex import Vertex
from graph.edge import Edge


class LinkedListNode:
    """
    A single node in the linked list used by the AdjacencyList representation.

    Each node stores a neighbouring vertex, the weight of the edge connecting
    it to the source vertex, and a pointer to the next node in the list.
    Together, the chain of nodes for a given vertex forms its adjacency list.
    """

    def __init__(self, neighbour: Vertex, weight: float, next_node: 'LinkedListNode | None' = None) -> None:
        """
        Initialises a LinkedListNode for use in an adjacency list.

        @param neighbour: The neighbouring vertex this node points to.
        @param weight: The weight of the edge connecting the source vertex
                       to this neighbour.
        @param next_node: The next node in the linked list, or None if this
                          is the last node.
        @returns: None
        """
        self.neighbour = neighbour
        self.weight = weight
        self.next = next_node

    def __repr__(self) -> str:
        """
        Returns a string representation of this linked list node, showing
        the neighbour and weight, followed by the remainder of the chain.

        @returns: A string of the form '(V1, 0.9) -> (V2, 0.4) -> None'.
        """
        return f"({self.neighbour}, {self.weight}) -> {self.next!r}"


class AdjacencyList(Graph):
    """
    An adjacency list representation of a weighted undirected graph.

    Each vertex is associated with a linked list of LinkedListNodes,
    where each node stores a neighbouring vertex and the weight of the
    connecting edge. Only actual edges are stored, giving O(|V| + |E|)
    space complexity compared to O(|V|^2) for a matrix.

    Getting the neighbours of a vertex requires traversing its linked
    list, which takes O(deg(u)) time — proportional only to the number
    of actual neighbours, not the total number of vertices.
    """

    def __init__(self) -> None:
        """
        Initialises an empty adjacency list graph.

        Internally maintains a list of LinkedListNode heads (one per vertex)
        and a separate list of Vertex objects for iteration.

        @returns: None
        """
        self._heads: list[LinkedListNode | None] = []
        self._vertices: list[Vertex] = []
        self._num_edges: int = 0

    def add_vertex(self, vertex: Vertex) -> None:
        """
        Adds a vertex to the graph and initialises its adjacency linked list
        with an empty head (None).

        @param vertex: The vertex to add.
        @returns: None
        """
        self._vertices.append(vertex)
        self._heads.append(None)

    def add_edge(self, u: Vertex, v: Vertex, weight: float) -> bool:
        """
        Adds an undirected edge to the graph by inserting a LinkedListNode
        at the head of the adjacency list for both endpoint vertices.

        Inserting at the head of the list is O(1).
        Since the graph is undirected, both directions are recorded:
        u -> v and v -> u, using the same edge weight.

        @param u: The first vertex.
        @param v: The second vertex.
        @param weight: The weight of the edge (e.g. transmission probability).
        @returns: True if the edge was added successfully, False otherwise.
        """
        if u.index >= len(self._heads) or v.index >= len(self._heads):
            return False

        # Insert v into u's adjacency list
        self._heads[u.index] = LinkedListNode(v, weight, self._heads[u.index])

        # Insert u into v's adjacency list
        self._heads[v.index] = LinkedListNode(u, weight, self._heads[v.index])

        self._num_edges += 1
        return True

    def get_vertices(self) -> list[Vertex]:
        """
        Returns a list of all vertices in the graph.

        @returns: A list of all Vertex objects in the graph.
        """
        return self._vertices

    def get_edges(self) -> list[Edge]:
        """
        Returns a list of all edges in the graph.
        Each undirected edge appears only once, collected by iterating
        over each vertex's linked list and recording only edges where
        the source index is less than the neighbour index.

        @returns: A list of all Edge objects in the graph.
        """
        edges = []
        for vertex in self._vertices:
            node = self._heads[vertex.index]
            while node is not None:
                if vertex.index < node.neighbour.index:
                    edges.append(Edge(vertex, node.neighbour, node.weight))
                node = node.next
        return edges

    def get_neighbours(self, vertex: Vertex) -> list[tuple[Vertex, float]]:
        """
        Returns all neighbours of a given vertex by traversing its adjacency
        linked list from head to tail.

        This operation takes O(deg(u)) time — proportional only to the number
        of actual neighbours of the vertex, not the total number of vertices.

        @param vertex: The vertex whose neighbours are to be returned.
        @returns: A list of (neighbour, weight) tuples, one per neighbouring vertex.
        """
        neighbours = []
        node = self._heads[vertex.index]
        while node is not None:
            neighbours.append((node.neighbour, node.weight))
            node = node.next
        return neighbours

    def has_edge(self, u: Vertex, v: Vertex) -> bool:
        """
        Checks whether an edge exists between two vertices by traversing
        u's adjacency linked list and looking for v.

        @param u: The first vertex.
        @param v: The second vertex.
        @returns: True if an edge exists between u and v, False otherwise.
        """
        node = self._heads[u.index]
        while node is not None:
            if node.neighbour.index == v.index:
                return True
            node = node.next
        return False

    def get_edge_weight(self, u: Vertex, v: Vertex) -> float:
        """
        Returns the weight of the edge between two vertices by traversing
        u's adjacency linked list and looking for v.

        @param u: The first vertex.
        @param v: The second vertex.
        @returns: The edge weight as a float, or 0.0 if no edge exists.
        """
        node = self._heads[u.index]
        while node is not None:
            if node.neighbour.index == v.index:
                return node.weight
            node = node.next
        return 0.0

    def num_vertices(self) -> int:
        """
        Returns the number of vertices in the graph.

        @returns: The number of vertices as an integer.
        """
        return len(self._vertices)

    def num_edges(self) -> int:
        """
        Returns the number of edges in the graph.
        Each undirected edge is counted once.

        @returns: The number of edges as an integer.
        """
        return self._num_edges

    def __repr__(self) -> str:
        """
        Returns a string representation of the adjacency list,
        showing each vertex and its chain of neighbours.

        @returns: A multi-line string with one row per vertex.
        """
        lines = []
        for vertex in self._vertices:
            lines.append(f"{vertex}: {self._heads[vertex.index]!r}")
        return "\n".join(lines)
