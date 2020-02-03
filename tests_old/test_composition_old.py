from src.helper.parser import *
from src.goals.operations import *

"""Parse Goals from Structured Text File"""

goals = parse('./input_files/test_composition.txt')


goal_composed = composition(
    [goals["goal_1"], goals["goal_2"]],
    name="goal_composed",
    description="description of goal_composed")

print(goal_composed)

