from src.components.operations import *


def test_port():

    components = [
        Component(
            component_id="robot_1",
            variables={"a": "0..15"},
            guarantees=["a > 3"],
        ),
        Component(
            component_id="robot_2",
            variables={"a": "0..15"},
            guarantees=["a >= 8"],
        ),
        Component(
            component_id="robot_3",
            variables={"a": "0..15"},
            guarantees=["a >= 9"],
        ),
        Component(
            component_id="c1",
            variables={"a_port_1": "0..15", "a_port_2": "0..15",
                       "b": "boolean"},
            assumptions=["a_port_1 > 5", "a_port_2 > 5"],
            guarantees=["b"]
        )]

    library = ComponentsLibrary(name="test", components=components)

    specification = Contract(variables={"b": "boolean"}, guarantees=["b"])

    components, hierarchy = components_selection(library, specification)

    print(components)
    print(hierarchy)
