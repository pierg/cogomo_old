from typing import List
from contracts.types import *
from src.helper.tools import extract_terms


class Context:

    def __init__(self,
                 expression: str = None):

        var_names = extract_terms(expression)

        self.__variables: List[Type] = []

        try:
            int(var_names[1])
            self.__variables.append(BoundedInt(var_names[0]))
        except:
            self.__variables.append(Boolean(var_names[0]))
            self.__variables.append(Boolean(var_names[1]))

        self.__formulas: List[str] = [expression]

    @property
    def variables(self):
        return self.__variables

    @variables.setter
    def variables(self, value):
        self.__variables = value

    @property
    def formulas(self):
        return self.__formulas

    @formulas.setter
    def formulas(self, value):
        self.__formulas = value

    def get_context(self):
        return self.__variables, self.__formulas

    def __str__(self, level=0):
        return self.__formulas
