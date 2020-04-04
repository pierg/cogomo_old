from contracts.formulas import Assumption
from src.checks.nusmv import *
from src.helper.logic import *
from src.helper.tools import *


class NonConsistentException(Exception):
    pass


def get_smallest_set(variables: List[Type], formulas: List[LTL]):
    smallest = formulas[0]

    for formula in formulas:
        if formula is not smallest and \
                includes(variables, formula, smallest):
            smallest = formula

    return smallest


def are_satisfiable(list_variables: List[List[Type]], propositions: List[LTL]):
    """Merge Lists"""
    variables = []
    for list_vars in list_variables:
        add_variables_to_list(variables, list_vars)

    """Check Attributes"""
    if not isinstance(propositions, list):
        raise AttributeError

    return check_satisfiability(variables, propositions)


def is_smaller_set_than(list_variables: List[List[Type]],
                        antecedent: List[LTL],
                        consequent: List[LTL],
                        check_type: bool = False):
    """Checks if the conjunction of antecedent and conjunction of consequent:
    antecedent implies consequent == antecedent is a smaller set of the consequent ==
    antecedent is contained in the consequent"""

    """Merge Lists"""
    variables = []
    for list_vars in list_variables:
        add_variables_to_list(variables, list_vars)

    """Check Attributes"""
    if not isinstance(consequent, list):
        raise AttributeError

    if not isinstance(antecedent, list):
        raise AttributeError

    return includes(variables, And(antecedent), And(consequent), check_type)


def includes(variables: List[Type],
             antecedent: LTL,
             consequent: LTL,
             check_type: bool = False):
    """Check if:
    antecedent implies consequent == antecedent is a smaller set of the consequent ==
    antecedent is contained in the consequent"""

    if consequent.formula == "TRUE":
        return True

    """Check that at least one type of variables in the consequent is contained in the antecedent"""
    types_antecedent = extract_variables_types(variables, antecedent)
    types_consequent = extract_variables_types(variables, consequent)

    if any(elem in types_antecedent for elem in types_consequent) is False:
        return False

    return check_validity(variables, Implies(antecedent, consequent), check_type)


def are_satisfied_in(list_variables: List[List[Type]],
                     propositions: List[List[LTL]]):
    """satisfiability check"""

    """Merge Lists"""
    variables = []
    for list_vars in list_variables:
        add_variables_to_list(variables, list_vars)

    propositions_list = []
    for list_propositions in propositions:
        propositions_list.extend(list_propositions)

    result = check_satisfiability(variables, propositions_list)

    return result


def add_propositions_to_list(variables: List[Type],
                             where: List[LTL],
                             what: List[LTL], simplify=True):
    """Add the propositions 'what' to the list 'where' if is consistent with the other propositions in 'where'"""

    for p in what:
        add_proposition_to_list(variables, where, p, simplify)


def add_proposition_to_list(variables: List[Type],
                            where: List[LTL],
                            what: LTL, simplify=True):
    """Add the proposition 'what' to the list 'where' if is consistent with the other propositions in 'where'
    also simplifies if a proposition is already included in the list"""

    if what == 'TRUE':
        return

    if what in where:
        return

    """Check if assumption is a abstraction of existing assumptions and vice-versa"""
    if simplify:
        for p in where:

            if includes(variables, p, what):
                where.remove(p)

            elif includes(variables, what, p):
                return

    where.append(what)

    if not check_satisfiability(variables, where):
        conflict = And(where.copy())
        where.remove(what)
        print("adding " + str(what) + " resulted in a incompatible contract:\n" + str(conflict))
        raise NonConsistentException


def add_variables_to_list(where: List[Type], what: List[Type]):
    """Add all the elements in 'what' to 'where' if is consistent with the other elements in 'where'"""

    for v in what:
        add_variable_to_list(where, v)


def add_variable_to_list(where: List[Type], what: Type):
    """Add 'what' to 'where' if is consistent with the other elements in 'where'"""

    for elem in where:
        if elem.name == what.name:
            type_a = type(what).__name__
            type_b = type(elem).__name__
            if type_a != type_b:
                print("Variable " + str(what) + " is already present but "
                                                "is of tyoe " + type_a + " instead of " + type_b)
                raise NonConsistentException
            else:
                return
    where.append(what)
