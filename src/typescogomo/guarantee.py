from copy import deepcopy

from checks.tools import Implies
from typescogomo.formula import LTL
from typescogomo.variables import Variables

USE_SATURATED_GUARANTEES = True


class Guarantee(LTL):

    def __init__(self,
                 formula: str,
                 variables: Variables = None,
                 saturated: str = None):
        if saturated is None:
            super().__init__(formula, variables)
            self.__unsaturated: str = formula
            self.__saturated: str = formula
        else:
            self.__unsaturated: str = formula
            self.__saturated: str = saturated
            if USE_SATURATED_GUARANTEES:
                super().__init__(saturated, variables)
            else:
                super().__init__(formula, variables)
    @property
    def unsaturated(self) -> str:
        return self.__unsaturated

    @property
    def saturated(self) -> str:
        return self.__saturated

    def saturate_with(self, assumptions):
        new_vars = deepcopy(self.variables)
        new_vars.extend(assumptions.variables)
        saturated = Implies(str(assumptions.formula), self.unsaturated)
        self.__init__(self.unsaturated, new_vars, saturated)