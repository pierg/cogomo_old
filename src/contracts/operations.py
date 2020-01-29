from src.contracts.contract import Contract
from src.checks.nsmvhelper import *
import itertools as it


def is_refinement_correct(refined_contract, abstracted_contract, counterexample=False):
    """
    Check if A1 >= A2 and if G1 <= G2
    """

    a_check = is_set_smaller_or_equal(refined_contract.get_variables(), abstracted_contract.get_variables(),
                                      abstracted_contract.get_list_assumptions(),
                                      refined_contract.get_list_assumptions())

    g_check = is_set_smaller_or_equal(abstracted_contract.get_variables(), refined_contract.get_variables(),
                                      refined_contract.get_list_guarantees(), abstracted_contract.get_list_guarantees())

    return a_check and g_check


def compose_contracts(contracts):
    """
    :param contracts: list of goals name and contract
    :return: True, contract which is the composition of the contracts in the goals or the contracts in the list
             False, unsat core of smt, list of proposition to fix that cause a conflict when composing
    """

    if not isinstance(contracts, list):
        raise Exception("Wrong Parameters")

    g_abstracted = None
    if abstract_on is not None:
        g_abstracted = abstract_on.get_list_guarantees()

    variables = {}
    assumptions = []
    guarantees = []
    guarantees_saturated = []

    for contract in contracts:
        variables.update(contract.get_variables())
        assumptions.extend(contract.get_list_assumptions())
        guarantees.extend(contract.get_list_guarantees())
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

            if is_set_smaller_or_equal(variables, variables, g_elem, a_elem):
                print("Simplifying assumption " + str(a_elem))
                if isinstance(a_elem, list):
                    for a in a_elem:
                        if a in a_composition_simplified:
                            a_composition_simplified.remove(a)
                else:
                    if a_elem in a_composition_simplified:
                        a_composition_simplified.remove(a_elem)
                g_elem_list.append(g_elem)

    if len(a_composition_simplified) == 0:
        a_composition_simplified.append("TRUE")


    composed_contract = Contract(variables=variables,
                                 assumptions=a_composition_simplified,
                                 guarantees=g_composition)

    return composed_contract


def incomposable_check(list_contracts):
    """Return True if the list of contracts is not satisfiable, not compatible or not feasible"""
    if not isinstance(list_contracts, list):
        raise Exception("Wrong Parameter")

    variables = {}
    propositions = set([])

    for contract in list_contracts:
        variables.update(contract.get_variables())
        for elem in contract.get_list_assumptions():
            propositions.add(elem)
        for elem in contract.get_list_guarantees():
            propositions.add(elem)

    return not check_satisfiability(variables, list(propositions))


def duplicate_contract(list_contracts):
    if not isinstance(list_contracts, list):
        raise Exception("Wrong Parameter")

    return len(list_contracts) != len(set(list_contracts))
