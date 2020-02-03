from src.components.operations import *
from src.goals.operations import *
from src.helper.parser import parse

component_library = ComponentsLibrary(name="cogomoLTL")

component_library.add_components(
    [
        Component(id="c0",
                  variables={"a": "boolean", "b": "boolean"},
                  assumptions=["a"],
                  guarantees=["b"]),
        Component(id="c1",
                  variables={"a": "boolean", "b": "boolean", "x": "0..100", "l": "boolean", "kp": "boolean"},
                  assumptions=["a", "l", "kp"],
                  guarantees=["b", "x > 5"]),
        Component(id="c2",
                  variables={"b": "boolean", "x": "0..100", "y": "0..100"},
                  assumptions=["b", "x > 10"],
                  guarantees=["y > 20"]),
        Component(id="c3",
                  variables={"b": "boolean", "x": "0..100", "y": "0..100"},
                  assumptions=["b", "x > 3"],
                  guarantees=["y > 40"]),
    ])

spec_a = []
spec_g = ["y > 40"]

if __name__ == '__main__':

    goals = parse('../input_files/test_consolidation.txt')

    cgt = conjunction(
        [goals["goal_1"], goals["goal_2"], goals["goal_3"]],
        name="goal_conjoined",
        description="description of goal_conjoined")

    cgt = composition(
        [cgt, goals["goal_4"], goals["goal_5"]],
        name="goal_composed",
        description="description of goal_composed")

    print(cgt)

    """Let's look for a refinement of the only contract in goal 2"""
    mapping(component_library, goals["goal_2"])

    print(cgt)
