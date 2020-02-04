





def prioritize_goal(first_priority_goal, second_priority_goal):
    """
    Makes the assumption of one goal dependent on the satisfiability of the assumptions of the second goal
    """
    variables = {}
    stronger_assumptions_list = []

    for contract in first_priority_goal.contracts:
        variables.update(contract.variables)
        stronger_assumptions_list.append(And(contract.assumptions))

    for contract in second_priority_goal.contracts:
        contract.add_variables(variables)
        contract.add_assumption(Not(Or(stronger_assumptions_list)))

