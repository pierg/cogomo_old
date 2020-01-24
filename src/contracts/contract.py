from typing import Dict, List, Tuple
from src.checks.nsmvhelper import *


class Contract(object):
    """Contract class stores data attributes of a contract"""

    def __init__(self,
                 variables: Dict[str, str] = None,
                 assumptions: List[str] = None,
                 guarantees: List[str] = None):

        """Initialize a contract object"""
        self.variables = {}
        self.assumptions = []
        self.guarantees = []

        if variables is None:
            self.variables = {}
        elif isinstance(variables, dict):
            self.variables = variables
        else:
            raise AttributeError

        if guarantees is None:
            self.guarantees = []
        elif isinstance(guarantees, list):
            self.add_guarantees(guarantees)
        else:
            raise AttributeError

        if assumptions is None:
            self.assumptions = ["TRUE"]
        elif isinstance(assumptions, list):
            self.add_assumptions(assumptions)
        else:
            raise AttributeError

    """Variables"""

    def add_variable(self, variable: Tuple[str, str]):
        name, var_type = variable
        self.variables[name] = var_type

    def add_variables(self, variables: List[Tuple[str, str]]):
        if isinstance(variables, tuple):
            for variable in variables:
                self.add_variable(variable)
        elif isinstance(variables, dict):
            self.variables.update(variables)

    def merge_variables(self, variables_dictionary: Dict[str, str]):
        variables_copy = self.variables.copy()
        variables_copy.update(variables_dictionary)
        self.variables = variables_copy

    def get_variables(self):
        return self.variables

    """Assumptions"""

    def add_assumption(self, assumption: str):
        if not isinstance(assumption, str):
            raise AttributeError

        if "TRUE" in self.assumptions:
            self.assumptions.remove("TRUE")

        """Check if assumption is a refinement of exising assumptions and vice-versa"""
        for a in self.assumptions:

            """Check if the proposition is a port, then don't check"""
            var_a = re.sub("_port_\d+|_port", "", a)
            var_b = re.sub("_port_\d+|_port", "", assumption)

            if var_a == var_b:
                continue

            if is_set_smaller_or_equal(self.variables, self.variables, assumption, a):
                self.assumptions.remove(a)

            elif is_set_smaller_or_equal(self.variables, self.variables, a, assumption):
                return

        """Adding assumption"""
        self.assumptions.append(assumption)

        """Check Compatibility"""
        if not check_satisfiability(self.variables, self.assumptions):
            self.assumptions.remove(assumption)
            raise Exception("adding " + assumption + " resulted in a incompatible contract:\n" + str(self.assumptions))

    def add_assumptions(self, assumptions: List[str]):
        if isinstance(assumptions, list):
            for assumption in assumptions:
                self.add_assumption(assumption)
        else:
            raise AttributeError

    def get_ltl_assumptions(self):
        if len(self.assumptions) > 1:
            return And(self.assumptions)
        else:
            return self.assumptions[0]


    def get_list_assumptions(self):

        return self.assumptions

    """Guarantees"""

    def add_guarantee(self, guarantee: str):
        if not isinstance(guarantee, str):
            raise AttributeError

        """Check if guarantee is a refinement of existing gurantee and vice-versa"""
        for g in self.guarantees:
            if is_set_smaller_or_equal(self.variables, self.variables, guarantee, g):
                self.guarantees.remove(g)
            elif is_set_smaller_or_equal(self.variables, self.variables, g, guarantee):
                return

        """Adding guarantee"""
        self.guarantees.append(guarantee)

        """Check Consistency"""
        if not check_satisfiability(self.variables, self.guarantees):
            self.guarantees.remove(guarantee)
            raise Exception("adding " + guarantee + " resulted in a inconsistent contract:\n" + str(self.guarantees))

    def add_guarantees(self, guarantees: List[str]):
        for guarantee in guarantees:
            self.add_guarantee(guarantee)

    def get_ltl_guarantees_saturated(self):
        if len(self.guarantees) > 1:
            return Implies(self.get_ltl_assumptions(), And(self.guarantees))
        else:
            return Implies(self.get_ltl_assumptions(), self.guarantees[0])


    def get_list_guarantees_saturated(self):

        guarantees_saturated = []

        for g in self.guarantees:
            guarantees_saturated.append(Implies(self.get_ltl_assumptions(), g))

        return guarantees_saturated

    def get_list_guarantees(self):

        return self.guarantees


    def is_full(self):
        """
        Check if contract parameters are filled
        :return: A boolean indicating if the contracts parameters are not empty
        """
        return self.variables and self.assumptions and self.guarantees

    def cost(self):
        """
        Used for component selection. Always [0, 1]
        Lower is better
        :return: Real number
        """
        lg = len(self.guarantees)
        la = len(self.assumptions)

        """heuristic
        Low: guarantees while assuming little (assumption set is bigger)
        High: guarantees while assuming a lot (assumption set is smaller)"""

        return la / lg

    def __str__(self):
        """Override the print behavior"""
        astr = '  variables: [ '
        for var in self.variables:
            astr += '(' + var + '), '
        astr = astr[:-2] + ' ]\n  assumptions: [ '
        for assumption in self.assumptions:
            astr += str(assumption) + ', '
        astr = astr[:-2] + ' ]\n  guarantees: [ '
        for guarantee in self.guarantees:
            astr += str(guarantee) + ', '
        return astr[:-2] + ' ]\n]'
