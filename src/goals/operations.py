from src.goals.cgtgoal import CGTGoal
from src.contracts.operations import *

import itertools as it

import copy


def compose_goals(list_of_goal, name=None, description=""):
    contracts = {}

    for goal in list_of_goal:
        contracts[goal.get_name()] = goal.get_contracts()

    if name is None:
        name = '_'.join("{!s}".format(key) for (key, val) in list(contracts.items()))

    """List of Lists of Contract, 
    each element of the list is a list with the contracts in conjunctions, 
    and each element is in composition with the other elements"""

    contracts_dictionary = {}
    for goal in list_of_goal:
        contracts_dictionary[goal.get_name()] = goal.get_contracts()

    composition_contracts = (dict(list(zip(contracts, x))) for x in it.product(*iter(contracts.values())))

    composed_contract_list = []
    for contracts in composition_contracts:
        # composed_contract = compose_contracts(contracts)
        contract_list = list(contracts.values())
        composed_contract = compose_contracts(contract_list)
        composed_contract_list.append(composed_contract)

    composed_goal = CGTGoal(name=name,
                            description=description,
                            contracts=composed_contract_list,
                            sub_goals=list_of_goal,
                            sub_operation="COMPOSITION")

    # Connecting children to the parent
    for goal in list_of_goal:
        goal.set_parent(composed_goal, "COMPOSITION")

    return composed_goal


def conjoin_goals(goals, name="", description=""):
    """For each contract pair, checks the consistency of the guarantees among the goals that have common assumptions"""
    for pair_of_goals in it.combinations(goals, r=2):

        assumptions_set = []
        guarantees_set = []

        for contract_1 in pair_of_goals[0].get_contracts():

            assumptions_set.extend(contract_1.get_list_assumptions())

            guarantees_set.extend(contract_1.get_list_guarantees())

            for contract_2 in pair_of_goals[1].get_contracts():

                variables = contract_1.get_variables().copy()

                variables.update(contract_2.get_variables())

                assumptions_set.extend(contract_2.get_list_assumptions())

                guarantees_set.extend(contract_2.get_list_guarantees())

                """Checking Consistency only when the assumptions are satisfied together"""
                sat = check_satisfiability(variables, list(set(assumptions_set)))
                if sat:
                    """Checking Consistency only when the assumptions are satisfied together"""
                    sat = check_satisfiability(variables, list(set(guarantees_set)))
                    if not sat:
                        print("The assumptions in the conjunction of contracts are not mutually exclusive")
                        raise Exception("Conjunction Failed")

    print("The conjunction satisfiable.")

    # Creating new list of contracts
    list_of_new_contracts = []

    for goal in goals:
        contracts = goal.get_contracts()
        for contract in contracts:
            new_contract = copy.deepcopy(contract)
            list_of_new_contracts.append(new_contract)

    # Creating a new Goal parent
    conjoined_goal = CGTGoal(name=name,
                             description=description,
                             contracts=list_of_new_contracts,
                             sub_goals=goals,
                             sub_operation="CONJUNCTION")

    # Connecting children to the parent
    for goal in goals:
        goal.set_parent(conjoined_goal, "CONJUNCTION")

    return conjoined_goal


def prioritize_goal(first_priority_goal, second_priority_goal):
    """
    Makes the assumption of one goal dependent on the satisfiability of the assumptions of the second goal
    :param first_priority_goal:
    :param second_priority_goal:
    :return: lower priority goal
    """

    variables = {}
    stronger_assumptions_list = []

    for contract in first_priority_goal.get_contracts():
        variables.update(contract.get_variables())
        stronger_assumptions_list.append(And(contract.get_list_assumptions()))

    for contract in second_priority_goal.get_contracts():
        contract.merge_variables(variables)
        contract.add_assumption(Not(Or(stronger_assumptions_list)))


def mapping_to_goal(list_of_components, name=None, description=None, abstract_on=None):
    if not isinstance(list_of_components, list):
        raise AttributeError

    if name == None:
        name = ""

    if description == None:
        description = ""

    composition_contract = compose_contracts(list_of_components, abstract_on=abstract_on)
    new_goal = CGTGoal(name=name,
                       description=description,
                       contracts=[composition_contract])

    goal_list = []
    for component in list_of_components:
        goal_component = CGTGoal(name=component.get_id(),
                                 contracts=[component])
        goal_component.set_parent(new_goal, "COMPOSITION")

        goal_list.append(goal_component)

    new_goal.set_subgoals(goal_list, "MAPPING")

    return new_goal


def propagate_assumptions(abstract_goal, refined_goal):
    """

    :return:
    """
    contracts_refined = refined_goal.get_contracts()
    contracts_abstracted = abstract_goal.get_contracts()

    if len(contracts_refined) != len(contracts_abstracted):
        raise Exception("Propagating assumptions among goals with different number of conjoined contracts")

    for i, contract in enumerate(contracts_refined):
        """And(.....) of all the assumptions of the abstracted contract"""
        assumptions_abs_ltl = contracts_abstracted[i].get_ltl_assumptions()
        """List of all the assumptions of the refined contract"""
        assumptions_ref = contract.get_list_assumptions()
        assumptions_to_add = []
        for assumption in assumptions_ref:
            if not is_set_smaller_or_equal(assumptions_abs_ltl, assumption):
                assumptions_to_add.append(assumption)

        """Unify alphabets"""
        contracts_abstracted[i].merge_variables(contract.get_variables())
        contracts_abstracted[i].add_assumptions(assumptions_to_add)
