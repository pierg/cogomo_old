from typing import Union, List

from checks.tools import And
from typescogomo.formula import LTL, InconsistentException
from typescogomo.assumption import Assumption
from typescogomo.guarantee import Guarantee
from typescogomo.variables import Variables


class LTLs:
    """List of LTL formulae in conjunction with each other"""

    def __init__(self, formulae: List['LTL'], simplify=True):
        "formulae: list of formula to conjoin"

        "LTL formula"
        self.__formula: LTL = None

        "List of LTL formulae in conjunction that it is formed of"
        self.__list: List[LTL] = None


        if len(formulae) == 0:
            self.__formula: LTL = LTL("TRUE")
            self.__list: List[LTL] = []
        else:
            if simplify:
                self.__formula: LTL = LTL(formulae[0].formula, formulae[0].variables)
                self.__list: List[LTL] = [formulae[0]]
                if len(formulae) > 1:
                    try:
                        added_formulae = self.__formula.conjoin_with(formulae[1:])
                        self.list.extend(added_formulae)

                    except InconsistentException as e:
                        raise e

            else:

                variables = Variables()
                formulae_str = []

                for formula in formulae:
                    variables.extend(formula.variables)
                    formulae_str.append(formula.formula)
                try:
                    self.__formula: LTL = LTL(And(formulae_str), variables)
                except InconsistentException as e:
                    raise e

                self.__list: List[LTL] = formulae

    @property
    def list(self):
        return self.__list

    @list.setter
    def list(self, value: List['LTL']):
        if value is not None:

            self.__formula = LTL(value[0].formula, value[0].variables)

            added_formulae = self.__formula.conjoin_with(value[1:])

            self.__list: List[LTL] = added_formulae
        else:
            self.__list = []

    @property
    def formula(self) -> LTL:
        return self.__formula

    @property
    def variables(self):
        return self.formula.variables

    def is_universe(self):
        return self.formula.is_true()

    def are_satisfiable_with(self, other: 'LTLs'):
        return self.formula.is_satisfiable_with(other.formula)

    def extend(self, other: 'LTLs'):
        try:
            self.__formula = LTL(other.list[0].formula, other.list[0].variables)
        except Exception as e:
            print("WHT")
            raise e
        added_formulae = self.__formula.conjoin_with(other.list[1:])
        self.list.extend(added_formulae)

    def add(self, formulae: Union['LTL', List['LTL']]):

        added_formulae = self.formula.conjoin_with(formulae)
        self.list.extend(added_formulae)

    def remove(self, formulae: Union['LTL', List['LTL']]):

        if isinstance(formulae, LTL):
            formulae = [formulae]

        for formula in formulae:
            if formula in self.list:
                self.list.remove(formula)
            else:
                Exception("LTL formula not found, cannot be removed")

        if len(self.list) > 0:
            self.__formula = LTL(self.list[0].formula, self.list[0].variables)
            if len(self.list) > 1:
                self.__formula.conjoin_with(self.list[1:])

        else:
            self.list = None

    def __str__(self):
        return str(self.formula)


class Assumptions(LTLs):
    def __init__(self, assumptions: Union[List[Assumption], Assumption] = None):
        if assumptions is None:
            assumptions = [Assumption("TRUE")]
        if isinstance(assumptions, Assumption):
            assumptions = [assumptions]
        super().__init__(assumptions)

    def remove_kind(self, kind: str):

        for assumption in list(self.list):
            if assumption.kind == kind:
                self.list.remove(assumption)

    def get_kind(self, kind: str):
        ret = []
        for assumption in list(self.list):
            if assumption.kind == kind:
                ret.append(assumption)
        if len(ret) == 0:
            return None
        return ret


class Guarantees(LTLs):
    def __init__(self, guarantees: Union[List[Guarantee], Guarantee] = None):
        if guarantees is None:
            guarantees = [Guarantee("TRUE")]
        if isinstance(guarantees, Guarantee):
            guarantees = [guarantees]
        super().__init__(guarantees)

    def saturate_with(self, assumptions: Assumptions):
        pass
        # for guarantee in self.list:
        #     guarantee.saturate_with(assumptions)
        # super().__init__(self.list)

    def set_context(self, context):
        formulae_str = []

        for g in self.list:
            g.formula = "G((" + context.formula + ") -> " + g.formula + ")"
            g.variables.extend(context.variables)
            formulae_str.append(g.formula)
            self.variables.extend(context.variables)

        self.formula.formula = "G((" + context.formula + ") -> " + self.formula.formula + ")"
        self.formula.variables.extend(context.variables)

