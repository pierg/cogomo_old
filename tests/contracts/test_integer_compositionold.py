from src.contracts.operations import *


one_integer_contracts_with_guarantees_simplifiable = [
    Contract(
        variables={"a": "-50..50", "b": "-50..50"},
        assumptions=["a > 10"],
        guarantees=["b < 5", "b < 10"]
    )
]

def test_one_integer_contracts_with_guarantees_simplifiable():
    contract = Contract(
        variables={"a": "-50..50", "b": "-50..50"},
        assumptions=["a > 10"],
        guarantees=["b < 5", "b < 10"]
    )
    print(contract)

one_integer_contracts_with_assumptions_simplifiable = [
    Contract(
        variables={"a": "-50..50", "b": "-50..50"},
        assumptions=["a > 10", "a > 20"],
        guarantees=["b < 5"]
    )
]


two_integer_contracts = [
    Contract(
        variables={"a": "-50..50", "b": "-50..50"},
        assumptions=["a > 10"],
        guarantees=["b < 5"]
    ),
    Contract(
        variables={"c": "-50..50", "d": "-50..50"},
        assumptions=["c > 22"],
        guarantees=["d < 44"]
    ),
]

two_integer_contracts_with_simplification = [
    Contract(
        variables={"a": "-50..50", "b": "-50..50"},
        assumptions=["a > 10"],
        guarantees=["b < 5"]
    ),
    Contract(
        variables={"c": "-50..50", "d": "-50..50"},
        assumptions=["c > 22"],
        guarantees=["d < 44"]
    ),
]

two_integer_contracts_with_guarantees_simplifiable = [
    Contract(
        variables={"a": "-50..50", "b": "-50..50"},
        assumptions=["a > 10"],
        guarantees=["b < 5"]
    ),
    Contract(
        variables={"c": "-50..50", "d": "-50..50"},
        assumptions=["c > 22"],
        guarantees=["d < 44"]
    ),
]


two_integer_contracts_with_assumptions_simplifiable = [
    Contract(
        variables={"a": "-50..50", "b": "-50..50"},
        assumptions=["a > 10"],
        guarantees=["b < 5"]
    ),
    Contract(
        variables={"c": "-50..50", "d": "-50..50"},
        assumptions=["c > 22"],
        guarantees=["d < 44"]
    ),
]
