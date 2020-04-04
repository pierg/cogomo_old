from typing import List, Tuple

from contracts.formulas import *
from contracts.types import *
from src.helper.tools import extract_terms
from src.checks.nsmvhelper import *


class Context:

    def __init__(self,
                 expression: LTL = None,
                 variables: List[Type] = None):

        var_names = extract_terms(expression)

        if variables is None:

            self.__variables: List[Type] = []

            try:
                int(var_names[1])
                self.__variables.append(BoundedInt(var_names[0]))
            except:
                for var_name in var_names:
                    self.__variables.append(Boolean(var_name))

        else:
            self.__variables: List[Type] = variables

        self.__formula: LTL = expression

    @property
    def variables(self):
        return self.__variables

    @variables.setter
    def variables(self, value):
        self.__variables = value

    @property
    def formula(self):
        return self.__formula

    @formula.setter
    def formula(self, value):
        self.__formula = value

    def merge_with(self, other: 'Context'):
        missing_elements = set(other.variables) - set(self.variables)
        self.variables.extend(list(missing_elements))
        self.formula = And([self.formula, other.formula])
        print("context extended: " + str(self.formula))


    def get_context(self) -> Tuple[List[Type], LTL]:
        return self.__variables, self.__formula

    def is_included_in(self, other: 'Context') -> bool:
        return is_smaller_set_than([self.variables, other.variables],
                                   [self.formula],
                                   [other.formula])

    def is_not_included_in_and_viceversa(self, other: 'Context') -> bool:
        one = not is_smaller_set_than([self.variables, other.variables],
                                      [self.formula],
                                      [other.formula])
        two = not is_smaller_set_than([self.variables, other.variables],
                                      [other.formula],
                                      [self.formula])

        return one and two

    def is_satisfiable_with(self, other: 'Context') -> bool:

        sat = are_satisfiable([self.variables, other.variables],
                              [other.formula, self.formula])
        return sat

    def __str__(self):
        return str(self.__formula)

    def __eq__(self, other):
        if set(self.variables) != set(other.variables):
            return False

        implied_a = includes(self.variables, self.formula, other.formula)
        implied_b = includes(self.variables, self.formula, other.formula)

        return implied_a and implied_b

    def __hash__(self):
        return hash(self.__formula)



def get_smallest_context(contexts: List[Context]):
    smallest = contexts[0]

    for context in contexts:
        if context is not smallest and \
                is_smaller_set_than([smallest.variables, context.variables],
                                    [context.formula], [smallest.formula]):
            smallest = context

    return smallest
