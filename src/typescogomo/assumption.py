from typescogomo.formula import LTL
from typescogomo.variables import Variables

USE_SATURATED_GUARANTEES = False


class Assumption(LTL):

    def __init__(self, formula: str, variables: Variables = None, kind: str = None):
        super().__init__(formula, variables)
        if kind is None:
            self.__kind = "assumed"
        else:
            self.__kind = kind

    @property
    def kind(self) -> str:
        return self.__kind


class Context(Assumption):

    def __init__(self, scope: 'LTL' = None, formula: str = None, variables: Variables = None):
        if scope is not None:
            super().__init__(scope.formula, scope.variables, kind="context")
        else:
            super().__init__(formula, variables, kind="context")


class Expectation(Assumption):

    def __init__(self, formula: str, variables: Variables = None):
        super().__init__(formula, variables, kind="expectation")


class Domain(Assumption):

    def __init__(self, formula: str, variables: Variables = None):
        super().__init__(formula, variables, kind="domain")
