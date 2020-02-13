from typing import Union


class LTL:

    def __init__(self, formula: str):
        super().__init__()
        self.__formula: str = formula

        """Wrap the formula in parenthesis if contains an OR"""
        if "|" in self.__formula and\
                not self.__formula.startswith("(") and \
                not self.__formula.endswith(")"):
            self.__formula = f"({formula})"

    @property
    def formula(self) -> str:
        return self.__formula

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

