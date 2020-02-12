from goals.context import Context
from src.contracts.contract import *
from src.goals.operations import *

def test_context_booleans():
    list_of_goals2 = [
        CGTGoal(
            context=(Context(LTL("x"))),
            name="contract_1",
            contracts=[BooleanContract(["a"], ["b"])]
        ),
        CGTGoal(
            context=(Context(LTL("!x"))),
            name="contract_3",
            contracts=[BooleanContract(["ad"], ["bd"])]
        )
    ]

    list_of_goals = [
        CGTGoal(
            context=(Context(LTL("x"))),
            name="contract_1",
            contracts=[BooleanContract(["a"], ["b"])]
        ),
        CGTGoal(
            context=(Context(LTL("!y"))),
            name="contract_3",
            contracts=[BooleanContract(["ad"], ["bd"])]
        ),
        CGTGoal(
            context=(Context(LTL("y"))),
            name="contract_2",
            contracts=[BooleanContract(["c"], ["d"])]
        ),
        CGTGoal(
            context=(Context(LTL("x|z"))),
            name="contract_6",
            contracts=[BooleanContract(["k"], ["p"])]
        ),
        CGTGoal(
            context=(Context(LTL("z"))),
            name="contract_7",
            contracts=[BooleanContract(["k2"], ["p2"])]
        ),
        CGTGoal(
            context=(Context(LTL("!z"))),
            name="contract_8",
            contracts=[BooleanContract(["k3"], ["p4"])]
        )
    ]

    cgt = create_contextual_cgt(list_of_goals)

    save_to_file(str(cgt), "context_cgt.txt")


def test_context_integer_simple():
    list_of_goals = [
        CGTGoal(
            context=(Context(LTL("y > 5"))),
            name="contract_1",
            contracts=[BooleanContract(["a"], ["b"])]
        ),
        CGTGoal(
            context=(Context(LTL("x > 1"))),
            name="contract_11",
            contracts=[BooleanContract(["a1"], ["b1"])]
        ),
        CGTGoal(
            context=(Context(LTL("x > 6"))),
            name="contract_1",
            contracts=[BooleanContract(["a"], ["b"])]
        ),
        CGTGoal(
            context=(Context(LTL("x < 5"))),
            name="contract_2",
            contracts=[BooleanContract(["c"], ["d"])]
        ),
        CGTGoal(
            context=(Context(LTL("x < 3"))),
            name="contract_6",
            contracts=[BooleanContract(["k"], ["p"])]
        ),
        CGTGoal(
            context=(Context(LTL("x < 10"))),
            name="contract_55",
            contracts=[BooleanContract(["kd"], ["pf"])]
        )
    ]

    cgt = create_contextual_cgt(list_of_goals)

    save_to_file(str(cgt), "context_cgt_integer.txt")

def test_context_integer():
    list_of_goals = [
        CGTGoal(
            context=(Context(LTL("y > 5"))),
            name="contract_1",
            contracts=[BooleanContract(["a"], ["b"])]
        ),
        CGTGoal(
            context=(Context(LTL("x > 6"))),
            name="contract_1",
            contracts=[BooleanContract(["a"], ["b"])]
        ),
        CGTGoal(
            context=(Context(LTL("x < 5"))),
            name="contract_2",
            contracts=[BooleanContract(["c"], ["d"])]
        ),
        CGTGoal(
            context=(Context(LTL("x < 3"))),
            name="contract_6",
            contracts=[BooleanContract(["k"], ["p"])]
        ),
        CGTGoal(
            context=(Context(LTL("x < 7 & x !=5"))),
            name="contract_55",
            contracts=[BooleanContract(["kd"], ["pf"])]
        ),
        CGTGoal(
            context=(Context(LTL("x = 5"))),
            name="contract_55",
            contracts=[BooleanContract(["kd"], ["pf"])]
        )
    ]

    cgt = create_contextual_cgt(list_of_goals)

    save_to_file(str(cgt), "context_cgt_integer")


