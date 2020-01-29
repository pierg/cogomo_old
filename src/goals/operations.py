import itertools
from typing import Dict, List, Tuple

from src.components.components import ComponentsLibrary
from src.components.operations import components_selection
from src.goals.cgtgoal import CGTGoal
from src.contracts.operations import *


def compostion(list_of_goal, name=None, description=""):
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


def conjunction(goals, name="", description=""):
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


def mapping(component_library: ComponentsLibrary, specification: CGTGoal,
            name: str = None, description: str = None):
    if name == None:
        name = ""

    if description == None:
        description = ""

    for contract in specification.get_contracts():

        list_of_components = components_selection(component_library, contract)

        composition_contract = compose_contracts(list_of_components)

        composition_goal = CGTGoal(name=name,
                                   description=description,
                                   contracts=[composition_contract])

        goal_list = []
        for component in list_of_components:
            goal_component = CGTGoal(name=component.get_id(),
                                     contracts=[component])
            goal_component.set_parent(composition_goal, "COMPOSITION")

            goal_list.append(goal_component)

        composition_goal.set_subgoals(goal_list, "MAPPING")

        contract.refined_by(composition_contract)

        abstracted_goal = CGTGoal(name=name + "_abstracted",
                                  description=description,
                                  contracts=[contract],
                                  sub_goals=[composition_goal],
                                  sub_operation="REFINEMENT")

        composition_goal.set_parent(abstracted_goal, "ABSTRACTION")

    return abstracted_goal


def create_contextual_cgt(list_of_goals: List[CGTGoal]):
    variables = {}
    contexts = set()

    for goal in list_of_goals:
        var, ctx_1 = goal.get_context()
        if "TRUE" not in ctx_1:
            variables.update(var)
            contexts.add(And(ctx_1))

    contexts = list(contexts)

    ctx_combinations = itertools.combinations(contexts, 2)

    contexts_mutually_exclusive = set()
    """List of contrexts to remove because a refinement has been created"""
    contexts_to_remove = set()

    for ctx_a, ctx_b in ctx_combinations:
        if is_implied_in(variables, ctx_a, ctx_b):
            new_ctx = And([ctx_b, Not(ctx_a)])
            contexts_to_remove.add(ctx_b)
            contexts_mutually_exclusive.add(new_ctx)
            continue
        if is_implied_in(variables, ctx_b, ctx_a):
            new_ctx = And([ctx_a, Not(ctx_b)])
            contexts_to_remove.add(ctx_a)
            contexts_mutually_exclusive.add(new_ctx)
            continue
        contexts_mutually_exclusive.add(ctx_a)
        contexts_mutually_exclusive.add(ctx_b)

    for c in contexts_to_remove:
        if c in contexts_mutually_exclusive:
            contexts_mutually_exclusive.remove(c)

    contexts_mutually_exclusive = list(contexts_mutually_exclusive)

    context_goals: Dict[str, List] = {}

    for ctx in contexts_mutually_exclusive:
        for goal in list_of_goals:

            var, goal_ctx = goal.get_context()
            goal_ctx = And(goal_ctx)

            if is_implied_in(variables, ctx, goal_ctx):
                if ctx in context_goals:
                    if goal not in context_goals[ctx]:
                        context_goals[ctx].append(goal)
                else:
                    context_goals[ctx] = [goal]

    print(contexts_mutually_exclusive)

    composed_goals = []
    for ctx, goals in context_goals.items():
        ctx_goals = compostion(goals, name=ctx + "goals")
        composed_goals.append(ctx_goals)

    cgt = conjunction(composed_goals, name="all_contexts")

    print(cgt)
    print("CIAO")
