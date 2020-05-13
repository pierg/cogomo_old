from copy import deepcopy
from itertools import product, combinations
from typing import List, Dict, Tuple
from components.components import ComponentsLibrary
from src.contracts.contract import Contract, InconsistentContracts, IncompatibleContracts
from src.contracts.operations import compose_contracts
from src.goals.cgtgoal import CGTGoal
from typescogomo.assumption import Context
from typescogomo.formula import InconsistentException
from typescogomo.formulae import Guarantees, Assumptions
from src.goals.helpers import extract_ltl_rules, map_goals_to_contexts, filter_and_simplify_contexts, \
    extract_unique_contexts_from_goals, extract_all_combinations_and_negations_from_contexts, \
    add_constraints_to_all_contexts, merge_contexes, context_based_specification_clustering


class CGTFailException(Exception):
    def __init__(self, failed_operation: "str", faild_motivation: "str", goals_involved_a: List[CGTGoal], goals_involved_b: List[CGTGoal]):
        self.failed_operation = failed_operation
        self.faild_motivation = faild_motivation
        self.goals_involved_a = goals_involved_a
        self.goals_involved_b = goals_involved_b


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
                goals[n] = deepcopy(goal)
                goals[n].name = goals[n].name

    contracts: Dict[CGTGoal, List[Contract]] = {}

    if name is None:
        names = []
        for goal in goals:
            names.append(goal.name)
        names.sort()
        comp_name = ""
        for name in names:
            comp_name += name + "||"
        name = comp_name[:-2]

    for goal in goals:
        contracts[goal.name] = goal.contracts

    """Dot products among the contracts to perform the compositions of the conjunctions"""
    composition_contracts = (dict(list(zip(contracts, x))) for x in product(*iter(contracts.values())))

    """List of composed contracts. Each element of the list is in conjunction"""
    composed_contracts: List[Contract] = []

    for c in composition_contracts:
        contracts: List[Contract] = list(c.values())
        try:
            composed_contract = compose_contracts(contracts)

        except InconsistentContracts as e:
            goals_involved = []
            goals_failed = []
            for goal in goals:
                for contract in goal.contracts:
                    if e.guarantee_1 <= contract.guarantees.formula:
                        goals_involved.append(goal)
                    if e.guarantee_2 >= contract.guarantees.formula:
                        goals_failed.append(goal)
            raise CGTFailException(failed_operation="composition",
                                   faild_motivation="inconsistent",
                                   goals_involved_a=goals_involved,
                                   goals_involved_b=goals_failed)

        except IncompatibleContracts as e:

            goals_involved = []
            goals_failed = []
            for goal in goals:
                for contract in goal.contracts:
                    if e.assumptions_1 <= contract.assumptions.formula:
                        goals_involved.append(goal)
                    if e.assumptions_2 <= contract.assumptions.formula:
                        goals_failed.append(goal)
            raise CGTFailException(failed_operation="composition",
                                   faild_motivation="incompatible",
                                   goals_involved_a=goals_involved,
                                   goals_involved_b=goals_failed)

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
                goals[n] = deepcopy(goal)
                goals[n].name = goals[n].name

    if name is None:
        names = []
        for goal in goals:
            names.append(goal.name)
        names.sort()
        conj_name = ""
        for name in names:
            conj_name += name + "^^"
        name = conj_name[:-2]

    """For each contract pair, checks the consistency of the guarantees among the goals that have common assumptions"""
    for pair_of_goals in combinations(goals, r=2):

        assumptions_set = []
        guarantees_set = []

        for contract_1 in pair_of_goals[0].contracts:

            assumptions_set.extend(contract_1.assumptions.list)
            guarantees_set.extend(contract_1.guarantees.list)

            for contract_2 in pair_of_goals[1].contracts:

                assumptions_set.extend(contract_2.assumptions.list)
                guarantees_set.extend(contract_2.guarantees.list)

                try:
                    Assumptions(assumptions_set)

                    try:
                        Guarantees(guarantees_set)

                    except InconsistentException:
                        print("The assumptions in the conjunction of contracts "
                              "are not mutually exclusive and are inconsistent:\n" +
                              str(pair_of_goals[0]) + "\nCONJOINED WITH\n" + str(pair_of_goals[1])
                              + "\n\n" + str(list(set(guarantees_set))))
                        raise Exception("Conjunction Failed")
                except:
                    pass

    print("The conjunction satisfiable.")

    # Creating new list of contracts
    list_of_new_contracts = []

    for goal in goals:
        contracts = goal.contracts
        for contract in contracts:
            new_contract = deepcopy(contract)
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
    from components.operations import components_selection
    components, hierarchy = components_selection(component_library, specification)

    if len(components) == 0:
        raise Exception("No mapping possible. There is no component available in the library")

    """Compose the components"""
    composition_contract = compose_contracts(components)

    if name is None:
        names = []
        for component in components:
            names.append(component.id)
        names.sort()
        name = ""
        for n in names:
            name += n + "||"
        name = name[:-2]

    if len(hierarchy.values()) > 0:
        """Transforms the components in the dictionary in Goals"""
        hierarchy_goals: Dict[CGTGoal, List[CGTGoal]] = {}

        for i, (comp, comp_provided_by) in enumerate(hierarchy.items()):
            """Look if there is already a goal"""
            from goals.helpers import find_goal_with_name
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

    """Create a top level goal 'composition_goal'"""
    composition_goal = CGTGoal(name=name,
                               description=description,
                               contracts=[composition_contract],
                               refined_by=providing_goals_top,
                               refined_with="COMPOSITION/MAPPING")

    """Link 'composition_goal' to the 'specification_goal' 
    This will also propagate the assumptions from composition_goal"""
    specification_goal.refine_by([composition_goal])


def create_contextual_clusters(goals: List[CGTGoal], type: str, context_rules: Dict = None) -> Dict:
    """Returns all combinations that are consistent"""

    if type == "MINIMAL":
        """Context Creation"""
        """Within one context combination (a row), analyse each pair and discard the bigger set. It is always True"""
        KEEP_SMALLER_CONTEXT = True
        """Among a pair of context combinations (two rows), save only the smaller context"""
        KEEP_SMALLER_COMBINATION = True
        """Goal Mapping"""
        """When mapping a goal context to a combination of context C, map if the goal context is satisfiable with C"""
        GOAL_CTX_SAT = False
        """When mapping a goal context to a combination of context C, map if the goal context is smaller than C"""
        GOAL_CTX_SMALLER = False
        """When more context points to the same set of goal take the smaller context"""
        SAVE_SMALLER_CONTEXT = False

    elif type == "MUTEX":
        """Context Creation"""
        """Within one context combination (a row), analyse each pair and discard the bigger set"""
        KEEP_SMALLER_CONTEXT = True
        """Among a pair of context combinations (two rows), save only the smaller context"""
        KEEP_SMALLER_COMBINATION = False
        """Goal Mapping"""
        """When mapping a goal context to a combination of context C, map if the goal context is satisfiable with C"""
        GOAL_CTX_SAT = False
        """When mapping a goal context to a combination of context C, map if the goal context is smaller than C"""
        GOAL_CTX_SMALLER = False
        """When more context points to the same set of goal take the smaller context"""
        SAVE_SMALLER_CONTEXT = False
    else:
        raise Exception("The type is not supported, either MINIMAL or MUTEX")

    """Extract context rules in LTL"""
    if context_rules is not None:
        ltl_rules = extract_ltl_rules(context_rules)
    else:
        ltl_rules = []

    """Extract all unique contexts"""
    contexts: List[Context] = extract_unique_contexts_from_goals(goals)

    print("\n\n\n\n" + str(len(goals)) + " GOALS\nCONTEXTS:" + str([str(c) for c in contexts]))

    print("\n\n")

    """Extract the combinations of all contextes and the combination with the negations of all the other contexts"""
    combs_all_contexts, combs_all_contexts_neg = extract_all_combinations_and_negations_from_contexts(contexts)

    context_goals = {}

    if type == "MINIMAL":
        context_goals = context_based_specification_clustering(combs_all_contexts, ltl_rules, goals,
                                                               KEEP_SMALLER_COMBINATION,
                                                               GOAL_CTX_SAT,
                                                               GOAL_CTX_SMALLER,
                                                               SAVE_SMALLER_CONTEXT)

    if type == "MUTEX":
        context_goals = context_based_specification_clustering(combs_all_contexts_neg, ltl_rules, goals,
                                                               KEEP_SMALLER_COMBINATION,
                                                               GOAL_CTX_SAT,
                                                               GOAL_CTX_SMALLER,
                                                               SAVE_SMALLER_CONTEXT)
        for ctx, goals in context_goals.items():
            from helper.buchi import generate_buchi
            g_name = "||".join(g.name for g in goals)
            generate_buchi(ctx, "buchi/" + g_name)

    return context_goals


def create_cgt(context_goals: Dict):
    """Compose all the set of goals in identified context"""
    composed_goals = []
    for ctx, goals in context_goals.items():
        ctx_goals = composition(goals)
        composed_goals.append(ctx_goals)

    """Conjoin the goals across all the mutually exclusive contexts"""
    cgt = conjunction(composed_goals)

    return cgt


def pretty_cgt_exception(e: CGTFailException) -> str:
    ret = "---------CGT-FAIL---------\n"
    ret += "\n\tOPERATION:\t\t" + e.failed_operation
    ret += "\n\tMOTIVATION:\t\t" + e.faild_motivation
    ret += "\n\tGOALS_OK:\t\t\t" + str([g.name for g in e.goals_involved_a])
    ret += "\n\tGOALS_FAILED:\t\t" + str([g.name for g in e.goals_involved_b])

    ret += "\n\n"

    for g in e.goals_involved_a:
        ret += str(g)

    for g in e.goals_involved_b:
        ret += str(g)

    ret += "\n---------CGT-FAIL---------\n"
    return ret


def pretty_contexts_goals(context_goals: Dict) -> str:
    ret = ""
    for i, (ctx, ctx_goals) in enumerate(context_goals.items()):
        ret += "\n" + str(ctx.formula) + "\n-->\t" + str(len(ctx_goals)) + " goals: " + str(
            [c.name for c in ctx_goals]) + "\n"
    return ret