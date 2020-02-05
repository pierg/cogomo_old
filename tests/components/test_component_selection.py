from src.components.operations import *
from src.contracts.operations import *


def test_component_selection():
    component_library = ComponentsLibrary(name="cogomoLTL")

    component_library.add_components(
        [
            Component(component_id="c0",
                      variables={"a": "boolean", "b": "boolean"},
                      assumptions=["a"],
                      guarantees=["b"]),
            Component(component_id="c9",
                      variables={"l": "boolean", "p": "boolean"},
                      assumptions=["l"],
                      guarantees=["p"]),
            Component(component_id="c10",
                      variables={"a": "boolean", "o": "boolean"},
                      assumptions=["o"],
                      guarantees=["a"]),
            Component(component_id="c1",
                      variables={"a": "boolean", "b": "boolean", "p": "boolean", "x": "0..100"},
                      assumptions=["a", "p"],
                      guarantees=["b", "x > 5"]),
            Component(component_id="c2",
                      variables={"b": "boolean", "x": "0..100", "y": "0..100"},
                      assumptions=["b", "x > 10"],
                      guarantees=["y > 20"]),
            Component(component_id="c3",
                      variables={"b": "boolean", "x": "0..100", "y": "0..100"},
                      assumptions=["b", "x > 3"],
                      guarantees=["y > 40"])
        ]
    )

    specification = Contract(variables={"y": "0..100"}, guarantees=["y > 10"])

    components, hierarchy = components_selection(component_library, specification)

    composition = compose_contracts(components)

    ids = []
    for c in components:
        ids.append(c.id)
    print(ids)

    assert all(cid in ids for cid in ['c3', 'c9', 'c10', 'c1'])

    assert all(g in composition.guarantees for g in ["(a & p -> b)",
                                                     "(a & p -> x > 5)",
                                                     "(o -> a)",
                                                     "(b & x > 3 -> y > 40)",
                                                     "(l -> p)"])
