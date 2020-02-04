from typing import List


def And(list_propoositions: List[str]) -> str:
    """Returns a string representing the logical AND of list_propoositions"""
    if len(list_propoositions) > 1:
        ret = ""
        for i, elem in enumerate(list_propoositions):
            ret += elem
            if i < len(list_propoositions) - 1:
                ret += " & "
        return ret
    elif len(list_propoositions) == 1:
        return list_propoositions[0]
    else:
        return ""


def Or(list_propoositions):
    """Returns a string representing the logical OR of list_propoositions"""
    if len(list_propoositions) > 1:
        ret = "("
        for i, elem in enumerate(list_propoositions):
            ret += elem
            if i < len(list_propoositions) - 1:
                ret += " | "
        ret += ")"
        return ret
    elif len(list_propoositions) == 1:
        return list_propoositions[0]
    else:
        return ""


def Implies(prop_1, prop_2):
    """Returns a string representing the logical IMPLIES of prop_1 and prop_2"""
    return '(' + prop_1 + ' -> ' + prop_2 + ')'


def Not(prop):
    """Returns a string representing the logical NOT of prop"""
    return '! (' + prop + ')'
