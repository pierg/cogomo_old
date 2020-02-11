import copy
import itertools
from typing import Dict, List, Tuple, Set

from goals.context import Context
from goals.helpers import find_goal_with_name
from src.components.components import ComponentsLibrary
from src.components.operations import components_selection
from src.goals.cgtgoal import CGTGoal
from src.contracts.operations import *


def composition(goals: List[CGTGoal],
                name: str = None,
                description: str = None,
                connect_to: CGTGoal = None) -> CGTGoal:
    """Returns a new goal that is the result of the composition of 'goals'
    The new goal returned points to a copy of 'goals'"""

    for n, goal in enumerate(goals):
        if goal.connected_to is not None and connect_to is not None:
            if connect_to != goal.connected_to:
                print(goal.name + " is already part of another CGT. Making a copy of it...")
                goals[n] = copy.deepcopy(goal)
                goals[n].name = goals[n].name + "_copy"

    contracts: Dict[CGTGoal, List[Contract]] = {}

    if name is None:
        name = ""
        for goal in goals:
            name += goal.name + "||"
        name = name[:-2]

    for goal in goals:
        contracts[goal.name] = goal.contracts

    """Dot products mamong the contracts to perform the compositions of the conjunctions"""
    composition_contracts = (dict(list(zip(contracts, x))) for x in it.product(*iter(contracts.values())))

    """List of composed contracts. Each element of the list is in conjunction"""
    composed_contracts: List[Contract] = []

    for c in composition_contracts:
        contracts: List[Contract] = list(c.values())
        composed_contract = compose_contracts(contracts)
        composed_contracts.append(composed_contract)

    """Crate a new goal that is linked to the other goals by composition"""
    composed_goal = CGTGoal(name=name,
                            description=description,
                            contracts=composed_contracts,
                            refined_by=goals,
                            refined_with="COMPOSITION")

    """Or connect to existing goal"""
    if connect_to is None:
        """Crate a new goal that is linked to the other goals by composition"""
        return composed_goal
    else:
        connect_to.update_with(composed_goal, consolidate=False)


def conjunction(goals: List[CGTGoal],
                name: str = None,
                description: str = None,
                connect_to: CGTGoal = None) -> CGTGoal:
    """Conjunction Operations among the goals in 'goals'.
       It returns a new goal"""

    for n, goal in enumerate(goals):
        if goal.connected_to is not None and connect_to is not None:
            if connect_to != goal.connected_to:
                print(goal.name + " is already part of another CGT. Making a copy of it...")
                goals[n] = copy.deepcopy(goal)
                goals[n].name = goals[n].name + "_copy"

    if name is None:
        name = ""
        for goal in goals:
            name += goal.name + "^^"
        name = name[:-2]

    """For each contract pair, checks the consistency of the guarantees among the goals that have common assumptions"""
    for pair_of_goals in it.combinations(goals, r=2):

        assumptions_set = []
        guarantees_set = []

        for contract_1 in pair_of_goals[0].contracts:

            assumptions_set.extend(contract_1.assumptions)

            guarantees_set.extend(contract_1.guarantees)

            for contract_2 in pair_of_goals[1].contracts:

                variables = contract_1.variables.copy()

                variables.extend(contract_2.variables)

                assumptions_set.extend(contract_2.assumptions)

                guarantees_set.extend(contract_2.guarantees)

                """Checking Consistency only when the assumptions are satisfied together"""
                sat = check_satisfiability(variables, list(set(assumptions_set)))
                if sat:
                    """Checking Consistency only when the assumptions are satisfied together"""
                    sat = check_satisfiability(variables, list(set(guarantees_set)))
                    if not sat:
                        print("The assumptions in the conjunction of contracts "
                              "are not mutually exclusive and are inconsistent:\n" +
                              str(pair_of_goals[0]) + "\nCONJOINED WITH\n" + str(pair_of_goals[1])
                              + "\n\n" + str(list(set(guarantees_set))))

                        raise Exception("Conjunction Failed")

    print("The conjunction satisfiable.")

    # Creating new list of contracts
    list_of_new_contracts = []

    for goal in goals:
        contracts = goal.contracts
        for contract in contracts:
            new_contract = copy.deepcopy(contract)
            list_of_new_contracts.append(new_contract)

    conjoined_goal = CGTGoal(name=name,
                             description=description,
                             contracts=list_of_new_contracts,
                             refined_by=goals,
                             refined_with="CONJUNCTION")

    """Or connect to existing goal"""
    if connect_to is None:
        """Crate a new goal that is linked to the other goals by conjunction"""
        return conjoined_goal
    else:
        connect_to.update_with(conjoined_goal, consolidate=False)


def mapping(component_library: ComponentsLibrary,
            specification_goal: CGTGoal,
            name: str = None,
            description: str = None):
    """Given a component library and a specification connect to 'specification_goal' other goals that are the result
    of the composition of a selection of component in the library and that refined the specification
    after having propagated the assumptions"""

    if len(specification_goal.contracts) == 1:
        specification = specification_goal.contracts[0]
    else:
        raise Exception("The goal has multiple contracts in conjunction and cannot be mapped")

    """Get a list of components from the specification, greedy algorithm"""
    components, hierarchy = components_selection(component_library, specification)

    if len(components) == 0:
        raise Exception("No mapping possible. There is no component available in the library")

    """Compose the components"""
    composition_contract = compose_contracts(components)

    if name is None:
        mapping_name = ""
        for component in components:
            mapping_name += component.id + "||"
        mapping_name = mapping_name[:-2]
    else:
        mapping_name = name

    if len(hierarchy.values()) > 0:
        """Transforms the components in the dictionary in Goals"""
        hierarchy_goals: Dict[CGTGoal, List[CGTGoal]] = {}

        for i, (comp, comp_provided_by) in enumerate(hierarchy.items()):
            """Look if there is already a goal"""
            goal = find_goal_with_name(comp.id, hierarchy_goals)

            if goal is None:
                """Or create a new entry"""
                goal = CGTGoal(name=comp.id, contracts=[comp])

            for c_p in comp_provided_by:

                g_p = find_goal_with_name(c_p.id, hierarchy_goals)

                if g_p is None:
                    g_p = CGTGoal(name=c_p.id, contracts=[c_p])

                if goal not in hierarchy_goals:
                    hierarchy_goals[goal] = [g_p]
                else:
                    hierarchy_goals[goal].append(g_p)

        for i, (goal, providers) in enumerate(hierarchy_goals.items()):
            if len(providers) > 1:
                composition_providers = composition(providers)
                goal.provided_by(composition_providers)
            elif len(providers) == 1:
                goal.provided_by(providers[0])
            else:
                pass
            if i == 0:
                providing_goals_top = [goal]

    else:
        providing_goals_top = []
        for c in components:
            providing_goals_top.append(CGTGoal(name=c.id, contracts=[c]))

    """Create a top level goal 'composition_goal' and link it to the 'list_of_components_goals'"""
    composition_goal = CGTGoal(name=mapping_name,
                               description=description,
                               contracts=[composition_contract],
                               refined_by=providing_goals_top,
                               refined_with="MAPPING")

    """Link 'composition_goal' to the 'specification_goal' 
    This will also propagate the assumptions from composition_goal"""
    specification_goal.refine_by([composition_goal])


def create_contextual_cgt(goals: List[CGTGoal]) -> CGTGoal:
    """Returns a CGT from a list of goals based on the contexts of each goal"""

    variables: List[Type] = []
    contexts: Set[LTL] = set()

    """Extract all unique contexts"""
    for goal in goals:
        if goal.context is not None:
            c_vars, ctx = goal.context.get_context()
            variables.extend(c_vars)
            if ctx not in contexts:
                contexts.add(ctx)

    if len(contexts) == 1:
        cgt = composition(goals)
        return cgt

    contexts_mutually_exclusive = set()

    for i, ctx_a in enumerate(contexts):
        mutex = True
        for j, ctx_b in enumerate(contexts):
            if i != j:
                if is_implied_in(variables, ctx_a, ctx_b) or \
                       is_implied_in(variables, ctx_b, ctx_a):
                    mutex = False
        if mutex:
            satis = False
            for j, ctx_b in enumerate(contexts):
                if i != j:
                    if check_satisfiability(variables, [ctx_a, ctx_b]):
                        satis = True
            if not satis:
                contexts_mutually_exclusive.add(ctx_a)

    non_mutex_ctx = contexts - contexts_mutually_exclusive

    intermediate_ctx = []
    negated_ctx = []

    for i, ctx_a in enumerate(non_mutex_ctx):
        """List of contextes where ctx_a is implied"""
        implied_in = []
        for j, ctx_b in enumerate(non_mutex_ctx):
            if i != j and ctx_a not in contexts_mutually_exclusive and ctx_b not in contexts_mutually_exclusive:
                if is_implied_in(variables, ctx_a, ctx_b):
                    implied_in.append(ctx_b)
        if len(implied_in) > 0:
            if len(implied_in) > 1:
                ctx_i = get_smallest_set(variables, implied_in)
            else:
                ctx_i = implied_in[0]
            intermediate_ctx.append(ctx_i)
            negated_ctx.append(ctx_a)
            new_ctx = And([ctx_i, Not(ctx_a)])
            contexts_mutually_exclusive.add(new_ctx)

    for ctx in negated_ctx:
        if ctx not in intermediate_ctx:
            contexts_mutually_exclusive.add(ctx)

    contexts_mutually_exclusive = list(contexts_mutually_exclusive)
    print(contexts_mutually_exclusive)

    context_goals: Dict[LTL, List] = {}

    """Identifies the goals enabled for each mutually exclusive context"""
    for ctx in contexts_mutually_exclusive:
        for goal in goals:
            if goal.context is None:
                """Add goal to the context"""
                if ctx in context_goals:
                    if goal not in context_goals[ctx]:
                        context_goals[ctx].append(goal)
                else:
                    context_goals[ctx] = [goal]
            else:
                """Verify that the goal context is an abstraction of the mutex context"""
                var, goal_ctx = goal.context.get_context()
                if is_implied_in(variables, ctx, goal_ctx):
                    """Add goal to the context"""
                    if ctx in context_goals:
                        if goal not in context_goals[ctx]:
                            context_goals[ctx].append(goal)
                    else:
                        context_goals[ctx] = [goal]

    """Check if two mutex contexts have the same goals and merge them"""
    ctx_merged = set()
    context_goals_merged = {}
    for ctx_a, goals_a in context_goals.items():
        ctx_similar = set()
        for ctx_b, goals_b in context_goals.items():
            if ctx_a != ctx_b and \
                    ctx_a not in ctx_merged and \
                    ctx_b not in ctx_merged:
                if set(goals_a) == set(goals_b):
                    ctx_similar.add(ctx_a)
                    ctx_similar.add(ctx_b)
                    ctx_merged.add(ctx_a)
                    ctx_merged.add(ctx_b)
        """Merge the contexts"""
        if len(ctx_similar) > 0:
            new_ctx = Or(list(ctx_similar))
            context_goals_merged[new_ctx] = context_goals[list(ctx_similar)[0]]

    """Add the contexts that have not been merged"""
    for ctx_a, goals_a in context_goals.items():
        if ctx_a not in ctx_merged:
            context_goals_merged[ctx_a] = goals_a

    """Compose the goal in each mutually exclusive context"""
    composed_goals = []
    for ctx, goals in context_goals.items():
        ctx_goals = composition(goals)
        ctx_goals.context = Context(ctx)
        composed_goals.append(ctx_goals)

    """Conjoin the goals across all the mutually exclusive contexts"""
    cgt = conjunction(composed_goals)

    return cgt
