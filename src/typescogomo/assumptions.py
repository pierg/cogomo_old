from typescogomo.formulae import *

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


class Assumptions(LTLs):
    def __init__(self, assumptions: Union[List[Assumption], Assumption] = None):
        if assumptions is None:
            assumptions = [Assumption("TRUE")]
        if isinstance(assumptions, Assumption):
            assumptions = [assumptions]
        super().__init__(assumptions)

    def remove_kind(self, kind: str):

        for assumption in list(self.formulae):
            if assumption.kind == kind:
                self.formulae.remove(assumption)
