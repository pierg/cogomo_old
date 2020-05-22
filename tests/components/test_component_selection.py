from src.contracts.operations import compose_contracts
from src.components.operations import *
from src.contracts.contract import *


def test_component_selection():
    component_library = ComponentsLibrary(name="cogomoLTL")

    component_library.add_components(
        [
            SimpleComponent(component_id="c0",
                            assumptions=["a"],
                            guarantees=["b"]),
            SimpleComponent(component_id="c9",
                            assumptions=["l"],
                            guarantees=["p"]),
            SimpleComponent(component_id="c10",
                            assumptions=["o"],
                            guarantees=["a"]),
            SimpleComponent(component_id="c1-default",
                            assumptions=["a", "p"],
                            guarantees=["b", "x > 5"]),
            SimpleComponent(component_id="c2_conditional_scope_no_context",
                            assumptions=["b", "x > 10"],
                            guarantees=["y > 20"]),
            SimpleComponent(component_id="c3",
                            assumptions=["b", "x > 3"],
                            guarantees=["y > 40"])
        ]
    )

    specification = SimpleContract(guarantees=["y > 10"])

    components, hierarchy = components_selection(component_library, specification)

    composition = compose_contracts(components)

    ids = []
    for c in components:
        ids.append(c.id)
    print(ids)

    assert all(cid in ids for cid in ['c3', 'c9', 'c10', 'c1-default'])

    # assert all(g in composition.guarantees.list for g in [LTL("(a & p -> b)"),
    #                                                       LTL("(a & p -> x > 5)"),
    #                                                       LTL("(o -> a)"),
    #                                                       LTL("(b & x > 3 -> y > 40)"),
    #                                                       LTL("(l -> p)")])
