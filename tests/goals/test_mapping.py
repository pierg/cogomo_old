from src.components.operations import *
from src.goals.operations import *


def test_mapping_simple():
    component_library = ComponentsLibrary(name="cogomoLTL")

    component_library.add_components(
        [
            Component(component_id="c0",
                      variables={"a": "boolean", "b": "boolean"},
                      assumptions=["a"],
                      guarantees=["b"]),
            Component(component_id="c1",
                      variables={"a": "boolean", "b": "boolean", "x": "0..100", "l": "boolean", "k": "boolean"},
                      assumptions=["a", "l", "k"],
                      guarantees=["b", "x > 5"]),
            Component(component_id="c2",
                      variables={"b": "boolean", "x": "0..100", "y": "0..100"},
                      assumptions=["b", "x > 10"],
                      guarantees=["y > 20"]),
            Component(component_id="c3",
                      variables={"b": "boolean", "x": "0..100", "y": "0..100"},
                      assumptions=["b", "x > 3"],
                      guarantees=["y > 40"]),
        ])

    specification = CGTGoal(
        name="specification",
        contracts=[Contract(variables={"y": "0..100"}, guarantees=["y > 10"])])

    mapping(component_library, specification)

    print(specification)


def test_mapping_simple_ports():
    component_library = ComponentsLibrary(name="cogomoLTL")

    component_library.add_components(
        [
            Component(component_id="c0",
                      variables={"a": "boolean", "b": "boolean"},
                      assumptions=["a"],
                      guarantees=["b"]),
            Component(component_id="c1",
                      variables={"a": "boolean", "b": "boolean", "x": "0..100", "l": "boolean", "k": "boolean"},
                      assumptions=["a_port_1", "a_port_2", "l", "k"],
                      guarantees=["b", "x > 5"]),
            Component(component_id="c2",
                      variables={"b": "boolean", "x": "0..100", "y": "0..100"},
                      assumptions=["b", "x > 10"],
                      guarantees=["y > 20"]),
            Component(component_id="c3",
                      variables={"b": "boolean", "x": "0..100", "y": "0..100"},
                      assumptions=["b", "x > 3"],
                      guarantees=["y > 40"]),
        ])

    specification = CGTGoal(
        name="specification",
        contracts=[Contract(variables={"y": "0..100"}, guarantees=["y > 10"])])

    mapping(component_library, specification)

    print(specification)


def test_mapping():
    component_library = ComponentsLibrary(name="cogomoLTL")

    component_library.add_components(
        [
            Component(component_id="c0",
                      variables={"a": "boolean", "b": "boolean"},
                      assumptions=["a"],
                      guarantees=["b"]),
            Component(component_id="c1",
                      variables={"a": "boolean", "b": "boolean", "x": "0..100", "l": "boolean", "k": "boolean"},
                      assumptions=["a", "l", "k"],
                      guarantees=["b", "x > 5"]),
            Component(component_id="c2",
                      variables={"b": "boolean", "x": "0..100", "y": "0..100"},
                      assumptions=["b", "x > 10"],
                      guarantees=["y > 20"]),
            Component(component_id="c3",
                      variables={"b": "boolean",
                                 "x": "0..100",
                                 "y": "0..100",
                                 "t": "boolean",
                                 "r": "boolean",
                                 "e": "boolean"
                                 },
                      assumptions=["b", "x > 3", "t", "r", "e"],
                      guarantees=["y > 40"]),
            BooleanComponent(component_id="c9",  assumptions=["a3"], guarantees=["t"]),
            BooleanComponent(component_id="c10", assumptions=["a2"], guarantees=["r"]),
            BooleanComponent(component_id="c11", assumptions=["a1"], guarantees=["e"]),
            BooleanComponent(component_id="c12", assumptions=["b"],  guarantees=["a3"]),
            BooleanComponent(component_id="c5",  assumptions=["a"],  guarantees=["a2"]),
            BooleanComponent(component_id="c6",  assumptions=["r4"], guarantees=["a1"]),
            BooleanComponent(component_id="c7",  assumptions=["r4"], guarantees=["a3"]),
            BooleanComponent(component_id="c8",  assumptions=["t4"], guarantees=["r4"])
        ])

    specification = CGTGoal(
        name="specification",
        contracts=[Contract(variables={"y": "0..100"}, guarantees=["y > 10"])])

    mapping(component_library, specification)

    print(specification)