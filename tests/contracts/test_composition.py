from src.helper.parser import *
from src.contracts.operations import *

"""Parse Goals from Structured Text File"""

two_boolean_contracts = [
    BooleanContract(["a"], ["b"]),
    BooleanContract(["c"], ["d"])
]

three_boolean_contracts = [
    BooleanContract(["a"], ["b"]),
    BooleanContract(["c"], ["d"]),
    BooleanContract(["e"], ["f"])
]

def test_constructors():
    c1 = BooleanContract(["a"], ["b"])
    c2 = BooleanContract(["c"], ["d"])




def test_two_contracts_composition():

    contract_composed = compose_contracts(two_boolean_contracts)

    assert contract_composed.get_ltl_assumptions() == "a & c"


def test_three_contracts_composition():

    contract_composed = compose_contracts(three_boolean_contracts)

    assert contract_composed.get_ltl_assumptions() == "a & c & e"



