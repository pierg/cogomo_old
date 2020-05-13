from copy import deepcopy
from typing import Tuple, Union, List

from checks.nusmv import check_satisfiability, check_validity
from checks.tools import And, Implies
from typescogomo.variables import Variables, extract_variable


class LTL:

    def __init__(self, formula: str, variables: Variables = None):
        if (formula == "TRUE" or formula == "FALSE") and variables is None:
            self.__formula: str = formula
            self.__variables: Variables = Variables()
            return

        if formula is not None:

            if variables is None:
                variables = extract_variable(str(formula))

            self.__formula: str = formula
            self.__variables: Variables = variables

            if not self.is_satisfiable():
                raise InconsistentException(self, self)

    @property
    def formula(self) -> str:
        return self.__formula

    @formula.setter
    def formula(self, value: str):
        self.__formula = value

    @property
    def variables(self):
        return self.__variables

    @variables.setter
    def variables(self, value: Variables):
        self.__variables = value

    def negate(self):
        """Modifies the LTL formula with its negation"""
        self.formula = '!(' + self.formula + ')'

    def is_true(self):
        return self.formula == "TRUE"

    def is_satisfiable(self):
        if self.formula is None:
            print("wattt")
        return check_satisfiability(self.variables.get_nusmv_names(), self.formula)

    def conjoin_with(self, others: Union['LTL', List['LTL']]):
        if self.formula == "FALSE":
            return False
        if isinstance(others, LTL):
            if others.formula == "TRUE":
                return True
            if others.formula == "FALSE":
                self.formula = "FALSE"
                self.variables = None
                return True
            if self.formula == "TRUE":
                self.__init__(others.formula, others.variables)
                return True
            others = [others]
        for other in others:
            if self.is_satisfiable_with(other):
                if self.formula == "TRUE":
                    self.formula = deepcopy(other.formula)
                    self.variables = deepcopy(other.variables)
                else:
                    if other.formula == "TRUE":
                        continue
                    if other.formula == "FALSE":
                        self.formula = "FALSE"
                        self.variables = None
                        return True
                    new_formula = deepcopy(self)
                    new_formula.variables.extend(other.variables)
                    new_formula.formula = And([new_formula.formula, other.formula])

                    """If by conjoining other, the result should be a refinement of the existing formula"""
                    if new_formula <= self:
                        self.formula = deepcopy(new_formula.formula)
                        self.variables = deepcopy(new_formula.variables)
            else:
                print(self.formula +"\nINCONSISTENT WITH\n" + other.formula)
                raise InconsistentException(self, other)

        return False

    def is_satisfiable_with(self, other):
        if self.formula == "TRUE" or other.formula == "TRUE":
            return True
        variables = self.variables
        variables.extend(other.variables)
        return check_satisfiability(variables.get_nusmv_names(), [self.formula, other.formula])

    def can_provide_for(self, other):
        """Check if the set of behaviours is smaller or equal in the other set of behaviours but on the types"""
        variables = self.variables + other.variables
        proposition = Implies(self.formula, other.formula)
        for v in variables.list:
            proposition = proposition.replace(v.name, v.port_type)
        return check_validity(variables.get_nusmv_types(), proposition)

    def __str__(self):
        return self.__formula

    def __lt__(self, other: 'LTL'):
        """Check if the set of behaviours is smaller in the other set of behaviours"""
        lt = self <= other
        neq = self != other
        return lt and neq

    def __le__(self, other: 'LTL'):
        """Check if the set of behaviours is smaller or equal in the other set of behaviours"""
        variables_a = set(self.variables.get_nusmv_names())
        variables_b = set(other.variables.get_nusmv_names())
        variables = variables_a | variables_b
        return check_validity(list(variables), "((" + self.formula + ") -> (" + other.formula + "))")

    def __eq__(self, other: 'LTL'):
        """Check if the set of behaviours is equal to the other set of behaviours"""
        if self.formula == other.formula:
            return True
        implied_a = self >= other
        implied_b = self <= other
        return implied_a and implied_b

    def __ne__(self, other: 'LTL'):
        """Check if the set of behaviours is different from the other set of behaviours"""
        return not (self == other)

    def __gt__(self, other: 'LTL'):
        """Check if the set of behaviours is bigger than the other set of behaviours"""
        gt = self >= other
        neq = self != other
        return gt and neq

    def __ge__(self, other: 'LTL'):
        """Check if the set of behaviours is bigger of equal than the other set of behaviours"""
        variables_a = set(self.variables.get_nusmv_names())
        variables_b = set(other.variables.get_nusmv_names())
        variables = variables_a | variables_b
        return check_validity(list(variables), "((" + other.formula + ") -> (" + self.formula + "))")

    def __hash__(self):
        return hash(self.__formula)


class InconsistentException(Exception):

    def __init__(self, conj_a: LTL, conj_b: LTL):

        self.conj_a = conj_a
        self.conj_b = conj_b



def AndLTL(formulas: List[LTL]) -> LTL:
    """Returns an str formula representing the logical AND of list_propoositions"""
    if len(formulas) > 1:
        vars = formulas[0].variables
        for i in range(1, len(formulas)):
            vars += formulas[i].variables
        conj = ' & '.join(s.formula for s in formulas)
        return LTL("(" + conj + ")", vars)
    elif len(formulas) == 1:
        return formulas[0]
    else:
        raise Exception("List of formulas is empty")


def OrLTL(formulas: List[LTL]) -> LTL:
    """Returns an str formula representing the logical OR of list_propoositions"""
    if len(formulas) > 1:
        vars = formulas[0].variables
        for i in range(1, len(formulas)):
            vars += formulas[i].variables
        conj = ' | '.join(s.formula for s in formulas)
        return LTL("(" + conj + ")", vars)
    elif len(formulas) == 1:
        return formulas[0]
    else:
        raise Exception("List of formulas is empty")
