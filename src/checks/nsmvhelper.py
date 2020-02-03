from typing import Dict, List

from src.checks.nusmv import *
from src.helper.logic import *
from src.helper.tools import *


def is_implied_in(variables: Dict[str, str], formula_a: str, formula_b: str):
    if formula_b == "TRUE":
        return True

    """Check that at least all the variables in the abstracted are contained in the refined"""
    var_refined = extract_variables_name([formula_a])
    var_abstracted = extract_variables_name([formula_b])

    for va in var_abstracted:
        contained = False
        for vr in var_refined:
            if va == vr:
                contained = True
                continue
        if contained is False:
            return False

    return check_validity(variables, Implies(formula_a, formula_b))


def is_satisfied_in(variables: Dict[str, str], formula_a: str, formula_b: str):
    return check_satisfiability(variables, [formula_a, formula_b])


def are_implied_in(list_variables: List[Dict[str, str]], props_refined: List[str], props_abstracted: List[str]):
    """Checks if the conjunction of props_refined is contained in the conjunction of props_abstracted,
    i.e. props_abstracted is a bigger set than props_refined"""

    """Merge Dictionaries"""
    variables = {}
    for v in list_variables:
        variables.update(v)

    """Check Attributes"""
    if isinstance(props_abstracted, list):
        if 'TRUE' in props_abstracted:
            return True
    else:
        raise AttributeError

    if not isinstance(props_refined, list):
        raise AttributeError

    """Check that at least all the variables in the abstracted are contained in the refined"""

    var_refined = extract_variables_name(props_refined)
    var_abstracted = extract_variables_name(props_abstracted)

    for va in var_abstracted:
        contained = False
        for vr in var_refined:
            if va == vr:
                contained = True
                continue
        if contained is False:
            print("\tThe abstract contracts has propositions involving more variables")
            return False

    formula = Implies(And(props_refined), And(props_abstracted))
    print("checking validity of " + formula)
    result = check_validity(variables, formula)

    if result:
        print("\t\t\trefined:\t" + str(And(props_refined)) + "\n\t\t\tabstract:\t" + str(And(props_abstracted)))

    return result
