from src.helper.parser import *
from src.goals.operations import *

"""Parse Goals from Structured Text File"""


c_1 = Contract(variables={"a": "boolean", "b": "boolean"},
               assumptions=["a"],
               guarantees=["b"])

c_2 = Contract(variables={"c": "boolean", "d": "boolean"},
               assumptions=["c"],
               guarantees=["d"])


c_3 = Contract(variables={"d": "boolean", "e": "boolean"},
               assumptions=["d"],
               guarantees=["e"])


c = compose_contracts([c_1, c_2, c_3])

print(c)


