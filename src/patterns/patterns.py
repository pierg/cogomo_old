from src.contracts.contract import *


class Pattern(Contract):
    """
    General Pattern Class
    """

    def __init__(self):
        super().__init__()
        self.domain_properties: List[Assumption] = []

    def add_domain_properties(self):
        self.add_assumptions(self.domain_properties)


class CoreMovement(Pattern):
    """Core Movements Patterns
    All the variables are locations where there robot can be at a certain time"""

    def __init__(self, locations: List[str] = None):
        super().__init__()

        if locations is None:
            raise Exception("No location provided")

        """Adding variables for each location"""
        self.add_variables([Boolean(loc) for loc in locations])

        # Eliminating duplicates
        list_locations = list(dict.fromkeys(locations))

        """Domain Property: A robot cannot be in the same location at the same time"""
        ltl_formula = "G("
        for i, loc in enumerate(list_locations):
            ltl_formula += "(" + loc
            for loc_other in list_locations:
                if loc != loc_other:
                    ltl_formula += " & !" + loc_other
            ltl_formula += ")"
            if i < len(list_locations) - 1:
                ltl_formula += " | "

        ltl_formula += ")"

        self.domain_properties.append(Assumption(ltl_formula, kind="domain"))


class Visit(CoreMovement):
    """Visit a set of locations in an unspecified order"""

    def __init__(self, locations: List[str] = None):
        super().__init__(locations)

        """Adding the pattern as guarantee"""
        for location in locations:
            self.add_guarantee(Guarantee("F(" + location + ")"))


class SequencedVisit(CoreMovement):
    """Visit a set of locations in sequence, one after the other"""

    def __init__(self, locations: List[str] = None):

        super().__init__(locations)

        """Adding the pattern as guarantee"""
        guarantee = "F("
        for n, location in enumerate(locations):

            guarantee += location
            if n == len(locations) - 1:
                for _ in range(len(locations)):
                    guarantee += ")"
            else:
                guarantee += " & F("

        self.add_guarantee(Guarantee(guarantee))


class OrderedVisit(CoreMovement):
    """Sequence visit does not forbid to visit a successor location before its predecessor, but only that after the
    predecessor is visited the successor is also visited. Ordered visit forbids a successor to be visited
    before its predecessor."""

    def __init__(self, locations: List[str] = None):

        super().__init__(locations)

        """Adding the pattern as guarantee"""
        guarantee = "F("
        for n, location in enumerate(locations):

            guarantee += location
            if n == len(locations) - 1:
                for _ in range(len(locations)):
                    guarantee += ")"
            else:
                guarantee += " & F("

        self.add_guarantee(Guarantee(guarantee))

        for n, location in enumerate(locations):
            if n < len(locations) - 1:
                self.add_guarantee(Guarantee("!" + locations[n + 1] + " U " + locations[n]))


class GlobalAvoidance(Pattern):
    """Always avoid"""

    def __init__(self, proposition: str = None):
        super().__init__()

        if proposition is None:
            raise Exception("No proposition provided")

        self.add_variables([Boolean(proposition)])

        self.add_guarantee(Guarantee("G(!" + proposition + ")"))


class DelayedReaction(Pattern):
    """Delayed Reaction Pattern"""

    def __init__(self, trigger=None, reaction=None):
        super().__init__()
        if trigger is None or reaction is None:
            raise Exception("No trigger or reaction provided")

        self.add_variables([Boolean(trigger)])
        self.add_variables([Boolean(reaction)])

        self.add_guarantee(Guarantee("G(" + trigger + " -> F(" + reaction + "))"))
