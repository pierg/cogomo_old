from typing import Set, Union
from checks.tools import Implies, And, Not, Or
from typescogomo.subtypes.assumption import Assumption
from typescogomo.formula import LTL
from typescogomo.variables import Variables

USE_SATURATED_GUARANTEES = False


class Guarantee(LTL):

    def __init__(self,
                 formula: str = None,
                 variables: Variables = None,
                 cnf: Set['LTL'] = None,
                 saturated: str = None):

        if formula is None and cnf is not None:
            formulae = []
            for g in cnf:
                if not isinstance(g, LTL):
                    raise AttributeError
                formulae.append(g.formula)

            self.__saturated = And(formulae)
            self.__unsaturated = And(formulae)

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

    def __and__(self, other: 'LTL') -> Union['Guarantee', 'LTL']:
        """self & other
        Returns a new LTL that is the conjunction of self with other"""
        if isinstance(other, Guarantee):
            return Guarantee(cnf={self, other})
        else:
            return LTL(cnf={self, other})

    def __or__(self, other: 'LTL') -> Union['Guarantee', 'LTL']:
        """self | other
        Returns a new LTL that is the disjunction of self with other"""
        if isinstance(other, Guarantee):
            return Guarantee(
                formula=Or([self.formula, other.formula]),
                variables=Variables(self.variables | other.variables)
            )
        else:
            return LTL(
                formula=Or([self.formula, other.formula]),
                variables=Variables(self.variables | other.variables)
            )

    def __invert__(self) -> 'Guarantee':
        """~ self
        Returns a new LTL that is the negation of self"""
        return Guarantee(
            formula=Not(self.formula),
            variables=self.variables
        )

    def __rshift__(self, other: 'LTL') -> Union['Guarantee', 'LTL']:
        """>> self
        Returns a new LTL that is the result of self -> other (implies)"""
        if isinstance(other, Guarantee):
            return Guarantee(
                formula=Implies(self.formula, other.formula),
                variables=Variables(self.variables | other.variables)
            )
        else:
            return LTL(
                formula=Implies(self.formula, other.formula),
                variables=Variables(self.variables | other.variables)
            )

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
            super().__init__("G((" + context.formula + ") -> (" + self.saturated + "))",
                             Variables(self.variables | context.variables))
        else:
            super().__init__("G((" + context.formula + ") -> (" + self.formula + "))",
                             Variables(self.variables | context.variables))
