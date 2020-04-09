from typing import List

from typescogomo.assumptions import Assumptions, Assumption
from typescogomo.guarantees import Guarantees, Guarantee
from itertools import permutations

from typescogomo.variables import Variables, Boolean


class Contract:
    def __init__(self,
                 assumptions: Assumptions = None,
                 guarantees: Guarantees = None,
                 simplify: bool = True,
                 validate: bool = True
                 ):

        """Remove redundant assumptions and guarantees"""
        if simplify:
            if guarantees is not None:
                """Check any guarantee is a refinement of another guarantee and vice-versa"""
                g_pairs = permutations(guarantees.formulae, 2)
                g_removed = []
                for g_1, g_2 in g_pairs:
                    if g_1 <= g_2:
                        if g_2 not in g_removed:
                            guarantees.remove(g_2)
                            g_removed.append(g_2)

            if assumptions is not None:
                """Check any assumption is an abstraction of another assumption and vice-versa"""
                a_pairs = permutations(assumptions.formulae, 2)
                a_removed = []
                for a_1, a_2 in a_pairs:
                    """Ignore if its a port"""
                    if hasattr(a_1, "port_type") or hasattr(a_2, "port_type"):
                        continue
                    if a_1 >= a_2:
                        if a_2 not in a_removed:
                            assumptions.remove(a_2)
                            a_removed.append(a_2)

        """List of assumptions in conjunction"""
        if assumptions is None:
            self.__assumptions = Assumptions()
        else:
            self.__assumptions = assumptions

        """List of guarantees in conjunction. All guarantees are saturated"""
        if guarantees is None:
            self.__guarantees = Guarantees()
        else:
            self.__guarantees = guarantees

        """Checks feasibility"""
        if validate:
            if not self.assumptions.are_satisfiable_with(self.guarantees):
                raise Exception("The contract is unfeasible")

    @property
    def variables(self):
        a_vars = self.assumptions.variables
        g_vars = self.guarantees.variables
        return a_vars + g_vars

    @property
    def assumptions(self) -> Assumptions:
        return self.__assumptions

    @assumptions.setter
    def assumptions(self, values: Assumptions):
        self.__assumptions = values

    @property
    def guarantees(self) -> Guarantees:
        return self.__guarantees

    @guarantees.setter
    def guarantees(self, values: Guarantees):
        self.__guarantees = values

    def remove_contextual_assumptions(self):
        self.assumptions.remove_kind("context")

    def add_assumption(self, assumptions: List[Assumption]):

        self.assumptions.add(assumptions)

        self.guarantees.saturate_with(self.assumptions)

    def add_guarantees(self, guarantees: List[Guarantee]):

        self.guarantees.add(guarantees)

    def propagate_assumptions_from(self, c: 'Contract'):

        self.assumptions.extend(c.assumptions)

    def is_refined_by(self, other: 'Contract') -> bool:

        smaller_g = self.guarantees.formula <= other.guarantees.formula
        bigger_a = self.assumptions.formula >= other.assumptions.formula
        return smaller_g and bigger_a

    def cost(self):
        """Used for component selection. Always [0, 1]
        Lower is better"""
        lg = len(self.guarantees.formulae)
        la = len(self.assumptions.formulae)

        """heuristic
        Low: guarantees while assuming little (assumption set is bigger)
        High: guarantees while assuming a lot (assumption set is smaller)"""

        return la / lg

    def __str__(self):
        """Override the print behavior"""
        astr = '  variables:\t[ '
        for var in self.variables:
            astr += str(var) + ', '
        astr = astr[:-2] + ' ]\n  assumptions      :\t[ '
        for assumption in self.assumptions.formulae:
            astr += assumption.formula + ', '
        astr = astr[:-2] + ' ]\n  guarantees_satur :\t[ '
        for guarantee in self.guarantees.formulae:
            astr += guarantee.saturated + ', '
        astr = astr[:-2] + ' ]\n  guarantees_unsat :\t[ '
        for guarantee in self.guarantees.formulae:
            astr += guarantee.unsaturated + ', '
        return astr[:-2] + ' ]\n'


class BooleanContract(Contract):

    def __init__(self,
                 assumptions_str: List[str],
                 guarantees_str: List[str]):

        assumptions = []
        guarantees = []

        for a in assumptions_str:
            assumptions.append(Assumption(a, Variables(Boolean(a))))

        for g in guarantees_str:
            guarantees.append(Guarantee(g, Variables(Boolean(g))))

        assumptions = Assumptions(assumptions)
        guarantees = Guarantees(guarantees)

        guarantees.saturate_with(assumptions)

        super().__init__(assumptions=assumptions,
                         guarantees=guarantees)
