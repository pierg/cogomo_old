from goals.context import Context
from src.contracts.contract import *
from src.goals.operations import *

def test_context_booleans_1():
    list_of_goals = [
        CGTGoal(
            context=(Context(LTL("x"))),
            name="g1",
            contracts=[BooleanContract(["ax"], ["bx"])]
        ),
        CGTGoal(
            context=(Context(LTL("y"))),
            name="g2",
            contracts=[BooleanContract(["ay"], ["by"])]
        ),
        CGTGoal(
            context=(Context(LTL("z"))),
            name="g3",
            contracts=[BooleanContract(["az"], ["gz"])]
        )
    ]
    cgt = create_contextual_simple_cgt(list_of_goals)
    save_to_file(str(cgt), "test_context_booleans_1")

def test_context_booleans_2():
    list_of_goals = [
        CGTGoal(
            context=(Context(LTL("!x"))),
            name="g1",
            contracts=[BooleanContract(["ax"], ["bx"])]
        ),
        CGTGoal(
            context=(Context(LTL("x"))),
            name="g2",
            contracts=[BooleanContract(["ay"], ["by"])]
        ),
        CGTGoal(
            context=(Context(LTL("y"))),
            name="g3",
            contracts=[BooleanContract(["az"], ["gz"])]
        )
    ]
    cgt = create_contextual_simple_cgt(list_of_goals)
    save_to_file(str(cgt), "test_context_booleans_2")

def test_context_booleans_3():
    list_of_goals = [
        CGTGoal(
            context=(Context(LTL("x"))),
            name="g1",
            contracts=[BooleanContract(["a"], ["b"])]
        ),
        CGTGoal(
            context=(Context(LTL("!y"))),
            name="g2",
            contracts=[BooleanContract(["ad"], ["bd"])]
        ),
        CGTGoal(
            context=(Context(LTL("y"))),
            name="g3",
            contracts=[BooleanContract(["c"], ["d"])]
        ),
        CGTGoal(
            context=(Context(LTL("x|z"))),
            name="g4",
            contracts=[BooleanContract(["k"], ["p"])]
        ),
        CGTGoal(
            context=(Context(LTL("z"))),
            name="g5",
            contracts=[BooleanContract(["k2"], ["p2"])]
        ),
        CGTGoal(
            context=(Context(LTL("!z"))),
            name="g6",
            contracts=[BooleanContract(["k3"], ["p4"])]
        )
    ]
    cgt = create_contextual_simple_cgt(list_of_goals)
    save_to_file(str(cgt), "test_context_booleans_3")



def test_context_integer_simple():
    list_of_goals = [
        CGTGoal(
            context=(Context(LTL("y > 5"))),
            name="g1",
            contracts=[BooleanContract(["a"], ["b"])]
        ),
        CGTGoal(
            context=(Context(LTL("x > 1"))),
            name="g2",
            contracts=[BooleanContract(["a1"], ["b1"])]
        ),
        CGTGoal(
            context=(Context(LTL("x > 6"))),
            name="g3",
            contracts=[BooleanContract(["a"], ["b"])]
        ),
        CGTGoal(
            context=(Context(LTL("x < 5"))),
            name="g4",
            contracts=[BooleanContract(["c"], ["d"])]
        ),
        CGTGoal(
            context=(Context(LTL("x < 3"))),
            name="g5",
            contracts=[BooleanContract(["k"], ["p"])]
        ),
        CGTGoal(
            context=(Context(LTL("x < 10"))),
            name="g6",
            contracts=[BooleanContract(["kd"], ["pf"])]
        )
    ]

    cgt = create_contextual_simple_cgt(list_of_goals)
    save_to_file(str(cgt), "test_context_integer_simple")


def test_context_integer():
    list_of_goals = [
        CGTGoal(
            context=(Context(LTL("y > 5"))),
            name="g1",
            contracts=[BooleanContract(["a"], ["b"])]
        ),
        CGTGoal(
            context=(Context(LTL("x > 6"))),
            name="g2",
            contracts=[BooleanContract(["a"], ["b"])]
        ),
        CGTGoal(
            context=(Context(LTL("x < 5"))),
            name="g3",
            contracts=[BooleanContract(["c"], ["d"])]
        ),
        CGTGoal(
            context=(Context(LTL("x < 3"))),
            name="g4",
            contracts=[BooleanContract(["k"], ["p"])]
        ),
        CGTGoal(
            context=(Context(LTL("x < 7 & x !=5"))),
            name="g5",
            contracts=[BooleanContract(["kd"], ["pf"])]
        ),
        CGTGoal(
            context=(Context(LTL("x = 5"))),
            name="g6",
            contracts=[BooleanContract(["kd"], ["pf"])]
        )
    ]

    cgt = create_contextual_simple_cgt(list_of_goals)
    save_to_file(str(cgt), "test_context_integer")


