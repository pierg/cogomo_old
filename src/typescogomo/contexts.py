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
        super().__init__(formula)


"""Scopes for the property 'P is true' defined by Dwyer"""


class P_global(Scope):
    """G p"""

    def __init__(self, p: LTL):
        formula = "G({p})".format(p=p.formula)
        super().__init__(formula)


class P_before_R(Scope):
    """	F (r) -> (p U r) """

    def __init__(self, p: LTL, r: LTL):
        formula = "(F({r}) -> ({p} U {r}))".format(p=p.formula, r=r.formula)
        super().__init__(formula)


class P_after_Q(Scope):
    """	G(q -> G(p)) """

    def __init__(self, p: LTL, q: LTL):
        formula = "(G({q} -> G({p})))".format(p=p.formula, q=q.formula)
        super().__init__(formula)


class P_between_Q_and_R(Scope):
    """	G((q & !r & F r) -> (p U r)) """
    def __init__(self, p: LTL, q: LTL, r: LTL):
        formula = "(G(({q} & !{r} & F {r}) -> ({p} U {r})))".format(p=p.formula, q=q.formula, r=r.formula)
        super().__init__(formula)


class P_after_Q_until_R(Scope):
    """	G(q & !r -> ((p U r) | G p)) """

    def __init__(self, p: LTL, q: LTL, r: LTL):
        formula = "(G({q} & !{r} -> (({p} U {r}) | G {p})))".format(p=p.formula, q=q.formula, r=r.formula)
        super().__init__(formula)


"""Other patterns defined"""


class P_until_R(Scope):
    """	(p U r) """

    def __init__(self, p: LTL, r: LTL):
        formula = "({p} U {r})".format(p=p.formula, r=r.formula)
        super().__init__(formula)


class P_weakuntil_R(Scope):
    """	p W r = ((p U r) | G (p)) """

    def __init__(self, p: LTL, r: LTL):
        formula = "(({p} U {r}) | G ({p}))".format(p=p.formula, r=r.formula)
        super().__init__(formula)


class P_release_R(Scope):
    """	p R r = !(!p U !r) """

    def __init__(self, p: LTL, r: LTL):
        formula = "!(!{p} U !{r})".format(r=r.formula, p=p.formula)
        super().__init__(formula)


class P_strongrelease_R(Scope):
    """	p M r = ¬(¬p W ¬r) = r U (p & r) """

    def __init__(self, p: LTL, r: LTL):
        formula = "({r} U ({p} & {r}))".format(r=r.formula, p=p.formula)
        super().__init__(formula)
