from copy import deepcopy
from typing import Tuple, Union, List

from checks.nusmv import check_satisfiability, check_validity
from checks.tools import And, Implies
from typescogomo.variables import Variables, extract_variable


class IconsistentException(Exception):
    pass


class LTL:

    def __init__(self, formula: str, variables: Variables = None):
        if (formula == "TRUE" or formula == "FALSE") and variables is None:
            self.__formula: str = formula
            self.__variables: Variables = Variables()
            return

        if variables is None:
            variables = extract_variable(str(formula))

        self.__formula: str = formula
        self.__variables: Variables = variables

        if not self.is_satisfiable:
            raise IconsistentException("The formula is not satisfiable:\n" + self.formula)

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
                        return True
            else:
                raise IconsistentException("Conjunction not satisfiable:\n" + str(self) + "\nWITH\n" + str(other))

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


class LTLs:
    """List of LTL formulae in conjunction with each other"""

    def __init__(self, formulae: List['LTL']):

        if len(formulae) == 0:
            self.__formula: LTL = LTL("TRUE")
            self.__list: List[LTL] = []

        else:
            if formulae[0].formula == "TRUE":
                self.__formula: LTL = LTL("TRUE")
            else:
                self.__formula: LTL = LTL(formulae[0].formula, formulae[0].variables)

                if len(formulae) > 1:
                    self.__formula.conjoin_with(formulae[1:])

            self.__list: List[LTL] = formulae

    @property
    def list(self):
        return self.__list

    @list.setter
    def list(self, value: List['LTL']):
        self.__formula = LTL(value[0].formula, value[0].variables)

        self.__formula.conjoin_with(value[1:])

        self.__list: List[LTL] = value

    @property
    def formula(self) -> LTL:
        return self.__formula

    @property
    def variables(self):
        return self.formula.variables

    def is_universe(self):
        return self.formula.is_true()

    def are_satisfiable_with(self, other: 'LTLs'):
        return self.formula.is_satisfiable_with(other.formula)

    def extend(self, other: 'LTLs'):
        self.__formula = LTL(other.list[0].formula, other.list[0].variables)
        self.__formula.conjoin_with(other.list[1:])
        self.list.extend(other.list)

    def add(self, formulae: Union['LTL', List['LTL']]):

        res = self.formula.conjoin_with(formulae)

        if res:
            for e in list(self.list):
                if e.formula == "TRUE":
                    self.list.remove(e)
            if isinstance(formulae, list):
                self.list.extend(formulae)
            else:
                self.list.append(formulae)

    def remove(self, formulae: Union['LTL', List['LTL']]):

        if isinstance(formulae, LTL):
            formulae = [formulae]

        for formula in formulae:
            if formula in self.list:
                self.list.remove(formula)
            else:
                Exception("LTL formula not found, cannot be removed")

        if len(self.list) > 0:
            self.__formula = LTL(self.list[0].formula, self.list[0].variables)
            if len(self.list) > 1:
                self.__formula.conjoin_with(self.list[1:])
        else:
            self.list = None

    def __str__(self):
        return str(self.formula)
