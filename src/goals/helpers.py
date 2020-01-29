
from src.goals.operations import *


def consolidate(cgt: CGTGoal):
    """It recursivly re-perfom composition and conjunction operations up to the rood node"""

    parent = cgt.get_parent()
    if parent is None:
        return

    if parent.get_sub_operation() == "CONJUNCTION":
        parent = conjunction(
            parent.get_sub_goals(),
            parent.get_name(),
            parent.get_description()
        )

    elif parent.get_sub_operation() == "COMPOSITION":
        parent = compostion(
            parent.get_sub_goals(),
            parent.get_name(),
            parent.get_description()
        )

    consolidate(parent)




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




def propagate_assumptions(abstract_goal, refined_goal):
    """

    :return:
    """
    contracts_refined = refined_goal.get_contracts()
    contracts_abstracted = abstract_goal.get_contracts()

    if len(contracts_refined) != len(contracts_abstracted):
        raise Exception("Propagating assumptions among goals with different number of conjoined contracts")

    for i, contract in enumerate(contracts_refined):
        """And(.....) of all the assumptions of the abstracted contract"""
        assumptions_abs_ltl = contracts_abstracted[i].get_ltl_assumptions()
        """List of all the assumptions of the refined contract"""
        assumptions_ref = contract.get_list_assumptions()
        assumptions_to_add = []
        for assumption in assumptions_ref:
            if not is_set_smaller_or_equal(assumptions_abs_ltl, assumption):
                assumptions_to_add.append(assumption)

        """Unify alphabets"""
        contracts_abstracted[i].merge_variables(contract.get_variables())
        contracts_abstracted[i].add_assumptions(assumptions_to_add)



