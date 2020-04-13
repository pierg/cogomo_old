from src.goals.operations import composition
from src.contracts.contract import *
from src.goals.cgtgoal import *


def test_composition_pointers():
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

    cgt = composition(
        goal_list,
        name="goal_composed",
        description="description of goal_composed")

    new_goal = CGTGoal(
        name="goal_2",
        contracts=[BooleanContract(["e"], ["f"])]
    )

    print(cgt)
    print(goal_list[0])
    goal_list[0] = composition([goal_list[0], new_goal])
    print(goal_list[0])
    print(cgt)


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

    assert str(goal_composed.get_ltl_assumptions()) == "((a & c) & e)"
