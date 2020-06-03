from typing import Set
from typescogomo.formula import LTL
from typescogomo.variables import Variables


class Context(LTL):

    def __init__(self,
                 formula: str = None,
                 variables: Variables = None,
                 cnf: Set['LTL'] = None):
        super().__init__(formula, variables, cnf)

