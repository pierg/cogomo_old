from src.checks.nsmvhelper import *

def incomposable_check(list_contracts):
    """Return True if the list of contracts is not satisfiable, not compatible or not feasible"""
    if not isinstance(list_contracts, list):
        raise Exception("Wrong Parameter")

    variables = []
    propositions = set([])

    for contract in list_contracts:
        variables.extend(contract.variables)
        for elem in contract.assumptions:
            propositions.add(elem)
        for elem in contract.guarantees:
            propositions.add(elem)

    return not check_satisfiability(variables, list(propositions))


def duplicate_contract(list_contracts):
    if not isinstance(list_contracts, list):
        raise Exception("Wrong Parameter")

    return len(list_contracts) != len(set(list_contracts))
