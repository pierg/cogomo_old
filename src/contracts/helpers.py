from itertools import combinations
from src.contracts.contract import *

def incomposable_check(list_contracts: List[Contract]):
    """Return True if the list of contracts is not consistent, not compatible or not feasible"""
    if not isinstance(list_contracts, list):
        raise Exception("Wrong Parameter")

    for ca, cb in combinations(list_contracts, 2):
        if not ca.assumptions.are_satisfiable_with(cb.assumptions):
            return True
        if not ca.guarantees.are_satisfiable_with(cb.guarantees):
            return True
        if not ca.assumptions.are_satisfiable_with(cb.guarantees):
            return True

    return False