import itertools
from copy import deepcopy
from typing import Union, Dict, List, Tuple
from checks.nusmv import check_satisfiability
from checks.tools import Not, Or, And
from typescogomo.contexts import Context
from typescogomo.formulae import LTL, LTLs, IconsistentException
from typescogomo.variables import Type, Boolean, Variables
from goals.cgtgoal import CGTGoal

"""Context Creation"""
"""Within one context combination (a row), analyse each pair and discard the bigger set"""
KEEP_SMALLER_CONTEXT = True
"""Among a pair of context combinations (two rows), save only the smaller context"""
KEEP_SMALLER_COMBINATION = True

"""Goal Mapping"""
"""When mapping a goal context to a combination of context C, map if the goal context is smaller than C"""
GOAL_CTX_SMALLER = False
"""When more context points to the same set of goal take the smaller context"""
SAVE_SMALLER_CONTEXT = False


def find_goal_with_name(name: str, goals: Union[Dict[CGTGoal, List[CGTGoal]], List[CGTGoal]]):
    """Search for an existing goal"""
    if isinstance(goals, dict):
        for goal_1, goal_2 in goals.items():
            if goal_1.name == name:
                return goal_1
            for g in goal_2:
                if g.name == name:
                    return g

    elif isinstance(goals, list):
        for goal in goals:
            if goal.name == name:
                return goal


def filter_and_simplify_contexts(contexts: List[List[Context]]) -> List[List[Context]]:
    new_list: List[List[Context]] = []
    print("\n\nFILTERING " + str(len(contexts)) + " CONTEXTS...")

    for c_list in contexts:
        """Extract formulas and check satisfiability"""
        try:
            LTLs(c_list)
        except IconsistentException:
            continue

        """Simplify"""
        new_comb = c_list.copy()

        """If a context in one combination includes another context, take smaller or bigger set"""
        """Already included in LTLs"""
        new_comb_copy = list(new_comb)
        for ca in new_comb_copy:
            for cb in new_comb_copy:
                if KEEP_SMALLER_CONTEXT:
                    if (ca is not cb) and \
                            cb.formula in [n.formula for n in new_comb]:
                        if ca <= cb:
                            print(str(ca) + "\nINCLUDED IN\n" + str(cb))
                            new_comb.remove(cb)
                            print(str(cb) + "\nREMOVED (kept smaller)")
                else:
                    if (ca is not cb) and \
                            ca in new_comb:
                        if ca <= cb:
                            print(str(ca) + "\nINCLUDED IN\n" + str(cb))
                            new_comb.remove(ca)
                            print(str(ca) + "\nREMOVED (kept bigger)")

        new_list.append(new_comb)

    return new_list


def extract_ltl_rules(context_rules: Dict) -> List[LTL]:
    """Dict:  ltl_formula -> list_of_variables_involved"""

    ltl_list: List[LTL] = []

    for cvars in context_rules["mutex"]:
        variables_list: List[Type] = []
        ltl = "G("
        ltl_components = []
        for vs in cvars:
            variables_list.extend(vs.variables.list)

        cvars_str = [n.formula for n in cvars]
        for vs in list(cvars_str):
            cvars_str.remove(vs)
            cvars_str.append(Not(vs))
            ltl_components.append(Or(cvars_str))

        ltl += Not(And(ltl_components))

        ltl += ")"
        ltl_list.append(LTL(formula=ltl, variables=Variables(variables_list)))

    for cvars in context_rules["inclusion"]:
        variables_list: List[Type] = []
        ltl = "G("
        for i, vs in enumerate(cvars):
            variables_list.extend(vs.variables.list)
            ltl += str(vs)
            if i < (len(cvars) - 1):
                ltl += " -> "
        ltl += ")"
        ltl_list.append(LTL(formula=ltl, variables=Variables(variables_list)))

    return ltl_list


def extract_unique_contexts_from_goals(goals: List[CGTGoal]) -> List[Context]:
    contexts: List[Context] = []

    for goal in goals:
        if goal.context is not None:
            already_there = False
            g_c = goal.context
            if len(g_c) == 0:
                continue
            if len(g_c) > 1:
                raise Exception("Context extraction is supported only to goals with individual contracts")
            if len(g_c) == 1:
                g_c = g_c[0]
            for c in contexts:
                if c == g_c:
                    already_there = True
            if not already_there:
                contexts.append(g_c)

    return contexts


def add_constraints_to_all_contexts(comb_contexts: List[List[Context]], context_variables_rules: List[LTL]):
    copy_list = list(comb_contexts)
    for c_list in copy_list:
        cvars = []
        for c in c_list:
            cvars.extend(c.variables.list)
        rules_to_add = []
        variables_to_add = []
        for rule in context_variables_rules:
            if len(list(set(cvars) & set(rule.variables.list))) > 0:
                rules_to_add.append(rule.formula)
                variables_to_add.extend(rule.variables.list)
        c_list.append(Context(formula=And(rules_to_add), variables=Variables(variables_to_add)))
    return copy_list


def add_constraints_to_goal(goals: List[CGTGoal], context_variables_rules: Dict[LTL, List[Type]]):
    for goal in goals:
        context = goal.context
        if context is not None:
            cvars = context.variables
            for k, v in context_variables_rules.items():
                if len(list(set(cvars) & set(v))) > 0:
                    """They have at least two variables in common, then add rule"""
                    context. \
                        merge_with(Context(k, v))
                    goal.context = context


def extract_all_combinations_and_negations_from_contexts(contexts: List[Context]) \
        -> Tuple[List[List[Context]], List[List[Context]]]:
    """Extract the combinations of all contexts"""
    combs_all_contexts: List[List[Context]] = []

    """Extract the combinations of all contexts with negations"""
    combs_all_contexts_neg: List[List[Context]] = []

    for i in range(0, len(contexts)):
        combs = itertools.combinations(contexts, i + 1)

        for comb in combs:

            comb_contexts = list(comb)
            comb_contexts_neg = list(comb)

            for ctx in contexts:
                if ctx.formula not in [n.formula for n in comb_contexts_neg]:
                    ctx_copy = deepcopy(ctx)
                    ctx_copy.negate()
                    comb_contexts_neg.append(ctx_copy)

            combs_all_contexts.append(comb_contexts)
            combs_all_contexts_neg.append(comb_contexts_neg)

    return combs_all_contexts, combs_all_contexts_neg


def merge_contexes(contexts: List[List[Context]]) -> Tuple[List[Context], List[Context]]:
    """Merge the consistent contexts with conjunction"""
    contexts_merged: List[Context] = []

    print("\n\nMERGING " + str(len(contexts)) + " CONTEXTS...")

    for group in contexts:
        if len(group) > 0:
            """Extract formulas and check satisfiability, it also filters and simplify each context"""
            try:
                conj = LTLs(group)
            except IconsistentException:
                continue
            new_ctx = Context()
            new_ctx.formula = str(conj.formula)
            new_ctx.variables = conj.variables
            already_there = False
            """"Check if newly created context is not equivalent to an existing previously created context"""
            for c in contexts_merged:
                if c == new_ctx:
                    already_there = True
            if not already_there:
                contexts_merged.append(new_ctx)

    context_merged_simplified = contexts_merged.copy()
    mutex = True
    context_merged_simplified_copy = list(context_merged_simplified)
    for ca in context_merged_simplified_copy:
        for cb in context_merged_simplified_copy:
            if KEEP_SMALLER_COMBINATION:
                if (ca is not cb) and \
                        cb in context_merged_simplified:
                    if ca <= cb:
                        print(str(ca) + "\nINCLUDED IN\n" + str(cb))
                        context_merged_simplified.remove(cb)
                        print(str(cb) + "\nREMOVED (kept smaller)")
                    else:
                        if ca.is_satisfiable_with(cb):
                            mutex = False
            else:
                if (ca is not cb) and \
                        ca in context_merged_simplified:
                    if ca <= cb:
                        print(str(ca) + "\nINCLUDED IN\n" + str(cb))
                        context_merged_simplified.remove(ca)
                        print(str(ca) + "\nREMOVED (kept bigger)")
                    else:
                        if ca.is_satisfiable_with(cb):
                            mutex = False

    if mutex:
        print("****  All contexts are mutually exclusive  ****")
    else:
        print("**** Contexts are NOT mutually exclusive  ****")

    return contexts_merged, context_merged_simplified


def map_goals_to_contexts(contexts: List[Context], goals: List[CGTGoal]) -> Dict[Context, List[CGTGoal]]:
    """Map each goal to each context, refined indicates if a contexts c point to goals that have a context which is
    a refinement of c, or an abstraction of c (refined=False) """

    goals_non_mapped = list(goals)
    print("\n\nMAPPING " + str(len(goals)) + " GOALS TO " + str(len(contexts)) + " CONTEXTS")
    context_goals: Dict[Context, List[CGTGoal]] = {}
    for ctx in contexts:
        for goal in goals:
            """If the goal has no context"""
            if goal.context is None:
                """Add goal to the context"""
                if ctx in context_goals:
                    if goal not in context_goals[ctx]:
                        context_goals[ctx].append(goal)
                else:
                    context_goals[ctx] = [goal]
                if goal in goals_non_mapped:
                    goals_non_mapped.remove(goal)
            else:
                goal_ctxs = goal.context
                goal_ctx = goal_ctxs[0]
                if GOAL_CTX_SMALLER:
                    """Verify that the goal is included the context"""
                    if goal_ctx <= ctx:
                        print("Goal_ctx: " + str(goal_ctx) + " \t-->\t Ctx: " + str(ctx))
                        """Add goal to the context"""
                        if ctx in context_goals:
                            if goal not in context_goals[ctx]:
                                context_goals[ctx].append(goal)
                        else:
                            context_goals[ctx] = [goal]
                        if goal in goals_non_mapped:
                            goals_non_mapped.remove(goal)
                else:
                    """Verify that the context is included in goal context"""
                    if ctx <= goal_ctx:
                        print("Ctx: " + str(ctx) + " \t-->\t Goal_ctx: " + str(goal_ctx))
                        """Add goal to the context"""
                        if ctx in context_goals:
                            if goal not in context_goals[ctx]:
                                context_goals[ctx].append(goal)
                        else:
                            context_goals[ctx] = [goal]
                        if goal in goals_non_mapped:
                            goals_non_mapped.remove(goal)

    """Check all the contexts that point to the same set of goals and take the most abstract one"""
    ctx_removed = []
    context_goals_copy = dict(context_goals)
    for ctxa, goalsa in context_goals_copy.items():

        for ctxb, goalsb in context_goals_copy.items():
            if ctxa.formula in ctx_removed:
                continue
            if ctxb.formula in ctx_removed:
                continue
            if ctxa is not ctxb:
                if set(goalsa) == set(goalsb):
                    if ctxa <= ctxb:
                        print(str(ctxa) + "\nINCLUDED IN\n" + str(ctxb))
                        if SAVE_SMALLER_CONTEXT:
                            del context_goals[ctxb]
                            ctx_removed.append(ctxb.formula)
                            print(str(ctxb) + "\nREMOVED")
                        else:
                            del context_goals[ctxa]
                            ctx_removed.append(ctxa.formula)
                            print(str(ctxa) + "\nREMOVED")

    """Check the all the goals have been mapped"""
    if len(goals_non_mapped) > 0:
        print("+++++CAREFUL+++++++")
        for g in goals_non_mapped:
            print(g.name + ": " + str(g.context) + " not mapped to any goal")
        raise Exception("Some goals have not been mapped to the context!")

    print("*** ALL GOAL HAVE BEEN MAPPED TO A CONTEXT ***")

    return context_goals


def prioritize_goal(first_priority_goal, second_priority_goal):
    pass
    """
    Makes the assumption of one goal dependent on the satisfiability of the assumptions of the second goal
    """
    variables = []
    stronger_assumptions_list = []

    for contract in first_priority_goal.contracts:
        variables.extend(contract.variables)
        stronger_assumptions_list.append(And(contract.assumptions))

    for contract in second_priority_goal.contracts:
        contract.add_variables(variables)
        contract.add_assumptions(Not(Or(stronger_assumptions_list)))
