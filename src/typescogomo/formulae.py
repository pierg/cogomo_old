from typing import Tuple, Union

from typescogomo.variables import *


class LTL:

    def __init__(self, formula: str, variables: List[Type] = None):

        self.__formula: str = formula
        self.__variables: List[Type] = variables

        """Wrap the formula in parenthesis if contains an OR"""
        if "|" in self.__formula and \
                not self.__formula.startswith("(") and \
                not self.__formula.endswith(")"):
            self.__formula = f"({formula})"


    @property
    def formula(self) -> str:
        return self.__formula

    @formula.setter
    def formula(self, value):
        self.__formula = value

    @property
    def variables(self):
        return self.__variables

    @variables.setter
    def variables(self, value):
        self.__variables = value

    def get_formula_variable_names(self):
        from helper.tools import extract_terms
        return extract_terms(self)

    def merge_with(self, other: 'LTL'):
        if self.variables is not None and other.variables is not None:
            missing_elements = set(other.variables) - set(self.variables)
            self.variables.extend(list(missing_elements))
            from helper.logic import And
            self.formula = And([self, other])
            print("LTL extended: " + str(self.formula))
        else:
            Exception("None Attributes to LTL formula")

    def get_vars_and_formula(self) -> Tuple[List[Type], 'LTL']:
        return self.__variables, self

    def is_included_in(self, other: 'Context') -> bool:
        from checks.nsmvhelper import are_included_in
        return are_included_in([self.variables, other.variables], [self], [other])

    def is_not_included_in_and_viceversa(self, other: 'Context') -> bool:
        from checks.nsmvhelper import are_included_in
        one = not are_included_in([self.variables, other.variables], [self], [other])
        two = not are_included_in([self.variables, other.variables], [other], [self])
        return one and two

    def is_satisfiable_with(self, other: 'Context') -> bool:
        from checks.nsmvhelper import are_satisfiable
        sat = are_satisfiable([self.variables, other.variables], [other, self])
        return sat

    def __str__(self):
        return self.__formula

    def __eq__(self, other: Union[str, 'LTL']):
        if isinstance(other, str):
            print("WTF")
        if self.variables is None and other.variables is None:
            if isinstance(other, str):
                return self.formula == other
            elif isinstance(other, LTL):
                return self.formula == other.formula
            else:
                raise AttributeError

        if set(self.variables) != set(other.variables):
            return False
        from checks.nsmvhelper import is_included_in
        implied_a = is_included_in(self.variables, self, other)
        implied_b = is_included_in(self.variables, other, self)

        return implied_a and implied_b

    def __hash__(self):
        return hash(self.__formula)

    def __add__(self, other):
        return str(self) + other

    def __radd__(self, other):
        return other + str(self)


class Context(LTL):

    def __init__(self, expression: LTL = None, variables: List[Type] = None):

        if variables is None:
            from helper.tools import extract_terms
            var_names = extract_terms(expression)

            context_vars: List[Type] = []

            try:
                int(var_names[1])
                context_vars.append(BoundedInt(var_names[0]))
            except:
                for var_name in var_names:
                    context_vars.append(Boolean(var_name))

        else:
            context_vars: List[Type] = variables

        super().__init__(str(expression), context_vars)


USE_SATURATED_GUARANTEES = False


class Guarantee(LTL):

    def __init__(self, formula: str, saturated: str = None):
        if saturated is None:
            super().__init__(formula)
            self.__unsaturated: str = formula
            self.__saturated = None
        else:
            self.__unsaturated: str = formula
            self.__saturated: str = saturated
            if USE_SATURATED_GUARANTEES:
                super().__init__(saturated)
            else:
                super().__init__(formula)

    @property
    def unsaturated(self) -> str:
        return self.__unsaturated

    @property
    def saturated(self) -> str:
        return self.__saturated

    def saturate_with(self, assumptions: LTL):
        from helper.logic import Implies
        saturated = str(Implies(assumptions, LTL(self.unsaturated)))
        self.__init__(self.unsaturated, saturated)


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

    def __eq__(self, other: Union[str, 'AP']):
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

    def __init__(self, p: LTL):
        formula = "G({p})".format(p=str(p))
        super().__init__(formula)


class BeforeR(Scope):
    """	F (r) -> (p U r) """

    def __init__(self, p: LTL, r: LTL):
        formula = "(F({r}) -> ({p} U {r}))".format(p=str(p), r=str(r))
        super().__init__(formula)


class UntilR(Scope):
    """	(p U r) """

    def __init__(self, p: LTL, r: LTL):
        formula = "({p} U {r})".format(p=str(p), r=str(r))
        super().__init__(formula)


class WeakUntilR(Scope):
    """	p W r = ((p U r) | G (p)) """

    def __init__(self, p: LTL, r: LTL):
        formula = "(({p} U {r}) | G ({p}))".format(p=str(p), r=str(r))
        super().__init__(formula)


class ReleaseR(Scope):
    """	r R p = p W (r & p) = (p U (r & p) | G (p)) """

    def __init__(self, r: LTL, p: LTL):
        formula = "({p} U ({r} & {p}) | G ({p}))".format(r=str(r), p=str(p))
        super().__init__(formula)


class StrongReleaseR(Scope):
    """	r R p = (p U (r & p)) """

    def __init__(self, r: LTL, p: LTL):
        formula = "({p} U ({r} & {p}))".format(r=str(r), p=str(p))
        super().__init__(formula)


class AfterQ(Scope):
    """	G(q -> G(p)) """

    def __init__(self, p: LTL, q: LTL):
        formula = "(G({q} -> G({p})))".format(p=str(p), q=str(q))
        super().__init__(formula)


class BetweenQandR(Scope):
    """	G((q & !r & F r) -> (p U r)) """

    def __init__(self, p: LTL, q: LTL, r: LTL):
        formula = "(G(({q} & !{r} & F {r}) -> ({p} U {r})))".format(p=str(p), q=str(q), r=str(r))
        super().__init__(formula)


class AfterQuntilR(Scope):
    """	G(q & !r -> ((p U r) | G p)) """

    def __init__(self, p: LTL, q: LTL, r: LTL):
        formula = "(G({q} & !{r} -> (({p} U {r}) | G {p})))".format(p=str(p), q=str(q), r=str(r))
        super().__init__(formula)
