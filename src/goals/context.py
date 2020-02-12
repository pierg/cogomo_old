from typing import List, Tuple

from contracts.formulas import LTL
from contracts.types import *
from src.helper.tools import extract_terms
from src.checks.nsmvhelper import *


class Context:

    def __init__(self,
                 expression: LTL = None):

        var_names = extract_terms(expression)

        self.__variables: List[Type] = []

        try:
            int(var_names[1])
            self.__variables.append(BoundedInt(var_names[0]))
        except:
            for var_name in var_names:
                self.__variables.append(Boolean(var_name))

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

    def get_context(self) -> Tuple[List[Type], LTL]:
        return self.__variables, self.__formula

    def is_not_included_in_and_viceversa(self, other: 'Context') -> bool:
        one = not are_implied_in([self.variables, other.variables],
                                 [self.formula],
                                 [other.formula])
        two = not are_implied_in([self.variables, other.variables],
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
        return str(self.formula) == str(other.formula)


def get_smallest_cotext(contexts: List[Context]):
    smallest = contexts[0]

    for context in contexts:
        if context is not smallest and \
                are_implied_in([smallest.variables, context.variables],
                               [context.formula], [smallest.formula]):
            smallest = context

    return smallest
