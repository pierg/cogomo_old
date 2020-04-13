from checks.tools import Implies
from typescogomo.assumptions import Assumptions
from typescogomo.formulae import *

USE_SATURATED_GUARANTEES = False


class Guarantee(LTL):

    def __init__(self,
                 formula: str,
                 variables: Variables = None,
                 saturated: str = None):
        if saturated is None:
            super().__init__(formula, variables)
            self.__unsaturated: str = formula
            self.__saturated = None
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

    def saturate_with(self, assumptions: Assumptions):
        saturated = Implies(str(assumptions.formula), self.unsaturated)
        self.__init__(self.unsaturated, self.variables, saturated)


class Guarantees(LTLs):
    def __init__(self, guarantees: Union[List[Guarantee], Guarantee] = None):
        if guarantees is None:
            guarantees = [Guarantee("TRUE")]
        if isinstance(guarantees, Guarantee):
            guarantees = [guarantees]
        super().__init__(guarantees)

    def saturate_with(self, assumptions: Assumptions):
        for guarantee in self.list:
            guarantee.saturate_with(assumptions)
        super().__init__(self.list)
