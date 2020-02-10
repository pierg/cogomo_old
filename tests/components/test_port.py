from src.components.operations import *


def test_port():

    components = [
        Component(
            component_id="robot_1",
            variables=[BoundedInt("a")],
            guarantees=["a > 3"],
        ),
        Component(
            component_id="robot_2",
            variables=[BoundedIntPort(port_type="a", name="a_name")],
            guarantees=["a_name >= 8"],
        ),
        Component(
            component_id="robot_3",
            variables=[BoundedInt("a")],
            guarantees=["a >= 9"],
        ),
        Component(
            component_id="robot_4",
            variables=[BoundedIntPort(port_type="a", name="a_name1"), BoundedIntPort(port_type="a", name="a_name2")],
            guarantees=["a_name1 >= 8", "a_name2 >= 8"],
        ),
        Component(
            component_id="c1",
            variables=[BoundedIntPort(port_type="a", name="a1"),
                       BoundedIntPort(port_type="a", name="a2"),
                       Boolean("b")],
            assumptions=["a1 > 5", "a2 > 5"],
            guarantees=["b"]
        )]


    library = ComponentsLibrary(name="test", components=components)

    specification = Contract(
        variables=[Boolean("b")],
        guarantees=["b"]
    )

    components, hierarchy = components_selection(library, specification)

    print(components)
    print(hierarchy)
