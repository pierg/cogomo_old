from src.components.operations import *
from src.goals.operations import *

component_library = ComponentsLibrary(name="cogomoLTL")

component_library.add_components(
    [
        Component(id="c0",
                  variables={"a": "boolean", "b": "boolean"},
                  assumptions=["a"],
                  guarantees=["b"]),
        Component(id="c1",
                  variables={"a": "boolean", "b": "boolean", "x": "0..100", "l": "boolean", "k": "boolean"},
                  assumptions=["a", "l", "k"],
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

    specification = Contract(variables={"y": "0..100"}, guarantees=["y > 10"])

    goal = mapping(component_library, specification)

    print(goal)
