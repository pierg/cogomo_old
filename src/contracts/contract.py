from copy import copy
from typing import Dict, List, Tuple, Union
from src.checks.nsmvhelper import *


class SaturatedContract(object):
    """Contract class stores data attributes of a contract"""

    def __init__(self,
                 variables: Dict[str, str] = None,
                 assumptions: List[str] = None,
                 guarantees: List[str] = None):

        """Initialize a contract object"""

        """Dictionary where: key=name of the variable, value=type of the variable"""
        self._variables: Dict[str, str] = {}

        """List of assumptions in conjunction"""
        self._assumptions: List[str] = []

        """List of guarantees in conjunction. All guarantees are saturated"""
        self._guarantees: List[str] = []

        if variables is None:
            pass
        else:
            self._variables = variables

        if assumptions is None:
            self._assumptions = ["TRUE"]
        else:
            self._assumptions = assumptions

        if guarantees is None:
            pass
        else:
            self._guarantees = guarantees

        self.validate()

    @property
    def variables(self):
        return self._variables

    @variables.setter
    def variables(self, values: Dict[str, str]):
        self._variables = values

    @property
    def assumptions(self) -> List[str]:
        return self._assumptions

    @assumptions.setter
    def assumptions(self, values: List[str]):
        self._assumptions = values

    @property
    def guarantees(self) -> List[str]:
        return self._guarantees

    @guarantees.setter
    def guarantees(self, values: List[Tuple[str, str]]):
        self._guarantees = values

    def _is_compatible(self) -> bool:
        """Check Compatibility"""
        return check_satisfiability(self.variables, self.assumptions)

    def _is_consistent(self) -> bool:
        """Check Consistency"""
        return check_satisfiability(self.variables, self.guarantees)

    def is_feasible(self) -> bool:
        """Check Consistency"""
        return check_satisfiability(self.variables, self.guarantees)

    def validate(self):
        """Performs compatibility, consistency and feasibility checks on the contract"""
        if not self._is_compatible():
            raise Exception("The contract is incompatible")
        if not self._is_consistent():
            raise Exception("The contract is inconsistent")
        if not self.is_feasible():
            raise Exception("The contract is unfeasible")

    def add_variables(self, variables: Dict[str, str]):

        common_keys = self.variables.keys() & variables.keys()

        for k in common_keys:
            if self.variables[k] != variables[k]:
                raise Exception("Variable " + k + " is already present but "
                                                  "with type " + self.variables[k] + " instead of " + variables[k])

        self.variables.update(variables)

    def add_assumptions(self, assumptions: List[str]):

        for assumption in assumptions:
            self.add_assumption(assumption)

    def add_assumption(self, assumption: str):

        if "TRUE" in self.assumptions:
            self.assumptions.remove("TRUE")

        """Check if assumption is a abstraction of existing assumptions and vice-versa"""
        for a in self.assumptions:

            """Ignore if its a port"""
            if "port" in a:
                continue

            if is_implied_in(self.variables, a, assumption):
                self.assumptions.remove(a)

            elif is_implied_in(self.variables, assumption, a):
                return

        """Adding assumption"""
        self.assumptions.append(assumption)

        """Check Compatibility"""
        if not self._is_compatible():
            conflict = self.assumptions.copy()
            self.assumptions.remove(assumption)
            raise Exception("adding " + assumption + " resulted in a incompatible contract:\n" + str(conflict))

    def add_guarantees(self, guarantees: List[Union[Tuple[str, str], str]]):
        """guarantees can either be a list of strings or a list of tuple (a,g)
        In the first case the guarantee will be saturated with 'TRUE'"""

        for guarantee in guarantees:
            self.add_guarantee(guarantee)

    def add_guarantee(self, guarantee: Union[Tuple[str, str], str]):

        if isinstance(guarantee, tuple):
            a, g = guarantee
            saturated_guarantee = Implies(a, g)
        else:
            saturated_guarantee = Implies("TRUE", guarantee)

        """Check if guarantee is a refinement of existing guarantee and vice-versa"""
        for g in self.guarantees:

            if is_implied_in(self.variables, g, saturated_guarantee):
                self.guarantees.remove(g)

            elif is_implied_in(self.variables, saturated_guarantee, g):
                return

        """Adding guarantee"""
        self.guarantees.append(guarantee)

        """Check Consistency"""
        if not self._is_consistent():
            conflict = self.guarantees.copy()
            self.guarantees.remove(guarantee)
            raise Exception("adding " + str(guarantee) + " resulted in a inconsistent contract:\n" + conflict)

    def add_expectations(self, expectations: List['SaturatedContract']):
        """Expectations are conditional assumptions, they get added
        only if the Contract guarantees are a refinement of the Expectation guarantees"""

        for expectation in expectations:

            if are_implied_in([expectation.variables, self.variables],
                              self.guarantees,
                              expectation.guarantees):
                self.add_variables(expectation.variables)
                self.add_assumptions(expectation.assumptions)

    def _has_smaller_guarantees_than(self, c: 'SaturatedContract') -> bool:

        return are_implied_in([self.variables, c.variables],
                              self.guarantees,
                              c.guarantees)

    def _has_bigger_assumptions_than(self, c: 'SaturatedContract') -> bool:

        return are_implied_in([c.variables, self.variables],
                              c.assumptions,
                              self.assumptions)

    def propagate_assumptions_from(self, c: 'SaturatedContract'):
        self.add_variables(c.variables)
        self.add_assumptions(c.assumptions)

    def is_refined_by(self, c: 'SaturatedContract') -> bool:
        if not (c._has_smaller_guarantees_than(self) and
                c._has_bigger_assumptions_than(self)):
            return False
        return True

    def is_full(self):

        return self.variables and self.assumptions and self.guarantees

    def cost(self):
        """Used for component selection. Always [0, 1]
        Lower is better"""
        lg = len(self.guarantees)
        la = len(self.assumptions)

        """heuristic
        Low: guarantees while assuming little (assumption set is bigger)
        High: guarantees while assuming a lot (assumption set is smaller)"""

        return la / lg


class Contract(SaturatedContract):
    def __init__(self,
                 variables: Dict[str, str] = None,
                 assumptions: List[str] = None,
                 guarantees: List[str] = None):

        saturated_guarantees = None

        if guarantees is not None:
            saturated_guarantees = []
            for g in guarantees:
                saturated_guarantees.append(Implies(And(assumptions), g))

        super().__init__(variables=variables,
                         assumptions=assumptions,
                         guarantees=saturated_guarantees)

        self._unsaturated_guarantees = guarantees

    def __str__(self):
        """Override the print behavior"""
        astr = '  variables: [ '
        for var in self.variables:
            astr += '(' + var + '), '
        astr = astr[:-2] + ' ]\n  assumptions: [ '
        for assumption in self.assumptions:
            astr += str(assumption) + ', '
        astr = astr[:-2] + ' ]\n  guarantees: [ '
        for guarantee in self.unsaturated_guarantees:
            astr += str(guarantee) + ', '
        return astr[:-2] + ' ]\n]'

    @property
    def unsaturated_guarantees(self):
        return self.unsaturated_guarantees

    @unsaturated_guarantees.setter
    def unsaturated_guarantees(self, values: List[str]):
        self.unsaturated_guarantees = values


class BooleanContract(Contract):

    def __init__(self,
                 assumptions: List[str],
                 guarantees: List[str]):

        variables: Dict[str, str] = {}

        for a in assumptions:
            variables.update({a: "boolean"})
        for g in guarantees:
            variables.update({g: "boolean"})

        super().__init__(variables=variables,
                         assumptions=assumptions,
                         guarantees=guarantees)
