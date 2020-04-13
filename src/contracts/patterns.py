from checks.tools import And
from src.contracts.contract import *
from typescogomo.assumptions import Domain
from typescogomo.variables import extract_variable


class Pattern(Contract):
    """
    General Pattern Class
    """

    def __init__(self, formula: str, variables: Variables):
        super().__init__()
        self.domain_properties = []
        self.add_guarantees(Guarantee(formula, variables))

    def add_domain_properties(self):
        if self.domain_properties is not []:
            self.add_assumptions(self.domain_properties)


class CoreMovement(Pattern):
    """Core Movements Patterns
    All the variables are locations where there robot can be at a certain time"""

    def __init__(self, locations: List[str], formula: str):

        if locations is None:
            raise Exception("No location provided")

        # Eliminating duplicates
        list_locations = list(dict.fromkeys(locations))

        """Adding variables for each location"""
        vars = [Boolean(loc) for loc in locations]
        variables = Variables(vars)

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

        self.domain_properties.append(Domain(ltl_formula, Variables(vars)))
        super().__init__(formula, variables)


class Visit(CoreMovement):
    """Visit a set of locations in an unspecified order"""

    def __init__(self, locations: List[str] = None):
        conj_list = []
        for location in locations:
            conj_list.append("F(" + location + ")")

        super().__init__(locations, And(conj_list))


class SequencedVisit(CoreMovement):
    """Visit a set of locations in sequence, one after the other"""

    def __init__(self, locations: List[str] = None):

        guarantee = "F("
        for n, location in enumerate(locations):

            guarantee += location
            if n == len(locations) - 1:
                for _ in range(len(locations)):
                    guarantee += ")"
            else:
                guarantee += " & F("

        self.add_guarantees(Guarantee(guarantee))
        super().__init__(locations, guarantee)


class OrderedVisit(CoreMovement):
    """Sequence visit does not forbid to visit a successor location before its predecessor, but only that after the
    predecessor is visited the successor is also visited. Ordered visit forbids a successor to be visited
    before its predecessor."""

    def __init__(self, locations: List[str] = None):

        conj_list = []

        guarantee = "F("
        for n, location in enumerate(locations):

            guarantee += location
            if n == len(locations) - 1:
                for _ in range(len(locations)):
                    guarantee += ")"
            else:
                guarantee += " & F("

        conj_list.append(guarantee)

        for n, location in enumerate(locations):
            if n < len(locations) - 1:
                conj_list.append("(!" + locations[n + 1] + " U " + locations[n] + ")")

        super().__init__(locations, And(conj_list))


class GlobalAvoidance(Pattern):
    """Always avoid"""

    def __init__(self, proposition: str = None):
        if proposition is None:
            raise Exception("No proposition provided")

        variables = extract_variable(proposition)

        super().__init__("G(!" + proposition + ")", variables)


class DelayedReaction(Pattern):
    """Delayed Reaction Pattern"""

    def __init__(self, trigger=None, reaction=None):
        if trigger is None or reaction is None:
            raise Exception("No trigger or reaction provided")

        variables = Variables([Boolean(trigger), Boolean(reaction)])

        super().__init__("G(" + trigger + " -> F(" + reaction + "))", variables)
