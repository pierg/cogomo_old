from copy import deepcopy
from typing import List
from src.contracts.contract import Contract


def compose_contracts(contracts: List[Contract]) -> Contract:
    """Composition operation among list of contracts"""

    if len(contracts) == 1:
        return contracts[0]
    if len(contracts) == 0:
        raise Exception("No contract specified in the composition")

    new_contract = deepcopy(contracts[0])

    """Populate the data structure while checking for compatibility and consistency"""
    for contract in contracts[1:]:
        try:
            new_contract.merge_with(contract)
        except Exception as e:
            print("COMPOSITION FAILED")
            raise e

    print("The composition is compatible, consistent and feasible")

    """Removing 'TRUE' from assumptions"""
    for a in list(assumptions):
        if a.formula == 'TRUE':
            assumptions.remove(a)

    assumptions_simplified = assumptions.copy()

    a_simplified = []
    g_ports_used = []

    """For each combination of assumption/guarantees verify if some g_i -> a_i and simplify a_i"""
    for a_elem in assumptions:
        for g_elem in guarantees:
            if g_elem not in g_ports_used and a_elem not in a_simplified:
                if is_included_in(variables, g_elem, a_elem, check_type=True):
                    print("Simplifying assumption " + str(a_elem))
                    assumptions_simplified.remove(a_elem)
                    g_ports_used.append(g_elem)
                    a_simplified.append(a_elem)


    composed_contract = Contract(variables=variables,
                                 assumptions=assumptions_simplified,
                                 guarantees=guarantees,
                                 validate=False,
                                 simplify=False)

    print("Composed contract:")
    print(composed_contract)
    return composed_contract
