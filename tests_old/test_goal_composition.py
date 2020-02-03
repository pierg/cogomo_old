from src.helper.parser import *
from src.goals.operations import *

"""Parse Goals from Structured Text File"""

goals = parse('./input_files/test_composition.txt')

list_of_goals = [
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
    ),
    CGTGoal(
        context=None,
        name="goal_4",
        contracts=[BooleanContract(["g"], ["h"])]
    ),
    CGTGoal(
        context=None,
        name="goal_5",
        contracts=[BooleanContract(["f"], ["h"])]
    )
]


def test_two_contracts_composition():

    goal_composed = composition(
        [goals["goal_1"], goals["goal_2"]],
        name="goal_composed",
        description="description of goal_composed")

    assert goal_composed.get_ltl_assumptions() == "a & c"



