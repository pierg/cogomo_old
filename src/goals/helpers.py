import itertools
from typing import Union, Dict, List, Tuple

from checks.nsmvhelper import add_variables_to_list
from checks.nusmv import check_satisfiability
from contracts.formulas import LTL
from contracts.types import Type
from goals.cgtgoal import CGTGoal
from goals.context import Context
from helper.logic import Not, And


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


def extract_all_combinations_and_negations_from_contexts(contexts: List[Context]) \
        -> Tuple[List[List[Context]], List[List[Context]]]:
    """Extract the combinations of all contexts"""
    combs_all_contexts: List[List[Context]] = []

    """Extract the combinations of all contextes with negations"""
    combs_all_contexts_neg: List[List[Context]] = []

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

    return combs_all_contexts, combs_all_contexts_neg


def merge_contexes(contexts: List[List[Context]]) -> Tuple[List[Context], List[Context]]:
    """Merge the consistent contextes with conjunction"""
    contexts_merged: List[Context] = []

    for group in contexts:
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

    context_merged_simplified = contexts_merged.copy()
    mutex = True
    for ca in list(context_merged_simplified):
        for cb in list(context_merged_simplified):
            if ca is not cb:
                if ca.is_satisfiable_with(cb):
                    print(str(ca) + "  SAT WITH   " + str(cb))
                    mutex = False
                if ca.is_included_in(cb):
                    print(str(ca) + "  INCLUDED IN   " + str(cb))
                    context_merged_simplified.remove(ca)
                    break

    if mutex:
        print("All contexts are mutually exclusive")

    return contexts_merged, context_merged_simplified


def map_goals_to_contexts(contexts: List[Context], goals: List[CGTGoal], refined=False) -> Dict[Context, List[CGTGoal]]:
    """Map each goal to each context, refined indicates if among a two elements pointing at the same goal
    it must be taken the most reefined, otherwise the most abstract (in tems of context) is taken"""

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
                """Verify that the context is an abstraction of the goal context"""
                goal_ctx = goal.context
                if ctx.is_included_in(goal_ctx):
                    """Add goal to the context"""
                    if ctx in context_goals:
                        if goal not in context_goals[ctx]:
                            context_goals[ctx].append(goal)
                    else:
                        context_goals[ctx] = [goal]

    """Check all the contexts that point to the same set of goals and take the most abstract/refined one"""
    for ctxa, goalsa in dict(context_goals).items():

        for ctxb, goalsb in dict(context_goals).items():
            if ctxa is not ctxb:
                if set(goalsa) == set(goalsb):
                    if refined:
                        if ctxa.is_included_in(ctxb):
                            print("Simplifying " + str(ctxa))
                            del context_goals[ctxb]
                    else:
                        if ctxa.is_included_in(ctxb):
                            print("Simplifying " + str(ctxa))
                            del context_goals[ctxa]

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
