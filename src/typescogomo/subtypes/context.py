from typing import Set, Union
from typescogomo.formula import LTL
from typescogomo.variables import Variables
from checks.tools import Implies, And, Not, Or


class Context(LTL):

    def __init__(self,
                 formula: str = None,
                 variables: Variables = None,
                 cnf: Set['LTL'] = None):
        super().__init__(formula, variables, cnf)

    def __and__(self, other: 'LTL') -> Union['Context', 'LTL']:
        """self & other
        Returns a new LTL that is the conjunction of self with other"""
        if isinstance(other, Context):
            return Context(cnf={self, other})
        else:
            return LTL(cnf={self, other})

    def __or__(self, other: 'LTL') -> Union['Context', 'LTL']:
        """self | other
        Returns a new LTL that is the disjunction of self with other"""
        if isinstance(other, Context):
            return Context(
                formula=Or([self.formula, other.formula]),
                variables=Variables(self.variables | other.variables)
            )
        else:
            return LTL(
                formula=Or([self.formula, other.formula]),
                variables=Variables(self.variables | other.variables)
            )

    def __invert__(self) -> 'Context':
        """~ self
        Returns a new LTL that is the negation of self"""
        return Context(
            formula=Not(self.formula),
            variables=self.variables
        )

    def __rshift__(self, other: 'LTL') -> Union['Context', 'LTL']:
        """>> self
        Returns a new LTL that is the result of self -> other (implies)"""
        if isinstance(other, Context):
            return Context(
                formula=Implies(self.formula, other.formula),
                variables=Variables(self.variables | other.variables)
            )
        else:
            return LTL(
                formula=Implies(self.formula, other.formula),
                variables=Variables(self.variables | other.variables)
            )
