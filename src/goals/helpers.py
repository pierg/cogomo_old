





def prioritize_goal(first_priority_goal, second_priority_goal):
    """
    Makes the assumption of one goal dependent on the satisfiability of the assumptions of the second goal
    """
    variables = {}
    stronger_assumptions_list = []

    for contract in first_priority_goal.get_contracts():
        variables.update(contract.get_variables())
        stronger_assumptions_list.append(And(contract.get_list_assumptions()))

    for contract in second_priority_goal.get_contracts():
        contract.merge_variables(variables)
        contract.add_assumption(Not(Or(stronger_assumptions_list)))

