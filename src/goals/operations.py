import copy
import itertools
from typing import Dict, List, Tuple

from src.components.components import ComponentsLibrary
from src.components.operations import components_selection
from src.goals.cgtgoal import CGTGoal
from src.contracts.operations import *


def composition(list_of_goal: List[CGTGoal],
                name: str = None,
                description: str = "",
                parent_goal: CGTGoal = None):
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


    if parent_goal is not None:
        parent_goal.update(
            name=name,
            description=description,
            contracts=composed_contract_list,
            sub_goals=list_of_goal,
            sub_operation="COMPOSITION"
        )
        # Connecting children to the parent
        for goal in list_of_goal:
            goal.connect_to(parent_goal, "CONJUNCTION")
        return parent_goal

    composed_goal = CGTGoal(name=name,
                            description=description,
                            contracts=composed_contract_list,
                            refined_by=list_of_goal,
                            refined_with="COMPOSITION")

    # Connecting children to the parent
    for goal in list_of_goal:
        goal.connect_to(composed_goal, "COMPOSITION")

    return composed_goal


def conjunction(list_of_goals: List[CGTGoal],
                name: str = None,
                description: str = None,
                parent_goal: CGTGoal = None) -> CGTGoal:
    """Conjunction Operations among the goals in list_of_goals.
       It returns a new goal"""

    """For each contract pair, checks the consistency of the guarantees among the goals that have common assumptions"""
    for pair_of_goals in it.combinations(list_of_goals, r=2):

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

    for goal in list_of_goals:
        contracts = goal.get_contracts()
        for contract in contracts:
            new_contract = copy.deepcopy(contract)
            list_of_new_contracts.append(new_contract)

    if parent_goal is not None:
        parent_goal.update(
            name=name,
            description=description,
            contracts=list_of_new_contracts,
            sub_goals=list_of_goals,
            sub_operation="CONJUNCTION"
        )
        # Connecting children to the parent
        for goal in list_of_goals:
            goal.connect_to(parent_goal, "CONJUNCTION")
        return parent_goal

    # Creating a new Goal parent
    conjoined_goal = CGTGoal(name=name,
                             description=description,
                             contracts=list_of_new_contracts,
                             refined_by=list_of_goals,
                             refined_with="CONJUNCTION")

    # Connecting children to the parent
    for goal in list_of_goals:
        goal.connect_to(conjoined_goal, "CONJUNCTION")

    return conjoined_goal


def mapping(component_library: ComponentsLibrary, specification_goal: CGTGoal, name: str = None,
            description: str = None):
    """Given a component library and a specification returns the a goal that is the result
    of the composition of a selection of component in the library and that refined the specification
    after having propagated the assumptions"""

    if name is None:
        name = ""

    if description is None:
        description = ""

    if len(specification_goal.get_contracts()) == 1:
        specification = specification_goal.get_contracts()[0]
    else:
        raise Exception("The goal has multiple contracts in conjunction and cannot be mapped")

    """Get a list of components from the specification, greedy algorithm"""
    list_of_components = components_selection(component_library, specification)

    if len(list_of_components) == 0:
        raise Exception("No mapping possible. There is no component available in the library")

    """Compose the components"""
    composition_contract = compose_contracts(list_of_components)

    """Create a goal for each component"""
    list_of_components_goals = []
    for component in list_of_components:
        goal_component = CGTGoal(name=component.get_id(),
                                 contracts=[component])
        list_of_components_goals.append(goal_component)

    """Create a top level goal 'composition_goal' and link it to the 'list_of_components_goals'"""
    composition_goal = CGTGoal(name=name,
                               description=description,
                               contracts=[composition_contract],
                               refined_by=list_of_components_goals,
                               refined_with="MAPPING")

    # """Create a goal for each component"""
    # list_of_components_goals = []
    # for component in list_of_components:
    #     goal_component = CGTGoal(name=component.get_id(),
    #                              contracts=[component])
    #     goal_component.set_parent(composition_goal, "COMPOSITION")
    #
    #     list_of_components_goals.append(goal_component)
    #
    # composition_goal.set_subgoals(list_of_components_goals, "MAPPING")

    """Propagate the assumptions to the specification and check the refinement"""
    specification.propagate_assumptions_from(composition_contract)
    specification.is_refined_by(composition_contract)

    """Link 'composition_goal' to the 'specification_goal'"""
    specification_goal.refine_by([composition_goal], "REFINEMENT")

    """Connect the abstracted and refined goals"""
    composition_goal.connect_to(specification_goal, "ABSTRACTION")

    """Consolidate the tree from 'specification_goal' to the top"""
    # consolidate(specification_goal)


def consolidate(cgt: CGTGoal):
    """It recursivly re-perfom composition and conjunction operations up to the rood node"""
    if cgt.get_parent() is not None:
        parent = cgt.get_parent()
        if parent.get_sub_operation() == "CONJUNCTION":
            conjunction(
                parent.get_sub_goals(),
                parent.get_name(),
                parent.get_description(),
                parent
            )

        elif parent.get_sub_operation() == "COMPOSITION":
            composition(
                parent.get_sub_goals(),
                parent.get_name(),
                parent.get_description(),
                parent,
            )
        consolidate(parent)
    else:
        return


def create_contextual_cgt(list_of_goals: List[CGTGoal]) -> CGTGoal:
    """Returns a CGT from a list of goals based on the contexts of each goal"""

    variables = {}
    contexts = set()

    """Extract all the contexts"""
    for goal in list_of_goals:
        var, ctx_1 = goal.get_context()
        if "TRUE" not in ctx_1:
            variables.update(var)
            contexts.add(And(ctx_1))

    contexts = list(contexts)

    if len(contexts) == 1:
        cgt = composition(list_of_goals, name=contexts[0] + "goals")
        return cgt

    ctx_combinations = itertools.combinations(contexts, 2)

    contexts_mutually_exclusive = set()

    """List of contexts to remove because a refinement has been created"""
    contexts_to_remove = set()

    """Identifies all the mutually exclusive contexts"""
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

    """Identifies the goals enabled for each mutually exclusive context"""
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

    """Compose the goal in each mutually exclusive context"""
    composed_goals = []
    for ctx, goals in context_goals.items():
        ctx_goals = composition(goals, name=ctx + "goals")
        composed_goals.append(ctx_goals)

    """Conjoin the goals across all the mutually exclusive contexts"""
    cgt = conjunction(composed_goals, name="all_contexts")

    return cgt
