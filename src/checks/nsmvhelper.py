from typing import Dict

from src.checks.nusmv import *
from src.helper.logic import *


def is_implied_in(variables: Dict[str, str], formula_a: str, formula_b: str):

    return check_validity(variables, Implies(formula_a, formula_b))


def is_satisfied_in(variables: Dict[str, str], formula_a: str, formula_b: str):

    return check_satisfiability(variables, [formula_a, formula_b])


def is_set_smaller_or_equal(variables_refined, variables_abstracted, props_refined, props_abstracted):
    """
    Checks if the conjunction of props_refined is contained in the conjunction of props_abstracted, i.e. prop_2 is a bigger set
    :param props_refined: single proposition or list of propositions
    :param props_abstracted: single proposition or list of propositions
    :return: True if prop_1 is a refinement of prop_2
    """

    refinement = None
    abstract = None

    """Check Attributes"""
    if isinstance(props_refined, list):
        if len(props_refined) == 1:
            refinement = props_refined[0]
        else:
            refinement = And(props_refined)
    elif isinstance(props_refined, str):
        refinement = props_refined

    if isinstance(props_abstracted, list):
        if 'TRUE' in props_abstracted:
            return True
        if len(props_abstracted) == 1:
            abstract = props_abstracted[0]
        else:
            abstract = And(props_abstracted)
    elif isinstance(props_abstracted, str):
        if props_abstracted is 'TRUE':
            return True
        abstract = props_abstracted

    """Check port compatibility"""
    if check_ports_are_compatible(list(variables_refined.keys()), list(variables_abstracted.keys())) is False:
        return False

    """Merging the two dictionaries"""
    all_variables = variables_abstracted.copy()
    all_variables.update(variables_refined)

    result = check_validity(all_variables, Implies(refinement, abstract))

    if result:
        print("\t\t\trefined:\t" + str(refinement) + "\n\t\t\tabstract:\t" + str(abstract))

    return result


def check_ports_are_compatible(prop_1_names, prop_2_names):
    """Returns True if the two propositions or list of propositions share at least one port (variable)"""

    if not isinstance(prop_1_names, list):
        prop_1_names = [prop_1_names]

    if not isinstance(prop_2_names, list):
        prop_2_names = [prop_2_names]

    for var_names_1 in prop_1_names:
        for var_names_2 in prop_2_names:
            if var_names_1 == var_names_2:
                return True
    return False