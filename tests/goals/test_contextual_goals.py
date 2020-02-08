from src.contracts.contract import *
from src.goals.operations import *


def test_context_simple():
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


def test_empty_context():
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
