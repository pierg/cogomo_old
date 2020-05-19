from checks.tools import And
from src.contracts.contract import *
from typescogomo.assumption import Domain
from typescogomo.formulae import LTL
from typescogomo.variables import extract_variable


class Pattern(LTL):
    """
    General Pattern Class
    """

    def __init__(self, formula: str, variables: Variables = None):
        super().__init__(formula, variables)
        self.domain_properties = []


class CoreMovement(Pattern):
    """Core Movements Patterns
    All the variables are locations where there robot can be at a certain time"""

    def __init__(self, pattern_formula: str, locations: List[LTL], variables: Variables):

        # Eliminating duplicates
        list_locations = list(dict.fromkeys(locations))

        """Domain Property: A robot cannot be in the same location at the same time"""
        ltl_formula = "G("
        for i, loc in enumerate(list_locations):
            ltl_formula += "(" + loc.formula
            for loc_other in list_locations:
                if loc != loc_other:
                    ltl_formula += " & !" + loc_other.formula
            ltl_formula += ")"
            if i < len(list_locations) - 1:
                ltl_formula += " | "

        ltl_formula += ")"

        super().__init__(And([pattern_formula, ltl_formula]), variables)

        self.domain_properties.append(Domain(ltl_formula, variables))


class Visit(CoreMovement):
    """Visit a set of locations in an unspecified order"""

    def __init__(self, locations: List[LTL]):
        variables = Variables()
        pattern_formula = []

        for location in locations:
            variables.extend(location.variables)
            pattern_formula.append("F(" + location.formula + ")")

        pattern_formula = And(pattern_formula)

        super().__init__(pattern_formula, locations, variables)


class SequencedVisit(CoreMovement):
    """Visit a set of locations in sequence, one after the other"""

    def __init__(self, locations: List[LTL]):

        variables = Variables()
        pattern_formula = "F("

        for n, location in enumerate(locations):
            variables.extend(location.variables)
            pattern_formula += location.formula
            if n == len(locations) - 1:
                for _ in range(len(locations)):
                    pattern_formula += ")"
            else:
                pattern_formula += " & F("

        super().__init__(pattern_formula, locations, variables)


class Patroling(CoreMovement):
    """Keep visiting a set of locations, but not in a particular order"""

    def __init__(self, locations: List[LTL] = None):
        variables = Variables()
        pattern_formula = []

        for location in locations:
            variables.extend(location.variables)
            pattern_formula.append("G(F(" + location.formula + "))")

        pattern_formula = And(pattern_formula)

        super().__init__(pattern_formula, locations, variables)


class OrderedVisit(CoreMovement):
    """Sequence visit does not forbid to visit a successor location before its predecessor, but only that after the
    predecessor is visited the successor is also visited. Ordered visit forbids a successor to be visited
    before its predecessor."""

    def __init__(self, locations: List[LTL]):

        variables = Variables()
        pattern_formula = []

        guarantee = "F("
        for n, location in enumerate(locations):
            variables.extend(location.variables)
            guarantee += location.formula
            if n == len(locations) - 1:
                for _ in range(len(locations)):
                    guarantee += ")"
            else:
                guarantee += " & F("

        pattern_formula.append(guarantee)

        for n, location in enumerate(locations):
            if n < len(locations) - 1:
                pattern_formula.append("(!" + locations[n + 1].formula + " U " + locations[n].formula + ")")

        pattern_formula = And(pattern_formula)

        super().__init__(pattern_formula, locations, variables)


class GlobalAvoidance(Pattern):
    """Always avoid"""

    def __init__(self, proposition: LTL):
        variables = proposition.variables
        pattern_formula = "G(!" + proposition.formula + ")"

        super().__init__(pattern_formula, variables)


"""Trigger Pattern"""


class TriggerPattern(Pattern):

    def __init__(self, formula: str, variables: Variables):
        super().__init__(formula, variables)


class DelayedReaction(TriggerPattern):
    """Delayed Reaction Pattern"""

    def __init__(self, trigger: LTL, reaction: LTL):
        variables = Variables()
        variables.extend(trigger.variables)
        variables.extend(reaction.variables)
        pattern_formula = "G(({t}) -> F({r}))".format(t=trigger.formula, r=reaction.formula)

        super().__init__(pattern_formula, variables)


class InstantReaction(Pattern):
    """Instant Reaction Pattern"""

    def __init__(self, trigger: LTL, reaction: LTL):
        variables = Variables()
        variables.extend(trigger.variables)
        variables.extend(reaction.variables)
        pattern_formula = "G(({t}) -> ({r}))".format(t=trigger.formula, r=reaction.formula)

        super().__init__(pattern_formula, variables)


class PromptReaction(Pattern):
    """The occurrence of a stimulus triggers a counteraction promptly, i.e. in the next time instant."""

    def __init__(self, trigger: LTL, reaction: LTL):
        variables = Variables()
        variables.extend(trigger.variables)
        variables.extend(reaction.variables)
        pattern_formula = "G(({t}) -> X({r}))".format(t=trigger.formula, r=reaction.formula)

        super().__init__(pattern_formula, variables)


class BoundReaction(Pattern):
    """A counteraction must be performed every time and only when a speciﬁc location is entered."""

    def __init__(self, trigger: LTL, reaction: LTL):
        variables = Variables()
        variables.extend(trigger.variables)
        variables.extend(reaction.variables)
        pattern_formula = "G( (({t}) -> ({r})) & (({r}) -> ({t})))".format(t=trigger.formula, r=reaction.formula)

        super().__init__(pattern_formula, variables)

