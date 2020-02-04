from itertools import permutations
from src.checks.nsmvhelper import *


class SaturatedContract(object):
    """Contract class stores data attributes of a contract"""

    def __init__(self,
                 variables: Dict[str, str] = None,
                 assumptions: List[str] = None,
                 guarantees: List[str] = None,
                 validate: bool = True):

        """Dictionary where: key=name of the variable, value=type of the variable"""
        if variables is None:
            self.__variables = {}
        else:
            self.__variables = variables

        """List of assumptions in conjunction"""
        if assumptions is None:
            self.__assumptions = ["TRUE"]
        elif isinstance(assumptions, list) and len(assumptions) == 0:
            self.__assumptions = ["TRUE"]
        else:
            self.__assumptions = assumptions

        """List of guarantees in conjunction. All guarantees are saturated"""
        if assumptions is None:
            self.__guarantees = []
        else:
            self.__guarantees = guarantees

        """Checks compatibility, consistency and feasibility"""
        if validate:
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
    def variables(self, values: Dict[str, str]):
        self.__variables = values

    @property
    def assumptions(self) -> List[str]:
        return self.__assumptions

    @assumptions.setter
    def assumptions(self, values: List[str]):
        if isinstance(values, list) and len(values) == 0:
            self.__assumptions = ["TRUE"]
        else:
            self.__assumptions = values

    @property
    def guarantees(self) -> List[str]:
        return self.__guarantees

    @guarantees.setter
    def guarantees(self, values: List[str]):
        self.__guarantees = values

    def add_variables(self, variables: Dict[str, str]):

        add_element_to_dict(self.variables, variables)

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

        """Adding assumption if is compatible with th other assumptions"""
        add_proposition_to_list(self.variables, self.assumptions, assumption)

    def add_expectations(self, expectations: List['SaturatedContract']):
        """Expectations are conditional assumptions, they get added
        only if the Contract guarantees are a refinement of the 'expectations' guarantees"""

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
                 guarantees: List[str] = None,
                 saturated: List[str] = None,
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
                """Check any assumption is an abstraction of another guarantee and vice-versa"""
                a_pairs = permutations(assumptions, 2)

                for a_1, a_2 in a_pairs:
                    if is_implied_in(variables, a_1, a_2):
                        assumptions.remove(a_1)

        self.__unsaturated_guarantees: List[str] = guarantees

        if guarantees is not None:
            if saturated is None:
                saturated_guarantees = []
                if assumptions is None or len(assumptions) == 0:
                    assumptions = ["TRUE"]
                for g in guarantees:
                    saturated = Implies(And(assumptions), g)
                    saturated_guarantees.append(saturated)
            else:
                saturated_guarantees = saturated
        else:
            saturated_guarantees = None

        super().__init__(variables=variables,
                         assumptions=assumptions,
                         guarantees=saturated_guarantees,
                         validate=validate)

    @property
    def unsaturated_guarantees(self):
        return self.__unsaturated_guarantees

    @unsaturated_guarantees.setter
    def unsaturated_guarantees(self, values: List[str]):
        self.__unsaturated_guarantees = values

    def add_guarantees(self, guarantees: List[str], saturated: List[str] = None):
        """Add guarantees in 'guarantees'
        If the saturated version is not available, saturate with 'TRUE'"""

        for i, guarantee in enumerate(guarantees):
            if saturated is not None:
                self.add_guarantee(guarantee, saturated[i])

    def add_guarantee(self, guarantee: str, saturated: str = None):

        if saturated is None:
            saturated_guarantee = Implies("TRUE", guarantee)
        else:
            saturated_guarantee = saturated

        """Check if guarantee is a refinement of existing guarantee and vice-versa"""
        for i, g in enumerate(self.guarantees):
            if is_implied_in(self.variables, saturated_guarantee, g):
                print("simplifying\t" + self.guarantees[i])
                print("simplifying\t" + self.unsaturated_guarantees[i])
                del self.guarantees[i]
                del self.unsaturated_guarantees[i]

        """Adding guarantee if is consistent with th other guarantees"""
        add_proposition_to_list(self.variables, self.unsaturated_guarantees, guarantee)
        add_proposition_to_list(self.variables, self.guarantees, saturated_guarantee)

    def __str__(self):
        """Override the print behavior"""
        astr = '  variables:\t[ '
        for var in self.variables:
            astr += var + ', '
        astr = astr[:-2] + ' ]\n  assumptions:\t[ '
        for assumption in self.assumptions:
            astr += str(assumption) + ', '
        astr = astr[:-2] + ' ]\n  guarantees:\t[ '
        for guarantee in self.guarantees:
            astr += str(guarantee) + ', '
        astr = astr[:-2] + ' ]\n  unsaturated:\t[ '
        for guarantee in self.unsaturated_guarantees:
            astr += str(guarantee) + ', '
        return astr[:-2] + ' ]\n'


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
