import copy
import itertools
from typing import Dict, List, Tuple

from goals.helpers import find_goal_with_name
from src.components.components import ComponentsLibrary
from src.components.operations import components_selection
from src.goals.cgtgoal import CGTGoal
from src.contracts.operations import *


def composition(goals: List[CGTGoal],
                name: str = None,
                description: str = None) -> CGTGoal:
    """Returns a new goal that is the result of the composition of 'goals'
    The new goal returned points to a copy of 'goals'"""

    for n, goal in enumerate(goals):
        if goal.connected_to is not None:
            print(goal.name + " is already part of another CGT. Making a copy of it...")
            goals[n] = copy.deepcopy(goal)

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

    return composed_goal


def conjunction(goals: List[CGTGoal],
                name: str = None,
                description: str = None) -> CGTGoal:
    """Conjunction Operations among the goals in 'goals'.
       It returns a new goal"""

    for n, goal in enumerate(goals):
        if goal.connected_to is not None:
            print(goal.name + " is already part of another CGT. Making a copy of it...")
            goals[n] = copy.deepcopy(goal)

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

                variables.update(contract_2.variables)

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

    # Creating a new Goal parent
    conjoined_goal = CGTGoal(name=name,
                             description=description,
                             contracts=list_of_new_contracts,
                             refined_by=goals,
                             refined_with="CONJUNCTION")

    return conjoined_goal


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

    """Keep track of the head of the mapped goals"""
    providing_goals_top = None

    for i, (goal, providers) in enumerate(hierarchy_goals.items()):
        if len(providers) > 1:
            composition_providers = composition(providers)
            goal.provided_by(composition_providers)
        elif len(providers) == 1:
            goal.provided_by(providers[0])
        else:
            pass
        if i == 0:
            providing_goals_top = goal

    print(providing_goals_top)

    """Create a top level goal 'composition_goal' and link it to the 'list_of_components_goals'"""
    composition_goal = CGTGoal(name=mapping_name,
                               description=description,
                               contracts=[composition_contract],
                               refined_by=[providing_goals_top],
                               refined_with="MAPPING")

    """Link 'composition_goal' to the 'specification_goal' 
    This will also propagate the assumptions from composition_goal"""
    specification_goal.refine_by([composition_goal])


def create_contextual_cgt(list_of_goals: List[CGTGoal]) -> CGTGoal:
    """Returns a CGT from a list of goals based on the contexts of each goal"""

    variables = {}
    contexts = set()

    """Extract all the contexts"""
    for goal in list_of_goals:
        if goal.context is not None:
            var, ctx_1 = goal.context
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
            if goal.context is None:
                if ctx in context_goals:
                    if goal not in context_goals[ctx]:
                        context_goals[ctx].append(goal)
                else:
                    context_goals[ctx] = [goal]
            else:
                var, goal_ctx = goal.context
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


def add_expectations(cgt: CGTGoal, expectations: List[Contract]):
    """Domain Hypothesis or Expectations (i.e. prescriptive assumptions on the environment)
    Expectations are conditional assumptions, they get added to each contract of the CGT
    only if the Contract guarantees concern the 'expectations' guarantees and are consistent with them"""

    add_expectations_recursive(cgt, expectations)


def add_expectations_recursive(cgt: CGTGoal, expectations: List[Contract]):
    """For each contract in the CGT, add the expectation as assumption if opportune"""
    for contract in cgt.contracts:
        for expectation in expectations:
            if have_shared_keys(contract.variables, expectation.variables):
                if are_satisfied_in([contract.variables, expectation.variables],
                                    [contract.unsaturated_guarantees, expectation.unsaturated_guarantees]):
                    contract.add_variables(expectation.variables)
                    contract.add_assumptions(expectation.assumptions)
    if cgt.refined_by is None:
        consolidate_bottom_up(cgt)
    else:
        for goal in cgt.refined_by:
            add_expectations(goal, expectations)
