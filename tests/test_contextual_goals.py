from src.goals.cgtgoal import *
from src.contracts.contract import *
from src.goals.operations import *
#
# list_of_goals_1 = [
#     CGTGoal(
#         context=({"x": "0..100"},
#                  ["x > 10"]),
#         name="contract_1",
#         contracts=[BooleanContract(["a"], ["b"])]
#     ),
#     CGTGoal(
#         context=({"x": "0..100"},
#                  ["x > 13"]),
#         name="contract_2",
#         contracts=[BooleanContract(["c"], ["d"])]
#     ),
#     CGTGoal(
#         context=({"x": "0..100"},
#                  ["x > 10"]),
#         name="contract_6",
#         contracts=[BooleanContract(["k"], ["p"])]
#     ),
#     CGTGoal(
#         context=({"x": "0..100"},
#                  ["x <= 10"]),
#         name="contract_3",
#         contracts=[BooleanContract(["e"], ["f"])]
#     ),
#     CGTGoal(
#         context=({"x": "0..100"},
#                  ["x <= 10"]),
#         name="contract_4",
#         contracts=[BooleanContract(["g"], ["h"])]
#     ),
#     CGTGoal(
#         context=({"y": "0..100"},
#                  ["y > 23"]),
#         name="contract_9",
#         contracts=[BooleanContract(["g"], ["h"])]
#     ),
#     CGTGoal(
#         context=({"y": "0..100", "x": "0..100"},
#                  ["y > 23", "x > 15"]),
#         name="contract_10",
#         contracts=[BooleanContract(["g"], ["h"])]
#     ),
#     CGTGoal(
#         context=None,
#         name="contract_5",
#         contracts=[BooleanContract(["i"], ["l"])]
#     )
# ]

list_of_goals_2 = [
    CGTGoal(
        context=({"x": "boolean"},
                 ["x"]),
        name="contract_1",
        contracts=[BooleanContract(["a"], ["b"])]
    ),
    CGTGoal(
        context=({"y": "boolean"},
                 ["y"]),
        name="contract_2",
        contracts=[BooleanContract(["c"], ["d"])]
    ),
    CGTGoal(
        context=({"x": "boolean", "y": "boolean"},
                 ["x", "y"]),
        name="contract_6",
        contracts=[BooleanContract(["k"], ["p"])]
    ),
    CGTGoal(
        context=({"z": "boolean", "y": "boolean"},
                 ["z", "y"]),
        name="contract_3",
        contracts=[BooleanContract(["e"], ["f"])]
    ),
    CGTGoal(
        context=({"z": "boolean", "x": "boolean"},
                 ["!z", "x"]),
        name="contract_4",
        contracts=[BooleanContract(["g"], ["h"])]
    )
]


cgt = create_contextual_cgt(list_of_goals_2)

print(cgt)
