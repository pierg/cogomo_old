from typing import Tuple

from src.contracts.contract import Contract
from src.checks.nsmvhelper import *
import itertools as it


def compose_contracts(contracts: List[Contract]) -> Contract:
    """Composition operation among list of contracts"""

    """Variables of the resulting contract"""
    variables: Dict[str, str] = {}

    """Assumptions of the resulting contract"""
    assumptions: List[str] = []

    """Guarantees of the resulting contract"""
    guarantees: List[str] = []

    """Unsaturated guarantees of the resulting contract"""
    unsaturated_guarantees: List[str] = []

    """Populate the data structure while checking for compatibility and consistency"""
    for contract in contracts:
        try:
            add_element_to_dict(variables, contract.variables)
            add_propositions_to_list(variables, assumptions, contract.assumptions)
            add_propositions_to_list(variables, guarantees, contract.guarantees)
            add_propositions_to_list(variables, unsaturated_guarantees, contract.unsaturated_guarantees)
        except NonConsistentException:
            print("Composition is not doable")
            raise NonConsistentException

    """Remove 'TRUE' from assumptions if exists"""
    if "TRUE" in assumptions:
        assumptions.remove("TRUE")

    """Check for feasibility"""
    if not check_satisfiability(variables, assumptions + guarantees):
        raise Exception("Composition not feasible:\n" + str(assumptions + guarantees))

    print("The composition is compatible, consistent and feasible. Composing now...")

    assumptions_simplified = assumptions.copy()

    """Combinations of guarantees"""
    g_combinations = []
    for i in range(len(unsaturated_guarantees)):
        oc = it.combinations(unsaturated_guarantees, i + 1)
        for c in oc:
            g_combinations.append(list(c))

    """Combinations of assumptions"""
    a_combinations = []
    for i in range(len(assumptions)):
        oc = it.combinations(assumptions, i + 1)
        for c in oc:
            a_combinations.append(list(c))

    """For each possible combination of assumption/guarantees verify if some g_i -> a_i and simplify a_i"""
    for a_elem in assumptions:
        for g_elem in unsaturated_guarantees:
            if is_implied_in(variables, g_elem, a_elem):
                print("Simplifying assumption " + str(a_elem))
                if isinstance(a_elem, list):
                    for a in a_elem:
                        if a in assumptions_simplified:
                            assumptions_simplified.remove(a)

    # """For each possible combination of assumption/guarantees verify if some g_i -> a_i and simplify a_i"""
    # for a_elem in a_combinations:
    #     for g_elem in g_combinations:
    #
    #         """Avoid comparing things that have already been removed"""
    #         if isinstance(a_elem, list):
    #             flag = False
    #             for a in a_elem:
    #                 if a not in assumptions_simplified:
    #                     flag = True
    #             if flag:
    #                 continue
    #
    #         if are_implied_in([variables], g_elem, a_elem):
    #             print("Simplifying assumption " + str(a_elem))
    #             if isinstance(a_elem, list):
    #                 for a in a_elem:
    #                     if a in assumptions_simplified:
    #                         assumptions_simplified.remove(a)

    """Delete unused variables"""
    var_names = []
    var_names.extend(extract_variables_name(assumptions_simplified))
    var_names.extend(extract_variables_name(guarantees))
    var_names = list(set(var_names))

    try:
        variables_filtered = {var: variables[var] for var in var_names}
        composed_contract = Contract(variables=variables_filtered,
                                     assumptions=assumptions_simplified,
                                     guarantees=unsaturated_guarantees,
                                     saturated=guarantees,
                                     validate=False,
                                     simplify=False)
        print("Composed contract:")
        print(composed_contract)
        return composed_contract

    except Exception as e:
        print(str(e))
