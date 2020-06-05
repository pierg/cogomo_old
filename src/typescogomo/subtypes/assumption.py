from typing import Set

from checks.tools import Or, Implies, Not
from typescogomo.formula import LTL
from typescogomo.variables import Variables


class Assumption(LTL):

    def __init__(self,
                 formula: str = None,
                 variables: Variables = None,
                 cnf: Set['LTL'] = None,
                 kind: str = None):
        super().__init__(formula, variables, cnf)
        if kind is None:
            self.__kind = "assumed"
        else:
            self.__kind = kind


    def __and__(self, other: 'Assumption'):
        """self & other
        Returns a new LTL that is the conjunction of self with other"""
        if not isinstance(other, Assumption):
            return AttributeError
        return Assumption(
            cnf={self, other}
        )

    def __or__(self, other):
        """self | other
        Returns a new LTL that is the disjunction of self with other"""
        if not isinstance(other, Assumption):
            return AttributeError
        return Assumption(
            formula=Or([self.formula, other.formula]),
            variables=Variables(self.variables | other.variables)
        )

    def __neg__(self):
        """~ self
        Returns a new LTL that is the negation of self"""
        return Assumption(
            formula=Not(self.formula),
            variables=self.variables
        )

    def __rshift__(self, other):
        """>> self
        Returns a new LTL that is the result of self -> other (implies)"""
        if not isinstance(other, Assumption):
            return AttributeError
        return Assumption(
            formula=Implies(self.formula, other.formula),
            variables=Variables(self.variables | other.variables)
        )

    @property
    def kind(self) -> str:
        return self.__kind

    def remove_kind(self, kind: str):

        for assumption in self.cnf:
            if isinstance(assumption, Assumption):
                if assumption.kind == kind:
                    self.cnf.remove(assumption)

        super().__init__(cnf=self.cnf)

    def get_kind(self, kind: str):
        ret = []
        for assumption in self.cnf:
            if isinstance(assumption, Assumption):
                if assumption.kind == kind:
                    ret.append(assumption)
        if len(ret) == 0:
            return None
        return ret


class Expectation(Assumption):

    def __init__(self,
                 formula: str = None,
                 variables: Variables = None,
                 cnf: Set['Expectation'] = None):
        super().__init__(formula, variables, cnf, kind="expectation")


class Domain(Assumption):

    def __init__(self,
                 formula: str = None,
                 variables: Variables = None,
                 cnf: Set['Domain'] = None):
        super().__init__(formula, variables, cnf, kind="domain")

# class Context(Assumption):
#
#     def __init__(self, scope: 'LTL' = None, formula: str = None, variables: Variables = None):
#         if scope is not None:
#             super().__init__(scope.formula, scope.variables, kind="context")
#         else:
#             super().__init__(formula, variables, kind="context")
#
