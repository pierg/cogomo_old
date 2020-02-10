from typing import Union, Dict, List

from goals.cgtgoal import CGTGoal


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
