from itertools import permutations

from contracts.formulas import Assumption, Guarantee
from src.checks.nsmvhelper import *
from src.contracts.types import *


class Contract:
    def __init__(self,
                 variables: List[Type] = None,
                 assumptions: List[Assumption] = None,
                 guarantees: List[Guarantee] = None,
                 simplify: bool = True,
                 validate: bool = True
                 ):

        """Remove redundant assumptions and guarantees"""
        if simplify:
            if guarantees is not None:
                """Check any guarantee is a refinement of another guarantee and vice-versa"""
                g_pairs = permutations(guarantees, 2)

                for g_1, g_2 in g_pairs:
                    if is_implied_in(variables, g_1, g_2):
                        guarantees.remove(g_2)

            if assumptions is not None:
                """Check any assumption is an abstraction of another assumption and vice-versa"""
                a_pairs = permutations(assumptions, 2)
                for a_1, a_2 in a_pairs:
                    """Ignore if its a port"""
                    if hasattr(a_1, "port_type") or hasattr(a_2, "port_type"):
                        continue
                    if is_implied_in(variables, a_1, a_2):
                        assumptions.remove(a_1)

        """List of variables"""
        if variables is None:
            self.__variables = []
        else:
            self.__variables = variables

        """List of assumptions in conjunction"""
        if assumptions is None:
            self.__assumptions = [Assumption("TRUE")]
        elif isinstance(assumptions, list) and len(assumptions) == 0:
            self.__assumptions = [Assumption("TRUE")]
        else:
            self.__assumptions = assumptions

        """List of guarantees in conjunction. All guarantees are saturated"""
        if guarantees is None:
            self.__guarantees = []
        else:
            self.__guarantees = guarantees

        """Checks compatibility, consistency and feasibility"""
        if validate and self.is_full():
            """Performs compatibility, consistency and feasibility checks on the contract"""
            if not check_satisfiability(self.__variables, self.__assumptions):
                raise Exception("The contract is incompatible")
            if not check_satisfiability(self.__variables, self.__guarantees):
                raise Exception("The contract is inconsistent")
            if not check_satisfiability(self.__variables, self.__guarantees + self.__assumptions):
                raise Exception("The contract is unfeasible")

    @property
    def variables(self):
        return self.__variables

    @variables.setter
    def variables(self, values: List[Type]):
        self.__variables = values

    @property
    def assumptions(self) -> List[Assumption]:
        return self.__assumptions

    @assumptions.setter
    def assumptions(self, values: List[Assumption]):
        if isinstance(values, list) and len(values) == 0:
            self.__assumptions = [Assumption("TRUE")]
        else:
            self.__assumptions = values

    @property
    def guarantees(self) -> List[Guarantee]:
        return self.__guarantees

    @guarantees.setter
    def guarantees(self, values: List[Guarantee]):
        self.__guarantees = values

    def add_variables(self, variables: List[Type]):

        add_variables_to_list(self.variables, variables)

    def add_assumptions(self, assumptions: List[Assumption]):

        for assumption in assumptions:
            self.add_assumption(assumption)

    def add_assumption(self, assumption: Assumption):

        for a in list(self.assumptions):
            if a.formula == "TRUE":
                self.assumptions.remove(a)

        """Check if assumption is a abstraction of existing assumptions and vice-versa"""
        for a in self.assumptions:

            if is_implied_in(self.variables, a, assumption):
                self.assumptions.remove(a)

            elif is_implied_in(self.variables, assumption, a):
                return

        """Adding assumption if is compatible with th other assumptions"""
        add_proposition_to_list(self.variables, self.assumptions, assumption)

        if len(self.assumptions) == 0:
            self.assumptions = [Assumption("TRUE")]

    def add_guarantees(self, guarantees: List[Guarantee]):
        """Add guarantees in 'guarantees'"""

        for i, guarantee in enumerate(guarantees):
            self.add_guarantee(guarantee)

    def add_guarantee(self, guarantee: Guarantee):

        """Check if guarantee is a refinement of existing guarantee and vice-versa"""
        for i, g in enumerate(self.guarantees):
            if is_implied_in(self.variables, guarantee, g):
                print("simplifying\t" + str(self.guarantees[i]))
                del self.guarantees[i]

        """Adding guarantee if is consistent with th other guarantees"""
        add_proposition_to_list(self.variables, self.guarantees, guarantee)

    def _has_smaller_guarantees_than(self, c: 'Contract') -> bool:

        return are_implied_in([self.variables, c.variables],
                              self.guarantees,
                              c.guarantees)

    def _has_bigger_assumptions_than(self, c: 'Contract') -> bool:

        return are_implied_in([c.variables, self.variables],
                              c.assumptions,
                              self.assumptions)

    def propagate_assumptions_from(self, c: 'Contract'):
        """propagates assumptions while simplifying other assumptions"""
        self.add_variables(c.variables)
        self.add_assumptions(c.assumptions)

    def is_refined_by(self, c: 'Contract') -> bool:
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

    def __str__(self):
        """Override the print behavior"""
        astr = '  variables:\t[ '
        for var in self.variables:
            astr += str(var) + ', '
        astr = astr[:-2] + ' ]\n  assumptions:\t[ '
        for assumption in self.assumptions:
            astr += str(assumption) + ', '
        astr = astr[:-2] + ' ]\n  guarantees :\t[ '
        for guarantee in self.guarantees:
            astr += str(guarantee) + ', '
        astr = astr[:-2] + ' ]\n  saturated  :\t[ '
        for guarantee in self.guarantees:
            astr += str(guarantee.saturated) + ', '
        return astr[:-2] + ' ]\n'


class BooleanContract(Contract):

    def __init__(self,
                 assumptions_str: List[str],
                 guarantees_str: List[str]):

        variables: List[Type] = []

        for a in assumptions_str:
            variables.append(Boolean(a))
        for g in guarantees_str:
            variables.append(Boolean(g))

        assumptions = []
        guarantees = []

        for a in assumptions_str:
            assumptions.append(Assumption(a))

        for g in guarantees_str:
            saturated = Implies(And(assumptions), LTL(g))
            guarantees.append(Guarantee(g, saturated=str(saturated)))

        super().__init__(variables=variables,
                         assumptions=assumptions,
                         guarantees=guarantees)
