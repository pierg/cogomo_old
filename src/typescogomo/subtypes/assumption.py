from typing import Set
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
