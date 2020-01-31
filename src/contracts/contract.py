from typing import Dict, List, Tuple
from src.checks.nsmvhelper import *


class Contract(object):
    """Contract class stores data attributes of a contract"""

    def __init__(self,
                 variables: Dict[str, str] = None,
                 assumptions: List[str] = None,
                 guarantees: List[str] = None,
                 guaratnees_saturated: List[str] = None):

        """Initialize a contract object"""
        self.variables = {}
        self.assumptions = []
        self.guarantees = []
        self.guarantees_saturated = []

        if variables is None:
            self.variables = {}
        elif isinstance(variables, dict):
            self.add_variables(variables)
        else:
            raise AttributeError

        if assumptions is None:
            self.assumptions = ["TRUE"]
        elif isinstance(assumptions, list):
            self.add_assumptions(assumptions)
        else:
            raise AttributeError

        if guaratnees_saturated is None:
            if guarantees is None:
                self.guarantees = []
                self.guarantees_saturated = []
            elif isinstance(guarantees, list):
                self.add_guarantees(guarantees)
        else:
            if guarantees is None:
                raise AttributeError
            elif isinstance(guarantees, list):
                self.add_guarantees(guarantees, saturated=guaratnees_saturated)

    """Variables"""

    def add_variable(self, variable: Tuple[str, str]):
        name, var_type = variable
        if name in self.variables.keys():
            if self.variables[name] != var_type:
                raise Exception("Variables Incompatible: \n" + \
                                name + ": " + self.variables[name] + "\n" + \
                                name + ": " + var_type)
        self.variables[name] = var_type

    def add_variables(self, variables: Dict[str, str]):
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

        """Check if assumption is a abstraction of exising assumptions and vice-versa"""
        for a in self.assumptions:

            """Check if the proposition is a port, then don't check"""
            var_a = re.sub("_port_\d+|_port", "", a)
            var_b = re.sub("_port_\d+|_port", "", assumption)

            if var_a == var_b:
                continue

            if is_implied_in(self.variables, a, assumption):
                self.assumptions.remove(a)

            elif is_implied_in(self.variables, assumption, a):
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
        return And(self.assumptions)

    def get_list_assumptions(self):

        return self.assumptions

    """Guarantees"""

    def add_guarantee(self, guarantee: str, saturated: str = None):
        if not isinstance(guarantee, str):
            raise AttributeError

        if len(self.assumptions) == 0:
            raise Exception("Insert Assumptions First")

        if saturated is None:
            """Saturate the guarantee"""
            new_g_sat = Implies(self.get_ltl_assumptions(), guarantee)
        else:
            new_g_sat = saturated

        """Check if guarantee is a refinement of existing guarantee and vice-versa"""
        for idx, g_sat in enumerate(self.guarantees_saturated):
            if is_implied_in(self.variables, new_g_sat, g_sat):
                self.guarantees.remove(self.guarantees[idx])
                self.guarantees_saturated.remove(g_sat)
            elif is_implied_in(self.variables, g_sat, new_g_sat):
                return

        """Adding guarantee"""
        self.guarantees.append(guarantee)
        self.guarantees_saturated.append(new_g_sat)

        """Check Consistency"""
        if not check_satisfiability(self.variables, self.guarantees_saturated):
            self.guarantees.remove(guarantee)
            self.guarantees_saturated.remove(new_g_sat)
            raise Exception("adding " + guarantee + " resulted in a inconsistent contract:\n" + str(self.guarantees))

    def add_guarantees(self, guarantees: List[str], saturated: List[str] = None):
        for guarantee in guarantees:
            self.add_guarantee(guarantee, saturated=None)

    def get_list_guarantees_saturated(self):

        # return self.guarantees

        guarantees_saturated = []

        for g in self.guarantees:
            guarantees_saturated.append(Implies(self.get_ltl_assumptions(), g))

        return guarantees_saturated

    def get_ltl_guarantees(self):
        return And(self.guarantees_saturated)

    def get_list_guarantees(self):

        return self.guarantees

    def has_smaller_guarantees_than(self, c: 'Contract'):

        return are_implied_in([self.variables, c.get_variables()],
                              self.guarantees,
                              c.get_list_guarantees())

    def has_bigger_assumptions_than(self, c: 'Contract'):

        return are_implied_in([c.get_variables(), self.variables],
                              c.get_list_assumptions(),
                              self.assumptions)

    def propagate_assumptions_from(self, c: 'Contract'):
        self.merge_variables(c.variables)
        self.add_assumptions(c.assumptions)

    def is_refined_by(self, c: 'Contract'):
        if not (c.has_smaller_guarantees_than(self) and
                c.has_bigger_assumptions_than(self)):
            raise Exception("Refinement not correct")
        return True

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


class BooleanContract(Contract):

    def __init__(self, assumptions: List[str], guarantees: List[str]):

        variables: Dict[str, str] = {}

        for a in assumptions:
            variables.update({a: "boolean"})
        for g in guarantees:
            variables.update({g: "boolean"})

        super().__init__(variables=variables,
                         assumptions=assumptions,
                         guarantees=guarantees)
