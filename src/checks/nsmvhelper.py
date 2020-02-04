from typing import Dict, List, Tuple

from src.checks.nusmv import *
from src.helper.logic import *
from src.helper.tools import *


class NonConsistentException(Exception):
    pass


def is_implied_in(variables: Dict[str, str], antecedent: str, consequent: str):
    if consequent == "TRUE":
        return True

    """Check that at least one variables in the consequent is contained in the antecedent"""
    var_antecedent = extract_variables_name([antecedent])
    var_consequent = extract_variables_name([consequent])

    if any(elem in var_antecedent for elem in var_consequent) is False:
        return False

    return check_validity(variables, Implies(antecedent, consequent))


def is_satisfied_in(variables: Dict[str, str], formula_a: str, formula_b: str):
    return check_satisfiability(variables, [formula_a, formula_b])


def add_propositions_to_list(variables: Dict[str, str], where: List[str], what: List[str]):
    """Add the propositions 'what' to the list 'where' if is consistent with the other propositions in 'where'"""

    for p in what:
        add_proposition_to_list(variables, where, p)


def add_proposition_to_list(variables: Dict[str, str], where: List[str], what: str):
    """Add the proposition 'what' to the list 'where' if is consistent with the other propositions in 'where'"""

    where.append(what)

    if not check_satisfiability(variables, where):
        conflict = where.copy()
        where.remove(what)
        print("adding " + what + " resulted in a incompatible contract:\n" + str(conflict))
        raise NonConsistentException


def add_element_to_dict(where: Dict[str, str], what: Dict[str, str]):
    """Add the (key,value) pair in 'what' to 'where' if is consistent with the other elements in 'where'"""

    common_keys = where.keys() & what.keys()

    for k in common_keys:
        if what[k] != what[k]:
            print("Key " + k + " is already present but "
                               "with value " + where[k] + " instead of " + what[k])
            raise NonConsistentException

    where.update(what)


def are_implied_in(list_variables: List[Dict[str, str]], antecedent: List[str], consequent: List[str]):
    """Checks if the conjunction of antecedent is contained in the conjunction of consequent,
    i.e. consequent is a bigger set than antecedent"""

    """Merge Dictionaries"""
    variables = {}
    for v in list_variables:
        variables.update(v)

    """Check Attributes"""
    if isinstance(consequent, list):
        if 'TRUE' in consequent:
            return True
    else:
        raise AttributeError

    if not isinstance(antecedent, list):
        raise AttributeError

    """Check that all the variables in the consequent are contained in the antecedent"""
    var_antecedent = extract_variables_name(antecedent)
    var_consequent = extract_variables_name(consequent)

    if all(elem in var_antecedent for elem in var_consequent) is False:
        return False

    formula = Implies(And(antecedent), And(consequent))
    result = check_validity(variables, formula)

    # if result:
    #     print("\t\t\trefined:\t" + str(And(antecedent)) + "\n\t\t\tabstract:\t" + str(And(consequent)))

    return result
