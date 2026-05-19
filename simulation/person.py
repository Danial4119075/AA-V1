# -------------------------------------------------
# DON'T CHANGE THIS FILE.
# Person class for the disease simulation.
#
# __author__ = 'Edward Small'
# __project__ = 'Modelling a Disease Outbreak'
# __copyright__ = 'Copyright 2026, RMIT University'
# -------------------------------------------------

from graph.vertex import Vertex


class Person(Vertex):
    """
    Represents a resident of Metropolis in the disease simulation.

    Extends the generic Vertex class with disease-specific attributes.
    Each person has an infection state, a vulnerability score, and a
    dosage requirement for antiviral treatment. The benefit score is
    set directly from the infection risk computed by the risk solver.
    """

    def __init__(self, index: int, vulnerability: float, dosage_requirement: int, state: bool = False) -> None:
        """
        Initialises a Person with disease-specific attributes.

        @param index: The unique integer index of this person in the graph.
        @param vulnerability: A positive float representing how susceptible
                               this person is to the virus. Range is controlled
                               by the simulation config.
        @param dosage_requirement: A positive integer representing the number
                                   of antiviral doses required to treat this
                                   person. Range is controlled by the simulation
                                   config.
        @param state: Infection state. False if healthy, True if infected.
                      Defaults to False (healthy).
        @returns: None
        """
        super().__init__(index)

        if vulnerability <= 0:
            raise ValueError(f"vulnerability must be positive, got {vulnerability}")
        if dosage_requirement <= 0:
            raise ValueError(f"dosage_requirement must be positive, got {dosage_requirement}")

        self.state: bool = state
        self.vulnerability: float = vulnerability
        self.dosage_requirement: int = dosage_requirement

        # Computed after risk solver runs
        self.prob_of_infection: float = 0.0
        self.benefit: float = 0.0

    def set_state(self, state: bool) -> None:
        """
        Updates the infection state of this person.

        @param state: False if healthy, True if infected.
        @returns: None
        """
        self.state = state

    def set_prob_of_infection(self, prob: float) -> None:
        """
        Updates the probability of infection for this person and sets
        the benefit score directly from this value.

        Must be a value in [0.0, 1.0].

        @param prob: The infection risk r_{i,T} computed by the risk solver.
        @returns: None
        """
        if not (0.0 <= prob <= 1.0):
            raise ValueError(f"prob_of_infection must be in [0.0, 1.0], got {prob}")
        self.prob_of_infection = prob
        self.benefit = prob

    def __repr__(self) -> str:
        """
        Returns a string representation of this person.

        @returns: A string of the form 'P0 (infected)' or 'P0 (healthy)'.
        """
        status = "infected" if self.state else "healthy"
        return f"P{self.index} ({status})"
