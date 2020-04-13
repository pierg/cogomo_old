from checks.tools import And
from src.contracts.contract import BooleanContract
from src.contracts.operations import *

"""Parse Goals from Structured Text File"""

two_boolean_contracts = [
    BooleanContract(["a"], ["b"]),
    BooleanContract(["c"], ["d"])
]

two_boolean_contracts_with_simplification = [
    BooleanContract(["a"], ["b"]),
    BooleanContract(["b"], ["c"])
]

three_boolean_contracts = [
    BooleanContract(["a"], ["b"]),
    BooleanContract(["c"], ["d"]),
    BooleanContract(["e"], ["f"])
]

three_boolean_contracts_with_simplification = [
    BooleanContract(["a"], ["b"]),
    BooleanContract(["c"], ["d"]),
    BooleanContract(["b"], ["f"])
]

def test_constructors():
    c1 = BooleanContract(["a"], ["b"])
    c2 = BooleanContract(["c"], ["d"])


def test_two_contracts_composition():

    ca = two_boolean_contracts[0]
    cb = two_boolean_contracts[1]

    print(ca)
    print(cb)

    contract_composed = compose_contracts(two_boolean_contracts)

    assert str(contract_composed.assumptions) == "(a & c)"


def test_three_contracts_composition():

    contract_composed = compose_contracts(three_boolean_contracts)

    assert str(contract_composed.assumptions) == "((a & c) & e)"



def test_two_contracts_composition_assumption_simplification():

    contract_composed = compose_contracts(two_boolean_contracts_with_simplification)

    assert str(contract_composed.assumptions) == "a"


def test_three_contracts_composition_assumption_simplification():

    contract_composed = compose_contracts(three_boolean_contracts_with_simplification)

    assert str(contract_composed.assumptions) == "(a & c)"







