from typing import Union


class LTL:

    def __init__(self, formula: str):
        self.__formula: str = formula

        """Wrap the formula in parenthesis if contains an OR"""
        if "|" in self.__formula and \
                not self.__formula.startswith("(") and \
                not self.__formula.endswith(")"):
            self.__formula = f"({formula})"

    @property
    def formula(self) -> str:
        return self.__formula\

    @formula.setter
    def formula(self, value):
        self.__formula = value

    def __str__(self):
        return self.__formula

    def __eq__(self, other: Union[str, 'LTL']):
        if isinstance(other, str):
            return self.formula == other
        elif isinstance(other, LTL):
            return self.formula == other.formula
        else:
            raise AttributeError

    def __hash__(self):
        return hash(self.__formula)


class Guarantee(LTL):

    def __init__(self, formula: str, saturated: str = None):
        super().__init__(formula)
        if saturated is None:
            self.__saturated: str = formula
        else:
            self.__saturated: str = saturated

    @property
    def saturated(self) -> str:
        return self.__saturated


class Assumption(LTL):

    def __init__(self, formula: str, kind: str = None):
        super().__init__(formula)
        if kind is None:
            self.__kind = "assumed"
        else:
            self.__kind = kind

    @property
    def kind(self) -> str:
        return self.__kind


class AP:
    """Atomic Proposition"""

    def __init__(self, ap: str):
        self.__ap: str = ap

    @property
    def ap(self) -> str:
        return self.__ap

    def __str__(self):
        return self.__ap

    def __eq__(self, other: Union[str, 'LTL']):
        if isinstance(other, str):
            return self.ap == other
        elif isinstance(other, AP):
            return self.ap == other.ap
        else:
            raise AttributeError

    def __hash__(self):
        return hash(self.__ap)


class Scope(LTL):

    def __init__(self, formula: str):
        super().__init__(formula)


class Always(Scope):
    """G p"""

    def __init__(self, p: AP):
        formula = "G({p})".format(p=str(p))
        super().__init__(formula)


class BeforeR(Scope):
    """	F (r) -> (p U r) """

    def __init__(self, p: AP, r: AP):
        formula = "(F({r}) -> ({p} U {r}))".format(p=str(p), r=str(r))
        super().__init__(formula)


class AfterQ(Scope):
    """	G(q -> G(p)) """

    def __init__(self, p: AP, q: AP):
        formula = "(G({q} -> G({p})))".format(p=str(p), q=str(q))
        super().__init__(formula)


class BetweenQandR(Scope):
    """	G((q & !r & F r) -> (p U r)) """

    def __init__(self, p: AP, q: AP, r: AP):
        formula = "(G(({q} & !{r} & F {r}) -> ({p} U {r})))".format(p=str(p), q=str(q), r=str(r))
        super().__init__(formula)


class AfterQuntilR(Scope):
    """	G(q & !r -> ((p U r) | G p)) """

    def __init__(self, p: AP, q: AP, r: AP):
        formula = "(G({q} & !{r} -> (({p} U {r}) | G {p})))".format(p=str(p), q=str(q), r=str(r))
        super().__init__(formula)
