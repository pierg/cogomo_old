from typing import Set

from checks.tools import Implies, And
from typescogomo.subtypes.assumption import Assumption
from typescogomo.formula import LTL
from typescogomo.variables import Variables

USE_SATURATED_GUARANTEES = False


class Guarantee(LTL):

    def __init__(self,
                 formula: str = None,
                 variables: Variables = None,
                 cnf: Set['Guarantee'] = None,
                 saturated: str = None):

        if formula is None and cnf is not None:
            unsat = []
            sat = []
            for g in cnf:
                if not isinstance(g, Guarantee):
                    raise AttributeError
                unsat.append(g.unsaturated)
                sat.append(g.saturated)

            self.__saturated = And(sat)
            self.__unsaturated = And(unsat)

            super().__init__(cnf=cnf)

        if formula is not None and cnf is None:
            if saturated is None:
                self.__unsaturated: str = formula
                self.__saturated = formula
            else:
                self.__unsaturated: str = formula
                self.__saturated: str = saturated

            if USE_SATURATED_GUARANTEES:
                super().__init__(self.__saturated, variables, cnf=None)
            else:
                super().__init__(self.__unsaturated, variables, cnf=None)

        self.__context = None

    @property
    def unsaturated(self) -> str:
        return self.__unsaturated

    @property
    def saturated(self) -> str:
        return self.__saturated

    def saturate_with(self, assumptions: Assumption):
        saturated = Implies(str(assumptions), self.unsaturated)
        self.__init__(self.unsaturated, Variables(self.variables | assumptions.variables), self.cnf, saturated)

    def set_context(self, context):
        self.__context = context
        if USE_SATURATED_GUARANTEES:
            super().__init__("G((" + context + ") -> (" + self.saturated + "))", self.variables, self.cnf)
        else:
            super().__init__("G((" + context + ") -> (" + self.formula + "))", self.variables, self.cnf)
