from src.helper.parser import *
from src.goals.operations import *

"""Parse Goals from Structured Text File"""

two_boolean_goals = [
    CGTGoal(
        name="goal_1",
        contracts=[BooleanContract(["a"], ["b"])]
    ),
    CGTGoal(
        name="goal_2",
        contracts=[BooleanContract(["c"], ["d"])]
    )
]


three_boolean_goals = [
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

def test_two_contracts_composition():

    goal_composed = composition(
        two_boolean_goals,
        name="goal_composed",
        description="description of goal_composed")

    assert is_implied_in(
        variables=goal_composed.get_list_contracts()[0].variables,
        formula_a=goal_composed.get_ltl_assumptions(),
        formula_b="a & c")


def test_three_contracts_composition():

    goal_composed = composition(
        three_boolean_goals,
        name="goal_composed",
        description="description of goal_composed")

    assert goal_composed.get_ltl_assumptions() == "a & c & e"


