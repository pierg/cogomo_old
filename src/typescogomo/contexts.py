from typescogomo.assumptions import Assumption
from typescogomo.formulae import LTL
from typescogomo.variables import extract_variable, Variables


class Context(Assumption):

    def __init__(self, scope: 'Scope' = None, formula: str = None, variables: Variables = None):
        if scope is not None:
            super().__init__(scope.formula, scope.variables, kind="context")
        else:
            super().__init__(formula, variables, kind="context")


class Scope(LTL):

    def __init__(self, formula: str):
        variables = extract_variable(str(formula))
        super().__init__(formula, variables)


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
