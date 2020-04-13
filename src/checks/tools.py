from typing import List


def And(propositions: List[str]) -> str:
    """Returns an str formula representing the logical AND of list_propoositions"""
    if len(propositions) > 1:
        conj = ' & '.join(propositions)
        return "(" + conj + ")"
    elif len(propositions) == 1:
        return propositions[0]
    else:
        raise Exception("List of propositions is empty")


def Implies(prop_1: str, prop_2: str) -> str:
    """Returns an str formula representing the logical IMPLIES of prop_1 and prop_2"""
    return '((' + prop_1 + ') -> (' + prop_2 + '))'


def Not(prop: str) -> str:
    """Returns an str formula representing the logical NOT of prop"""
    return "!(" + prop + ")"


def Or(propositions: List[str]) -> str:
    """Returns an LTL formula representing the logical OR of list_propoositions"""
    if len(propositions) > 1:
        ret = "("
        for i, elem in enumerate(propositions):
            ret += elem
            if i < len(propositions) - 1:
                ret += " | "
        ret += ")"
        return ret
    elif len(propositions) == 1:
        return propositions[0]
    else:
        raise Exception("List of propositions is empty")
