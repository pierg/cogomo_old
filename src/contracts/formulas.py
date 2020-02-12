
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


if __name__ == '__main__':
    a1 = Assumption("a_1")

    g1 = Guarantee("g1")

    g2 = Guarantee("g1", saturated="XXX -> g1")


    print(a1)
    print(a1.kind)
    print(g1)
    print(g1.saturated)
    print(g2)
    print(g2.saturated)

