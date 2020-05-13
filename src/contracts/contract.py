from typing import List, Union, Pattern

from typescogomo.assumption import Assumption
from typescogomo.formula import LTL, InconsistentException
from typescogomo.guarantee import Guarantee
from typescogomo.variables import Variables, Boolean
from typescogomo.formulae import Assumptions, Guarantees


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

    def add_assumptions(self, assumptions: Union[List[Assumption], Assumption]):

        try:
            self.assumptions.add(assumptions)
        except InconsistentException as e:
            raise IncompatibleContracts(e.conj_a, e.conj_b)

        self.guarantees.saturate_with(self.assumptions)

    def add_guarantees(self, guarantees: Union[List[Guarantee], Guarantee]):
        try:
            self.guarantees.add(guarantees)
        except InconsistentException as e:
            raise InconsistentContracts(e.conj_a, e.conj_b)

    def propagate_assumptions_from(self, c: 'Contract'):

        self.assumptions.extend(c.assumptions)

    def refines(self, other: 'Contract') -> bool:

        smaller_g = self.guarantees.formula <= other.guarantees.formula
        bigger_a = self.assumptions.formula >= other.assumptions.formula
        return smaller_g and bigger_a

    def cost(self):
        """Used for component selection. Always [0, 1]
        Lower is better"""
        lg = len(self.guarantees.list)
        la = len(self.assumptions.list)

        """heuristic
        Low: guarantees while assuming little (assumption set is bigger)
        High: guarantees while assuming a lot (assumption set is smaller)"""

        return la / lg

    def add_domain_properties(self):
        pass

    def __str__(self):
        """Override the print behavior"""
        astr = '  variables:\t[ '
        for var in self.variables.list:
            astr += str(var) + ', '
        astr = astr[:-2] + ' ]\n  assumptions      :\t[ '
        for assumption in self.assumptions.list:
            astr += assumption.formula + ', '
        astr = astr[:-2] + ' ]\n  guarantees_satur :\t[ '
        for guarantee in self.guarantees.list:
            astr += guarantee.saturated + ', '
        astr = astr[:-2] + ' ]\n  guarantees_unsat :\t[ '
        for guarantee in self.guarantees.list:
            astr += guarantee.unsaturated + ', '
        return astr[:-2] + ' ]\n'


class IncompatibleContracts(Exception):
    def __init__(self, assumptions_1: Assumption, assumptions_2: Assumption):
        self.assumptions_1 = assumptions_1
        self.assumptions_2 = assumptions_2

class InconsistentContracts(Exception):
    def __init__(self, guarantee_1: Guarantee, guarantee_2: Guarantee):
        self.guarantee_1 = guarantee_1
        self.guarantee_2 = guarantee_2

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


class SimpleContract(Contract):

    def __init__(self,
                 guarantees: List[str],
                 assumptions: List[str] = None):

        guarantees_obj = []

        from typescogomo.variables import extract_variable

        for g in guarantees:
            guarantees_obj.append(Guarantee(g, extract_variable(g)))

        guarantees_obj = Guarantees(guarantees_obj)

        if assumptions is None:
            assumptions_obj = Assumptions()

        else:
            assumptions_obj = []

            for a in assumptions:
                assumptions_obj.append(Assumption(a, extract_variable(a)))

            assumptions_obj = Assumptions(assumptions_obj)
            guarantees_obj.saturate_with(assumptions_obj)

        super().__init__(assumptions=assumptions_obj,
                         guarantees=guarantees_obj)


class PContract(Contract):

    def __init__(self, patterns: List[LTL]):
        self.patterns = patterns

        variables = Variables()

        guarantees = []

        for p in patterns:
            variables.extend(p.variables)
            guarantees.append(Guarantee(p.formula, p.variables))

        guarantees = Guarantees(guarantees)

        super().__init__(guarantees=guarantees)
