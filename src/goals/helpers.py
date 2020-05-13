import itertools
from copy import deepcopy
from typing import Union, Dict, List, Tuple
from checks.tools import Not, Or, And, Implies
from helper.tools import traslate_boolean
from typescogomo.assumption import Context
from typescogomo.formulae import LTLs, Assumptions
from typescogomo.formula import LTL, InconsistentException
from typescogomo.variables import Type, Variables
from goals.cgtgoal import CGTGoal


def context_based_specification_clustering(combinations: List[List[Context]],
                                           rules: List[LTL],
                                           goals,
                                           KEEP_SMALLER_COMBINATION,
                                           GOAL_CTX_SAT,
                                           GOAL_CTX_SMALLER,
                                           SAVE_SMALLER_CONTEXT):
    """Add constaints to the context combinations"""
    if rules is not None:
        add_constraints_to_all_contexts(combinations, rules, add_to_all=True)

    print("\n\n__ALL_COMBINATIONS_(" + str(
        len(combinations)) + ")___________________________________________________________")
    for c_list in combinations:
        print(*c_list, sep='\t\t\t')

    """Filter from combinations the comb that are satisfiable and if they are then simplify and merge them"""
    merged, merged_simplified = merge_contexes(combinations, KEEP_SMALLER_COMBINATION)

    print("\n\n__MERGED_____________________________________________________________________")
    print(*merged, sep='\n')

    # print("\n\n__MERGED_AND_GROUPED_________________________________________________________")
    # print(*merged_simplified, sep='\n')

    contexts_list = merged_simplified

    context_goals = map_goals_to_contexts(contexts_list, goals, GOAL_CTX_SAT, GOAL_CTX_SMALLER, SAVE_SMALLER_CONTEXT)

    return context_goals


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


def filter_and_simplify_contexts(contexts: List[List[Context]], KEEP_SMALLER_CONTEXT) -> List[List[Context]]:
    new_list: List[List[Context]] = []
    print("\n\nFILTERING " + str(len(contexts)) + " CONTEXTS...")

    for c_list in contexts:
        """Extract formulas and check satisfiability"""
        try:
            LTLs(c_list)
        except InconsistentException:
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
        variables_list: Variables = Variables()
        ltl = "G("
        for vs in cvars:
            variables_list.extend(vs.variables)
        cvars_str = [n.formula for n in cvars]
        clauses = []
        for vs_a in cvars_str:
            clause = []
            clause.append(deepcopy(vs_a))
            for vs_b in cvars_str:
                if vs_a is not vs_b:
                    clause.append(Not(deepcopy(vs_b)))
            clauses.append(And(clause))

        ltl += Or(clauses)
        ltl += ")"
        ltl_list.append(LTL(formula=ltl, variables=variables_list))

    for cvars in context_rules["inclusion"]:
        variables_list_inclusion: Variables = Variables()
        ltl = "G("
        for i, vs in enumerate(cvars):
            variables_list_inclusion.extend(vs.variables)
            ltl += str(vs)
            if i < (len(cvars) - 1):
                ltl += " -> "
        ltl += ")"

        ltl_list.append(LTL(formula=ltl, variables=variables_list_inclusion))

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


def add_constraints_to_all_contexts(comb_contexts: List[List[Context]], rules: List[LTL], add_to_all=False):

    if add_to_all:
        """Add all rules to all the combinations"""
        for comb in comb_contexts:
            for rule in rules:
                comb.append(rule)
    else:
        """Add rules only to the combinations that predicate on the rule"""
        for comb in comb_contexts:
            rules_added = []
            for c in comb:
                for rule in rules:
                    if rule in rules_added:
                        continue
                    if c.variables.n_shared_variables_with(rule.variables) > 0:
                        comb.append(rule)
                        rules_added.append(rule)


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


def merge_contexes(contexts: List[List[Context]], KEEP_SMALLER_COMBINATION) -> Tuple[List[Context], List[Context]]:
    """Merge the consistent contexts with conjunction"""
    contexts_merged: List[Context] = []

    print("\n\nMERGING " + str(len(contexts)) + " CONTEXTS...")

    for group in contexts:
        if len(group) > 0:
            """Extract formulas and check satisfiability, it also filters and simplify each context"""
            try:
                conj = LTLs(group, simplify=False)
            except InconsistentException:
                continue
            new_ctx = Context()
            new_ctx.formula = str(conj.formula)
            new_ctx.variables = conj.variables
            already_there = False
            """"Check if newly created context is not equivalent to an existing previously created context"""
            """Not really needed because we will simplify context later"""
            # for c in contexts_merged:
            #     if c == new_ctx:
            #         already_there = True
            if not already_there:
                contexts_merged.append(new_ctx)

    return contexts_merged, contexts_merged

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


def map_goals_to_contexts(contexts: List[Context], goals: List[CGTGoal], GOAL_CTX_SAT, GOAL_CTX_SMALLER,
                          SAVE_SMALLER_CONTEXT) -> Dict[Context, List[CGTGoal]]:
    """Map each goal to each context """

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
                if GOAL_CTX_SAT:
                    """Verify that the goal-context is satisfiable with the context"""
                    if goal_ctx.is_satisfiable_with(ctx):
                        print("Goal_ctx (" + goal.name + "): " + str(goal_ctx) + " \t-->\t Ctx: " + str(ctx))
                        """Add goal to the context"""
                        if ctx in context_goals:
                            if goal not in context_goals[ctx]:
                                context_goals[ctx].append(goal)
                        else:
                            context_goals[ctx] = [goal]
                        if goal in goals_non_mapped:
                            goals_non_mapped.remove(goal)
                else:
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


def extract_variables_name_from_dics(dics: List[Dict]) -> List[str]:
    vars_name = []
    for d in dics:
        for k, v in d.items():
            for var in v.variables.list:
                vars_name.append(var.name)
    return vars_name


def generate_controller_inputs_from(goals: Union[CGTGoal, List[CGTGoal]],
                                    uncontrollable_vars: List[str],
                                    context_rules: Dict,
                                    domain_rules: Dict,
                                    new_assumptions: LTL = None) -> Tuple[List[str], List[str], List[str], List[str], List[str]]:
    """Goal gaurantees will be saturated with their assumptions or in case of new_assumptions,
    the entire list of goals will be saturated with new_assumptions
    Returns: context_rules, domain_rules, guarantees, uncontrollable, controllable"""
    if isinstance(goals, CGTGoal):
        goals = [goals]

    variables = Variables()

    ctx_rules = []
    dom_rules = []
    guarantees = []
    uncontrollable = []
    controllable = []

    if new_assumptions is None:

        for goal in goals:
            ltl = goal.get_ltl_saturated_guarantees()
            guarantees.append(ltl.formula)
            variables.extend(ltl.variables)
    else:
        guarantees_list = []
        for goal in goals:
            ltl = goal.get_ltl_guarantees()
            guarantees_list.append(ltl.formula)
            variables.extend(ltl.variables)
            guarantees.append(Implies(new_assumptions.formula, And(guarantees_list)))


    for v in variables.list:
        if v.name in uncontrollable_vars:
            uncontrollable.append(v.name)
        else:
            controllable.append(v.name)

    environment_rules = extract_ltl_rules(context_rules)
    domain_rules = extract_ltl_rules(domain_rules)

    for e in environment_rules:
        for v in e.variables.list:
            if v.name not in uncontrollable:
                uncontrollable.append(v.name)
                # raise Exception("variable missing")
        ctx_rules.append(e.formula)

    for e in domain_rules:
        for v in e.variables.list:
            if v.name not in controllable:
                controllable.append(v.name)
                # raise Exception("variable missing")
        dom_rules.append(e.formula)

    return ctx_rules, dom_rules, guarantees, uncontrollable, controllable



def generate_controller_input_text(ctx_rules, dom_rules, guarantees, uncontrollable, controllable):

    ret = "CONSTRAINTS:\n\n"
    for p in ctx_rules:
        ret += p + "\n"
    ret += "\n"
    for p in dom_rules:
        ret += p + "\n"

    ret += "\n\nGUARANTEES:\n\n"
    for p in guarantees:
        ret += p + "\n"

    ret += "\n\nUNCONTROLLABLE:\n\n"
    ret += ", ".join(uncontrollable)

    ret += "\n\nCONTROLLABLE:\n\n"
    ret += ", ".join(controllable)

    return ret

def extract_saturated_guarantees_from(goals: Union[CGTGoal, List[CGTGoal]]) -> List[str]:
    if isinstance(goals, CGTGoal):
        goals = [goals]

    assumptions_goals = []
    guarantees_goals = []
    variables_goals = set()

    for goal in goals:
        goal_variables = set()
        goal_new_variables = set()
        goal_old_variables = set()
        assumptions_guarantee_pairs = []
        for contract in goal.contracts:
            a_boolean, a_new_vars, a_old_vars = traslate_boolean(str(contract.assumptions.formula))
            g_boolean, g_new_vars, g_old_vars = traslate_boolean(str(contract.guarantees.formula))
            vars = [v.name for v in contract.variables.list]
            goal_variables.update(vars)
            a_new_vars.extend(g_old_vars)
            a_old_vars.extend(g_old_vars)
            goal_new_variables.update(a_new_vars)
            goal_old_variables.update(a_old_vars)
            assumptions_guarantee_pairs.append((a_boolean, g_boolean))
        goal_variables = goal_variables - goal_old_variables
        goal_variables.update(goal_new_variables)

        assumptions_goal = Or([a for (a, goal) in assumptions_guarantee_pairs])
        guarantees_goal = And([Implies(a, goal) for (a, goal) in assumptions_guarantee_pairs])

        guarantees_goals.append(guarantees_goal)
        variables_goals.update(goal_variables)

    return guarantees_goals
