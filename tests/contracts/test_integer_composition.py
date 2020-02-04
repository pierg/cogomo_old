from src.contracts.operations import *


def test_one_integer_contracts_with_guarantees_simplifiable():
    contract = Contract(
        variables={"a": "-50..50", "b": "-50..50"},
        assumptions=["a > 10", "a > 30"],
        guarantees=["b < 5", "b < 10"]
    )
    print(contract)
    assert contract.unsaturated_guarantees == ["b < 5"]
    assert contract.assumptions == ["a > 10"]


def test_one_integer_contracts_with_guarantees_simplifiable_add_guarantee():
    contract = Contract(
        variables={"a": "-50..50", "b": "-50..50"},
        assumptions=["a > 10", "a > 30"],
        guarantees=["b < 5", "b < 10"]
    )
    print(contract)
    contract.add_guarantee("b < 2")
    print(contract)
    assert contract.unsaturated_guarantees == ["b < 2"]


def test_one_integer_contracts_with_guarantees_simplifiable_add_assumption():
    contract = Contract(
        variables={"a": "-50..50", "b": "-50..50"},
        assumptions=["a > 10", "a > 30"],
        guarantees=["b < 5", "b < 10"]
    )
    print(contract)
    contract.add_assumption("a > 2")
    print(contract)
    assert contract.assumptions == ["a > 2"]


def test_two_integer_contracts():
    list_contracts = [
        Contract(
            variables={"a": "-50..50", "b": "-50..50"},
            assumptions=["a > 10", "a > 30"],
            guarantees=["b < 5", "b < 10"]
        ),
        Contract(
            variables={"c": "-50..50", "d": "-50..50"},
            assumptions=["c > 10", "c > 30"],
            guarantees=["d < 5", "d < 10"]
        )
    ]
    composition = compose_contracts(list_contracts)

    assert composition.assumptions == ["a > 10", "c > 10"]
    assert composition.guarantees == ["(a > 10 -> b < 5)", "(c > 10 -> d < 5)"]
    assert composition.unsaturated_guarantees == ["b < 5", "d < 5"]


def test_two_integer_contracts_with_assumption_simplification():
    list_contracts = [
        Contract(
            variables={"a": "-50..50", "b": "-50..50"},
            assumptions=["a > 10"],
            guarantees=["b < 5"]
        ),
        Contract(
            variables={"b": "-50..50", "c": "-50..50"},
            assumptions=["b < 10"],
            guarantees=["c > 22"]
        )
    ]
    composition = compose_contracts(list_contracts)

    assert composition.assumptions == ["a > 10"]
    assert composition.guarantees == ["(a > 10 -> b < 5)", "(b < 10 -> c > 22)"]
    assert composition.unsaturated_guarantees == ["b < 5", "c > 22"]



def test_two_integer_contracts_without_assumption_simplification():
    list_contracts = [
        Contract(
            variables={"a": "-50..50", "b": "-50..50"},
            assumptions=["a > 10", "a > 30"],
            guarantees=["b < 5", "b < 10"]
        ),
        Contract(
            variables={"b": "-50..50", "c": "-50..50"},
            assumptions=["b < 2"],
            guarantees=["c > 22"]
        )
    ]
    composition = compose_contracts(list_contracts)

    assert composition.assumptions == ["a > 10", "b < 2"]
    assert composition.guarantees == ["(a > 10 -> b < 5)", "(b < 2 -> c > 22)"]
    assert composition.unsaturated_guarantees == ["b < 5", "c > 22"]
