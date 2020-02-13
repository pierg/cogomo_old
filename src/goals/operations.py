import copy
import itertools
from typing import Dict, List, Tuple, Set

from goals.context import Context, get_smallest_context
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

    goals_ctx = []

    for n, goal in enumerate(goals):
        if goal.context is not None:
            goals_ctx.append(goal.context)

        if goal.connected_to is not None and connect_to is not None:
            if connect_to != goal.connected_to:
                print(goal.name + " is already part of another CGT. Making a copy of it...")
                goals[n] = copy.deepcopy(goal)
                goals[n].name = goals[n].name + "_copy"

    contracts: Dict[CGTGoal, List[Contract]] = {}

    if len(goals_ctx) > 0:
        composition_ctx_vars = []
        composition_ctx_formula = []
        for ctx in goals_ctx:
            add_variables_to_list(composition_ctx_vars, ctx.variables)
            composition_ctx_formula.append(ctx.formula)

        composition_ctx = Context(variables=composition_ctx_vars,
                                  expression=And(composition_ctx_formula))
    else:
        composition_ctx = None

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
                            context=composition_ctx,
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

    goals_ctx = []
    for n, goal in enumerate(goals):
        if goal.context is not None:
            goals_ctx.append(goal.context)
        if goal.connected_to is not None and connect_to is not None:
            if connect_to != goal.connected_to:
                print(goal.name + " is already part of another CGT. Making a copy of it...")
                goals[n] = copy.deepcopy(goal)
                goals[n].name = goals[n].name + "_copy"

    if len(goals_ctx) > 0:
        cojunction_ctx_vars = []
        cojunction_ctx_formula = []
        for ctx in goals_ctx:
            add_variables_to_list(cojunction_ctx_vars, ctx.variables)
            cojunction_ctx_formula.append(ctx.formula)

        cojunction_ctx = Context(variables=cojunction_ctx_vars,
                                 expression=Or(cojunction_ctx_formula))
    else:
        cojunction_ctx = None

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
                             context=cojunction_ctx,
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


def filter_and_simplify_contexts(contexts: List[List[Context]]) -> List[List[Context]]:
    new_list: List[List[Context]] = []

    for c_list in contexts:
        """Extract formulas and check satisfiability"""
        c_vars = []
        c_expr = []
        for c in c_list:
            add_variables_to_list(c_vars, c.variables)
            c_expr.append(c.formula)

        if not check_satisfiability(c_vars, c_expr):
            continue

        """Simplify"""
        new_comb = c_list.copy()

        """Simplify new_comb"""
        for a in list(new_comb):
            for b in list(new_comb):
                if a is not b:
                    if a.is_included_in(b):
                        new_comb.remove(a)
                        break

        new_list.append(new_comb)

    return new_list



def create_contextual_operational_cgt(goals: List[CGTGoal]) -> CGTGoal:
    pass

def create_contextual_combinatorial_cgt(goals: List[CGTGoal]) -> CGTGoal:
    """Returns a CGT from a list of goals based on the contexts of each goal"""

    """Extract all unique contexts"""
    contexts: List[Context] = []

    for goal in goals:
        if goal.context is not None:
            already_there = False
            g_c = goal.context
            for c in contexts:
                if c == g_c:
                    already_there = True
            if not already_there:
                contexts.append(g_c)

    """If it's only one context return the CGT"""
    if len(contexts) == 1:
        cgt = composition(goals)
        cgt.context = list(contexts)[0]
        return cgt

    """Extract the combinations of all contextes"""
    combs_all_contexts: List[List[Context]] = []

    """Extract the combinations of all contextes with negations"""
    combs_all_contexts_neg: List[List[Context]] = []

    """Populating 'combs_all_contexts' and 'combs_all_contexts_neg'"""
    for i in range(0, len(contexts)):
        combs = itertools.combinations(contexts, i + 1)

        for comb in combs:

            comb_contexts = list(comb).copy()

            comb_contexts_neg = list(comb).copy()

            for ctx in contexts:
                if ctx not in comb_contexts_neg:
                    ctx_vars = ctx.variables
                    ctx_exp = Not(ctx.formula)
                    comb_contexts_neg.append(Context(variables=ctx_vars,
                                                     expression=ctx_exp))

            combs_all_contexts.append(comb_contexts)

            combs_all_contexts_neg.append(comb_contexts_neg)

    print("\n\n____________________ALL_COMBINATIONS_____________________")
    for c_list in combs_all_contexts:
        print(*c_list, sep='\t\t\t')

    print("\n\n____________________ALL_COMBINATIONS_WITH_NEG_____________________")
    for c_list in combs_all_contexts_neg:
        print(*c_list, sep='\t\t\t')

    """Filter from combs_all_contexts the comb that are satisfiable and if they are then simplify them"""
    combs_simpl_sat_contexts: List[List[Context]] = filter_and_simplify_contexts(combs_all_contexts)

    print("\n\n___________CONSISTENT_AND_SIMPLIFIED_____________________\n")
    for c_list in combs_simpl_sat_contexts:
        print(*c_list, sep='\t\t\t')

    """Filter from combs_contexts_neg the comb that are satisfiable and if they are then simplify them"""
    combs_simpl_sat_contexts_neg: List[List[Context]] = filter_and_simplify_contexts(combs_all_contexts_neg)

    print("\n\n___________CONSISTENT_AND_SIMPLIFIED_WITH_NEG_____________________\n")
    for c_list in combs_simpl_sat_contexts_neg:
        print(*c_list, sep='\t\t\t')

    """Merge the consistent contextes with conjunction"""
    contexts_merged: List[Context] = []

    for group in combs_simpl_sat_contexts_neg:
        variables: List[Type] = []
        formulas: List[LTL] = []
        for ctx in group:
            add_variables_to_list(variables, ctx.variables)
            formulas.append(ctx.formula)

        formula = And(formulas)
        new_ctx = Context(expression=formula, variables=variables)
        already_there = False
        for c in contexts_merged:
            if c == new_ctx:
                already_there = True
        if not already_there:
            contexts_merged.append(new_ctx)

    print("\n\n___________MERGED______________________________\n")
    for c in contexts_merged:
        print(c)

    mutex = True
    for ca in list(contexts_merged):
        for cb in list(contexts_merged):
            if ca is not cb:
                if ca.is_satisfiable_with(cb):
                    print(str(ca) + "  SAT WITH   " + str(cb))
                    mutex = False
                if ca.is_included_in(cb):
                    print(str(ca) + "  INCLUDED IN   " + str(cb))
                    contexts_merged.remove(ca)
                    break

    if mutex:
        print("All contexts are mutually exclusive")

    print("\n\n___________MERGED_SIMPLIFIED_________________________\n")
    for c in contexts_merged:
        print(c)

    """Map each goal to each context"""
    context_goals: Dict[Context, List] = {}
    for ctx in contexts_merged:
        for goal in goals:
            """If the goal has no context"""
            if goal.context is None:
                """Add goal to the context"""
                if ctx in context_goals:
                    if goal not in context_goals[ctx]:
                        context_goals[ctx].append(goal)
                else:
                    context_goals[ctx] = [goal]
            else:
                """Verify that the context is an abstraction of the goal context"""
                goal_ctx = goal.context
                if ctx.is_included_in(goal_ctx):
                    """Add goal to the context"""
                    if ctx in context_goals:
                        if goal not in context_goals[ctx]:
                            context_goals[ctx].append(goal)
                    else:
                        context_goals[ctx] = [goal]

    """Check all the contexts that point to the same set of goals and take the most abstract one"""
    for ctxa, goalsa in dict(context_goals).items():

        for ctxb, goalsb in dict(context_goals).items():
            if ctxa is not ctxb:
                if set(goalsa) == set(goalsb):
                    if ctxa.is_included_in(ctxb):
                        print("Simplifying " + str(ctxa))
                        del context_goals[ctxa]

    """Compose all the set of goals in identified context"""
    composed_goals = []
    for ctx, goals in context_goals.items():
        ctx_goals = composition(goals)
        composed_goals.append(ctx_goals)

    """Conjoin the goals across all the mutually exclusive contexts"""
    cgt = conjunction(composed_goals)

    return cgt
