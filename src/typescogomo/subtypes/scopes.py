from typing import Set, Union

from z3 import Or

from checks.tools import Not, Implies
from typescogomo.formula import LTL
from typescogomo.variables import Variables


class Scope(LTL):

    def __init__(self, formula: str = None, variables: Variables = None, cnf: Set['Pattern'] = None):
        super().__init__(formula, variables, cnf)

    def __and__(self, other: 'LTL') -> Union['Scope', 'LTL']:
        """self & other
        Returns a new LTL that is the conjunction of self with other"""
        if isinstance(other, Scope):
            return Scope(cnf={self, other})
        else:
            return LTL(cnf={self, other})

    def __or__(self, other: 'LTL') -> Union['Scope', 'LTL']:
        """self | other
        Returns a new LTL that is the disjunction of self with other"""
        if isinstance(other, Scope):
            return Scope(
                formula=Or([self.formula, other.formula]),
                variables=Variables(self.variables | other.variables)
            )
        else:
            return LTL(
                formula=Or([self.formula, other.formula]),
                variables=Variables(self.variables | other.variables)
            )

    def __invert__(self) -> 'Scope':
        """~ self
        Returns a new LTL that is the negation of self"""
        return Scope(
            formula=Not(self.formula),
            variables=self.variables
        )

    def __rshift__(self, other: 'LTL') -> Union['Scope', 'LTL']:
        """>> self
        Returns a new LTL that is the result of self -> other (implies)"""
        if isinstance(other, Scope):
            return Scope(
                formula=Implies(self.formula, other.formula),
                variables=Variables(self.variables | other.variables)
            )
        else:
            return LTL(
                formula=Implies(self.formula, other.formula),
                variables=Variables(self.variables | other.variables)
            )


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


"""Scopes for the property 'P becomes true' defined by Dwyer"""


class FP_global(Scope):
    """F p"""

    def __init__(self, p: LTL):
        formula = "F({p})".format(p=p.formula)
        super().__init__(formula)


class FP_before_R(Scope):
    """	F (r) -> (!r U p) """

    def __init__(self, p: LTL, r: LTL):
        formula = "(F({r}) -> (!{r} U {p}))".format(p=p.formula, r=r.formula)
        super().__init__(formula)


class FP_after_Q(Scope):
    """	G(!q) | F((q) & F (p)) """

    def __init__(self, p: LTL, q: LTL):
        formula = "(G(!{q}) | F(({q}) & F ({p})))".format(p=p.formula, q=q.formula)
        super().__init__(formula)


class FP_between_Q_and_R(Scope):
    """	G((q & F(r)) -> (!(r) U (p))) """

    def __init__(self, p: LTL, q: LTL, r: LTL):
        formula = "(G(({q} & F({r})) -> (!({r}) U ({p}))))".format(p=p.formula, q=q.formula, r=r.formula)
        super().__init__(formula)


class FP_after_Q_until_R(Scope):
    """	G((q) -> (!(r) U (p))) """

    def __init__(self, p: LTL, q: LTL, r: LTL):
        formula = "(G(({q}) -> (!({r}) U ({p}))))".format(p=p.formula, q=q.formula, r=r.formula)
        super().__init__(formula)


"""Recurrence pattern"""


class Recurrence_P_between_Q_and_R(Scope):
    """G((q & ! r & F r) -> ((F(p | r)) U r))"""

    def __init__(self, p: LTL, q: LTL, r: LTL):
        formula = "(G(({q} & ! {r} & F {r}) -> ((F({p} | {r})) U {r})))".format(p=p.formula, q=q.formula, r=r.formula)
        super().__init__(formula)


class Recurrence_P_after_Q_until_R(Scope):
    """G((q & ! r) -> ((F(p | r)) U r))"""

    def __init__(self, p: LTL, q: LTL, r: LTL):
        formula = "(G(({q} & ! {r}) -> (((F({p} | {r})) U {r}) | G((F({p} | {r}))))))".format(p=p.formula, q=q.formula,
                                                                                              r=r.formula)
        super().__init__(formula)


class Recurrence_P_after_Q_until_R_fixed(Scope):
    """G((q & ! r & F r) -> (F(p) U r))"""

    def __init__(self, p: LTL, q: LTL, r: LTL):
        formula = "(G(({q} & ! {r} & F {r}) -> (F({p}) U {r})))".format(p=p.formula, q=q.formula, r=r.formula)
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


"""Other pattern found"""


class P_exist_before_R(Scope):
    """	!r W (p & !r) = (!r U (p & !r)) | G (!r) """

    def __init__(self, p: LTL, r: LTL):
        formula = "((!{r} U ({p} & !{r})) | G (!{r}))".format(r=r.formula, p=p.formula)
        super().__init__(formula)


class Absense_P_between_Q_and_R(Scope):
    """ G((q & !r & F r) -> (!p U r))"""

    def __init__(self, p: LTL, r: LTL, q: LTL):
        formula = "(G(({q} & !{r} & F {r}) -> (!{p} U {r})))".format(q=q.formula, r=r.formula, p=p.formula)
        super().__init__(formula)


class Existence_P_between_Q_and_R(Scope):
    """ G(q & !r -> (!r W (p & !r))) = G(q & !r -> ((!r U (p & !r)) | G(!r)))"""

    def __init__(self, p: LTL, r: LTL, q: LTL):
        formula = "(G({q} & !{r} -> ((!{r} U ({p} & !{r})) | G(!{r}))))".format(q=q.formula, r=r.formula, p=p.formula)
        super().__init__(formula)


class S_responds_to_P_before_R(Scope):
    """F r -> (p -> (!r U (s & !r))) U r"""

    def __init__(self, p: LTL, r: LTL, s: LTL):
        formula = "(F {r} -> ({p} -> (!{r} U ({s} & !{r}))) U {r})".format(s=s.formula, r=r.formula, p=p.formula)
        super().__init__(formula)


class S_precedes_P(Scope):
    """!p W s = (!p U s) | G (!p) """

    def __init__(self, p: LTL, s: LTL):
        formula = "((!{p} U {s}) | G (!{p}))".format(s=s.formula, p=p.formula)
        super().__init__(formula)
