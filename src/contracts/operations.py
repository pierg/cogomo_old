from copy import deepcopy
from typing import List
from src.contracts.contract import Contract, InconsistentContracts, IncompatibleContracts, UnfeasibleContracts
from typescogomo.subtypes.assumption import Assumption


def compose_contracts(contracts: List[Contract]) -> Contract:
    """Composition operation among list of contracts"""

    if len(contracts) == 1:
        return contracts[0]
    if len(contracts) == 0:
        raise Exception("No contract specified in the composition")

    new_contract = deepcopy(contracts[0])

    c1_a = deepcopy(contracts[0].assumptions.cnf)

    assumptions = Assumption(cnf=deepcopy(contracts[0].assumptions.cnf))

    new_contract = Contract()


    """Populate the data structure while checking for compatibility and consistency"""
    for contract in contracts[1:]:
        try:
            new_contract.merge_with(contract)
        except InconsistentContracts as e:
            print("Contracts inconsistent")
            raise e
        except IncompatibleContracts as e:
            print("Contracts incompatible")
            raise e
        except UnfeasibleContracts as e:
            print("Contracts unfeasible")
            raise e

    print("The composition is compatible, consistent and feasible")

    a_removed = []
    g_used = []

    """For each combination of assumption/guarantees verify if some g_i -> a_i and simplify a_i"""
    for a_elem in list(new_contract.assumptions.cnf):
        for g_elem in list(new_contract.guarantees.cnf):
            if g_elem not in g_used and a_elem not in a_removed:
                if g_elem <= a_elem:
                    print("Simplifying assumption " + str(a_elem))
                    new_contract.assumptions.remove(a_elem)
                    g_used.append(g_elem)
                    a_removed.append(a_elem)

    print("Composed contract:")
    print(new_contract)
    return new_contract
