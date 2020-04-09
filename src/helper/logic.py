from copy import copy
from typing import List
from typescogomo.formulae import LTL


def And(propositions: List[LTL]) -> LTL:
    """Returns an LTL formula representing the logical AND of list_propoositions"""
    if len(propositions) > 1:
        new_proposition = copy(propositions[0])
        ret = ""
        for i, elem in enumerate(propositions):
            ret += elem.formula
            if i < len(propositions) - 1:
                ret += " & "
        new_proposition.formula = ret
        return new_proposition
    elif len(propositions) == 1:
        return propositions[0]
    else:
        raise Exception("List of propositions is empty")


def Or(propositions: List[LTL]) -> LTL:
    """Returns an LTL formula representing the logical OR of list_propoositions"""
    if len(propositions) > 1:
        ret = "("
        for i, elem in enumerate(propositions):
            ret += elem.formula
            if i < len(propositions) - 1:
                ret += " | "
        ret += ")"
        return LTL(formula=ret)
    elif len(propositions) == 1:
        return propositions[0]
    else:
        raise Exception("List of propositions is empty")


def Implies(prop_1: LTL, prop_2: LTL) -> LTL:
    """Returns an LTL formula representing the logical IMPLIES of prop_1 and prop_2"""
    return LTL(formula='((' + prop_1.formula + ') -> (' + prop_2.formula + '))')


def Not(prop: LTL, brakets=True) -> LTL:
    """Returns an LTL formula representing the logical NOT of prop"""
    if brakets:
        return LTL(formula='!(' + prop.formula + ')')
    return LTL(formula='!' + prop.formula + '')
