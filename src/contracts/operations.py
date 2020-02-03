from typing import Tuple

from src.contracts.contract import Contract
from src.checks.nsmvhelper import *
import itertools as it


def compose_contracts(contracts: List[Contract]) -> Contract:
    """Composition operation among list of contracts"""

    contract_composition = Contract()

    if not isinstance(contracts, list):
        raise Exception("Wrong Parameters")

    """Variables of the resulting contract"""
    variables: Dict[str, str] = {}

    """Assumptions of the resulting contract"""
    assumptions: List[str] = []

    """Guarantees of the resulting contract"""
    guarantees: List[str] = []

    """Unsaturated guarantees"""
    unsaturated_guarantees: List[str] = []

    contract_composition = Contract()

    for contract in contracts:
        for v, t in contract.variables.items():
            if v in variables.keys():
                if variables[v] != t:
                    raise Exception("Variables Incompatible: \n" + \
                                    v + ": " + variables[v] + "\n" + \
                                    v + ": " + t)
        variables.update(contract.variables)
        assumptions.extend(contract.assumptions)
        guarantees.extend(contract.guarantees)
        guarantees_saturated.extend(contract.get_list_guarantees_saturated())

    """Remove 'TRUE' from assumptions if exists"""
    if "TRUE" in assumptions:
        assumptions.remove("TRUE")

    assumptions_guarantees = assumptions.copy()
    assumptions_guarantees.extend(guarantees_saturated)

    """Checking Feasibility, Compatibility and Consistency"""
    satis = check_satisfiability(variables, list(set(assumptions_guarantees)))
    if not satis:
        print("The composition is unfeasible")

        satis = check_satisfiability(variables, list(set(assumptions)))
        if not satis:
            print(str(list(set(assumptions))))
            print("The composition is unfeasible")

        satis = check_satisfiability(variables, list(set(guarantees_saturated)))
        if not satis:
            print(str(list(set(guarantees_saturated))))
            print("The composition is inconsistent")

        raise Exception("Not composable")

    print("The composition is compatible, consistent and satisfiable. Composing now...")

    a_composition = list(set(assumptions))
    g_composition = list(set(guarantees))
    g_composition_saturated = list(set(guarantees_saturated))

    a_composition_simplified = a_composition[:]

    # List of guarantees used to simpolify assumptions, used later for abstraction
    g_elem_list = []
    # Compare each element in a_composition with each element in g_composition

    """Combinations of guarantees"""
    g_combinations = []
    for i in range(len(g_composition)):
        oc = it.combinations(g_composition, i + 1)
        for c in oc:
            g_combinations.append(list(c))

    """Combinations of assumptions"""
    a_combinations = []
    for i in range(len(a_composition)):
        oc = it.combinations(a_composition, i + 1)
        for c in oc:
            a_combinations.append(list(c))

    for a_elem in a_combinations:
        for g_elem in g_combinations:

            """Avoid comparing things that have already been removed"""
            if isinstance(a_elem, list):
                flag = False
                for a in a_elem:
                    if a not in a_composition_simplified:
                        flag = True
                if flag:
                    continue
            else:
                if a_elem not in a_composition_simplified:
                    continue

            if are_implied_in([variables], g_elem, a_elem):
                print("Simplifying assumption " + str(a_elem))
                if isinstance(a_elem, list):
                    for a in a_elem:
                        if a in a_composition_simplified:
                            a_composition_simplified.remove(a)
                else:
                    if a_elem in a_composition_simplified:
                        a_composition_simplified.remove(a_elem)
                g_elem_list.append(g_elem)

    """Delete unused variables"""
    var_names = []
    var_names.extend(extract_variables_name(a_composition_simplified))
    var_names.extend(extract_variables_name(g_composition))
    var_names = list(set(var_names))

    try:
        variables_filtered = {var: variables[var] for var in var_names}
        composed_contract = Contract(variables=variables_filtered,
                                     assumptions=a_composition_simplified,
                                     guarantees=g_composition)

        return composed_contract

    except Exception as e:
        print(str(e))
        return None
