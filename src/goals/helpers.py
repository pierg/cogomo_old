import itertools
from typing import Union, Dict, List, Tuple

from checks.nsmvhelper import add_variables_to_list
from checks.nusmv import check_satisfiability
from typescogomo.formulae import LTL, Assumption, Context
from typescogomo.variables import Type, Boolean
from goals.cgtgoal import CGTGoal
from helper.logic import Not, And, Or

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


# def group(contexts: List[Context], keep_smaller)


def filter_and_simplify_contexts(contexts: List[List[Context]]) -> List[List[Context]]:
    new_list: List[List[Context]] = []
    print("\n\nFILTERING " + str(len(contexts)) + " CONTEXTS...")

    for c_list in contexts:
        """Extract formulas and check satisfiability"""
        c_vars = []
        c_expr = []
        for c in c_list:
            add_variables_to_list(c_vars, c.variables)
            c_expr.append(c)

        if not check_satisfiability(c_vars, c_expr):
            continue

        """Simplify"""
        new_comb = c_list.copy()

        """If a context in one combination includes another context, take smaller or bigger set"""
        # group(new_comb, keep_smaller=KEEP_SMALLER_CONTEXT)

        new_comb_copy = list(new_comb)
        for ca in new_comb_copy:
            for cb in new_comb_copy:
                if KEEP_SMALLER_CONTEXT:
                    if (ca is not cb) and \
                            cb in new_comb:
                        if ca.is_included_in(cb):
                            print(str(ca) + "\nINCLUDED IN\n" + str(cb))
                            new_comb.remove(cb)
                            print(str(cb) + "\nREMOVED (kept smaller)")
                else:
                    if (ca is not cb) and \
                            ca in new_comb:
                        if ca.is_included_in(cb):
                            print(str(ca) + "\nINCLUDED IN\n" + str(cb))
                            new_comb.remove(ca)
                            print(str(ca) + "\nREMOVED (kept bigger)")

        new_list.append(new_comb)

    return new_list


def are_all_mutually_exclusive(contexts: List[Context]) -> bool:
    all_pairs = itertools.combinations(contexts, 2)

    for pair in all_pairs:
        """Extract formulas and check satisfiability"""
        c_vars = []
        c_expr = []
        for c in pair:
            add_variables_to_list(c_vars, c.variables)
            c_expr.append(c)

        if check_satisfiability(c_vars, c_expr):
            return False

    return True


def extract_context_rules(context_rules: Dict) -> Dict[LTL, List[Type]]:
    """Dict:  ltl_formula -> list_of_variables_involved"""

    context_rules_variables: Dict[LTL, List[Type]] = {}

    for cvars in context_rules["mutex"]:
        ltl = "G("
        ltl_components = []
        var_types = []
        for vs in cvars:
            var_types.append(Boolean(str(vs)))
            vars_mod = list(cvars)
            vars_mod.remove(vs)
            vars_mod.append(Not(vs, brakets=False))
            ltl_components.append(Or(vars_mod))

        ltl += str(Not(And(ltl_components)))

        ltl += ")"
        context_rules_variables[Assumption(ltl, kind="context")] = var_types

    for cvars in context_rules["inclusion"]:
        var_types = []
        ltl = "G("
        for i, vs in enumerate(cvars):
            var_types.append(Boolean(str(vs)))
            ltl += str(vs)
            if i < (len(cvars) - 1):
                ltl += " -> "
        ltl += ")"
        context_rules_variables[Assumption(ltl, kind="context")] = var_types

    return context_rules_variables


def extract_unique_contexts_from_goals(goals: List[CGTGoal]) -> List[Context]:
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

    return contexts


def add_constraints_to_all_contexts(comb_contexts: List[List[Context]], context_variables_rules: Dict[LTL, List[Type]]):
    copy_list = list(comb_contexts)
    for c_list in copy_list:
        cvars = []
        for c in c_list:
            cvars.extend(c.variables)
        for k, v in context_variables_rules.items():
            if len(list(set(cvars) & set(v))) > 0:
                """They have at least one variables in common, then add rule"""
                c_list.append(Context(k, v))

    return copy_list


def add_constraints_to_goal(goals: List[CGTGoal], context_variables_rules: Dict[LTL, List[Type]]):
    for goal in goals:
        context = goal.context
        if context is not None:
            cvars = context.variables
            for k, v in context_variables_rules.items():
                if len(list(set(cvars) & set(v))) > 0:
                    """They have at least two variables in common, then add rule"""
                    context.merge_with(Context(k, v))
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

            comb_contexts = list(comb).copy()

            comb_contexts_neg = list(comb).copy()

            for ctx in contexts:
                if ctx not in comb_contexts_neg:
                    ctx_vars = ctx.variables
                    ctx_exp = Not(ctx)
                    comb_contexts_neg.append(Context(variables=ctx_vars,
                                                     expression=ctx_exp))

            combs_all_contexts.append(comb_contexts)

            combs_all_contexts_neg.append(comb_contexts_neg)

    return combs_all_contexts, combs_all_contexts_neg


def merge_contexes(contexts: List[List[Context]]) -> Tuple[List[Context], List[Context]]:
    """Merge the consistent contexts with conjunction"""
    contexts_merged: List[Context] = []

    print("\n\nMERGING " + str(len(contexts)) + " CONTEXTS...")

    for group in contexts:
        variables: List[Type] = []
        formulas: List[LTL] = []
        for ctx in group:
            add_variables_to_list(variables, ctx.variables)
            formulas.append(ctx)

        """Conjunction of one consistent context"""
        formula = And(formulas)
        new_ctx = Context(expression=formula, variables=variables)
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
                    if ca.is_included_in(cb):
                        print(str(ca) + "\nINCLUDED IN\n" + str(cb))
                        context_merged_simplified.remove(cb)
                        print(str(cb) + "\nREMOVED (kept smaller)")
                    else:
                        if ca.is_satisfiable_with(cb):
                            mutex = False
            else:
                if (ca is not cb) and \
                        ca in context_merged_simplified:
                    if ca.is_included_in(cb):
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
            else:
                goal_ctx = goal.context
                if GOAL_CTX_SMALLER:
                    """Verify that the goal is included the context"""
                    if goal_ctx.is_included_in(ctx):
                        print("Goal_ctx: " + str(goal_ctx) + " \t-->\t Ctx: " + str(ctx))
                        """Add goal to the context"""
                        if ctx in context_goals:
                            if goal not in context_goals[ctx]:
                                context_goals[ctx].append(goal)
                        else:
                            context_goals[ctx] = [goal]
                else:
                    """Verify that the context is included in goal context"""
                    if ctx.is_included_in(goal_ctx):
                        print("Ctx: " + str(ctx) + " \t-->\t Goal_ctx: " + str(goal_ctx))
                        """Add goal to the context"""
                        if ctx in context_goals:
                            if goal not in context_goals[ctx]:
                                context_goals[ctx].append(goal)
                        else:
                            context_goals[ctx] = [goal]

    """Check all the contexts that point to the same set of goals and take the most abstract one"""
    ctx_removed = []
    context_goals_copy = dict(context_goals)
    for ctxa, goalsa in context_goals_copy.items():

        for ctxb, goalsb in context_goals_copy.items():
            if ctxa in ctx_removed:
                continue
            if ctxb in ctx_removed:
                continue
            if ctxa is not ctxb:
                if set(goalsa) == set(goalsb):
                    if ctxa.is_included_in(ctxb):
                        print(str(ctxa) + "\nINCLUDED IN\n" + str(ctxb))
                        if SAVE_SMALLER_CONTEXT:
                            del context_goals[ctxb]
                            ctx_removed.append(ctxb)
                            print(str(ctxb) + "\nREMOVED")
                        else:
                            del context_goals[ctxa]
                            ctx_removed.append(ctxa)
                            print(str(ctxa) + "\nREMOVED")

    """Check the all the goals have been mapped"""
    all_mapped = True
    for g in goals:
        goal_not_present = True
        for k, v in context_goals.items():
            if g in v:
                goal_not_present = False
                break
        if goal_not_present:
            print("+++++CAREFUL+++++++")
            print(g.name + ": " + str(g.context) + " not mapped to any goal")
            all_mapped = False
            # raise Exception("Some goals have not been mapped to the context!")

    if all_mapped:
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
        contract.add_assumption(Not(Or(stronger_assumptions_list)))
