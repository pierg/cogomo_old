from typescogomo.formulae import Guarantee, Assumption
from src.contracts.contract import Contract
from src.checks.nsmvhelper import *


def compose_contracts(contracts: List[Contract]) -> Contract:
    """Composition operation among list of contracts"""

    if len(contracts) == 1:
        return contracts[0]
    if len(contracts) == 0:
        raise Exception("No contract specified in the composition")

    """Variables of the resulting contract"""
    variables: List[Type] = []

    """Assumptions of the resulting contract"""
    assumptions: List[Assumption] = []

    """Guarantees of the resulting contract"""
    guarantees: List[Guarantee] = []

    """Populate the data structure while checking for compatibility and consistency"""
    for contract in contracts:
        try:
            add_variables_to_list(variables, contract.variables)
            add_propositions_to_list(variables, assumptions, contract.assumptions, simplify=False)
            add_propositions_to_list(variables, guarantees, contract.guarantees, simplify=False)
        except NonConsistentException:
            print("Composition is not doable")
            raise NonConsistentException

    """Check for feasibility"""
    if not check_satisfiability(variables, assumptions + guarantees):
        raise Exception("Composition not feasible:\n" + str(assumptions + guarantees))

    print("The composition is compatible, consistent and feasible. Composing now...")

    """Removing Duplicates"""
    guarantees = list(set(guarantees))
    assumptions = list(set(assumptions))

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
