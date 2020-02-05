from src.helper.parser import *
from src.goals.operations import *

def test_two_contracts_composition():
    goal_list = [
        CGTGoal(
            name="goal_1",
            contracts=[BooleanContract(["a"], ["b"])]
        ),
        CGTGoal(
            name="goal_2",
            contracts=[BooleanContract(["c"], ["d"])]
        )
    ]

    goal_composed = composition(
        goal_list,
        name="goal_composed",
        description="description of goal_composed")

    print(goal_composed)

    assert is_implied_in(
        variables=goal_composed.contracts[0].variables,
        antecedent=goal_composed.get_ltl_assumptions(),
        consequent="a & c")


def test_three_contracts_composition():

    goal_list = [
        CGTGoal(
            name="goal_1",
            contracts=[BooleanContract(["a"], ["b"])]
        ),
        CGTGoal(
            name="goal_2",
            contracts=[BooleanContract(["c"], ["d"])]
        ),
        CGTGoal(
            name="goal_3",
            contracts=[BooleanContract(["e"], ["f"])]
        )
    ]

    goal_composed = composition(
        goal_list,
        name="goal_composed",
        description="description of goal_composed")

    print(goal_composed)

    assert goal_composed.get_ltl_assumptions() == "a & c & e"


def test_three_contracts_composition():

    goal_list = [
        CGTGoal(
            name="goal_1",
            contracts=[BooleanContract(["a"], ["b"])]
        ),
        CGTGoal(
            name="goal_2",
            contracts=[BooleanContract(["c"], ["d"])]
        ),
        CGTGoal(
            name="goal_3",
            contracts=[BooleanContract(["e"], ["f"])]
        )
    ]

    goal_composed = composition(
        goal_list,
        name="goal_composed",
        description="description of goal_composed")

    print(goal_composed)

    assert goal_composed.get_ltl_assumptions() == "a & c & e"


