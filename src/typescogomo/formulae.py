from typing import Tuple, Union, List

from checks.nusmv import check_satisfiability, check_validity
from checks.tools import And
from typescogomo.variables import Variables


class IconsistentException(Exception):
    pass

class LTL:

    def __init__(self, formula: str, variables: Variables):
        self.__formula: str = formula
        self.__variables: Variables = variables

        """Wrap the formula in parenthesis if contains an OR"""
        if "|" in self.__formula and \
                not self.__formula.startswith("(") and \
                not self.__formula.endswith(")"):
            self.__formula = f"({formula})"

        if not formula == "TRUE":
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

    def is_satisfiable(self):
        return check_satisfiability(self.variables.get_list_str(), self.formula)

    def conjoin_with(self, others: Union['LTL', List['LTL']]):
        if isinstance(others, LTL):
            others = [others]
        for other in others:
            if self.is_satisfiable_with(other):
                self.variables.extend(other.variables)
                self.formula = And([self.formula, other.formula])
            else:
                raise IconsistentException("Conjunction not satisfiable:\n" + str(self) + "\nWITH\n" + str(other))

    def is_satisfiable_with(self, other):
        if self.formula == "TRUE" or other.formula == "TRUE":
            return True
        variables = self.variables.get_list_str()
        variables.extend(other.variables.get_list_str())
        return check_satisfiability(variables, [self.formula, other.formula])

    def __str__(self):
        return self.__formula

    def __lt__(self, other: 'LTL'):
        """Check if the set of behaviours is smaller in the other set of behaviours"""
        lt = self <= other
        neq = self != other
        return lt and neq

    def __le__(self, other: 'LTL'):
        """Check if the set of behaviours is smaller or equal in the other set of behaviours"""
        return check_validity(self.variables.get_list_str(), "((" + self.formula + ") -> (" + other.formula + "))")

    def __eq__(self, other: 'LTL'):
        """Check if the set of behaviours is equal to the other set of behaviours"""
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
        return check_validity(self.variables.get_list_str(), "((" + other.formula + ") -> (" + self.formula + "))")

    def __hash__(self):
        return hash(self.__formula)


class LTLs:
    """List of LTL formulae in conjunction with each other"""

    def __init__(self, formulae: List['LTL']):

        self.__formula : LTL = LTL(formulae[0].formula, formulae[0].variables)

        if len(formulae) > 1:
            self.__formula.conjoin_with(formulae[1:])

        self.__formulae: List[LTL] = formulae


    @property
    def formulae(self):
        return self.__formulae

    @formulae.setter
    def formulae(self, value: List['LTL']):
        self.__formula = LTL(value[0].formula, value[0].variables)

        self.__formula.conjoin_with(value[1:])

        self.__formulae: List[LTL] = value

    @property
    def formula(self) -> LTL:
        return self.__formula

    @property
    def variables(self):
        return self.formula.variables

    def are_satisfiable_with(self, other: 'LTLs'):
        return self.formula.is_satisfiable_with(other.formula)

    def extend(self, other: 'LTLs'):
        self.__formula = LTL(other.formulae[0].formula, other.formulae[0].variables)
        self.__formula.conjoin_with(other.formulae[1:])
        self.formulae.extend(other.formulae)


    def add(self, formulae: Union['LTL', List['LTL']]):

        self.formula.conjoin_with(formulae)

        if isinstance(formulae, LTL):
            self.formulae.append(formulae)
        else:
            self.formulae.extend(formulae)

    def remove(self, formulae: Union['LTL', List['LTL']]):

        if isinstance(formulae, LTL):
            formulae = [formulae]

        for formula in formulae:
            if formula in self.formulae:
                self.formulae.remove(formula)
            else:
                Exception("LTL formula not found, cannot be removed")

        if len(self.formulae) > 0:
            self.__formula = LTL(self.formulae[0].formula, self.formulae[0].variables)
            if len(self.formulae) > 1:
                self.__formula.conjoin_with(self.formulae[1:])
        else:
            self.formulae = None

