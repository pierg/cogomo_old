from typing import List

from typescogomo.assumptions import Assumptions, Assumption
from typescogomo.guarantees import Guarantees, Guarantee
from itertools import permutations

from typescogomo.variables import Variables, Boolean


class Contract:
    def __init__(self,
                 assumptions: Assumptions = None,
                 guarantees: Guarantees = None
                 ):

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

    def merge_with(self, other):

        self.add_guarantees(other.guarantees.list)
        self.add_assumptions(other.assumptions.list)

    def add_assumptions(self, assumptions: List[Assumption]):

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
