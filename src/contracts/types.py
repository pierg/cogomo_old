from typing import List


class Type(object):

    def __init__(self, name: str, var_type: str):
        self.name = name
        self.nuxmvtype = var_type

    def __str__(self):
        return self.name + ": " + self.nuxmvtype

    def nuxmv_variable(self):
        return self.name + ": " + self.nuxmvtype + ";\n"

    def __eq__(self, other):
        return self.name == other.name and self.nuxmvtype == other.nuxmvtype

    def __hash__(self):
        return hash(self.name + self.nuxmvtype)


class Boolean(Type):

    def __init__(self, name: str):
        super().__init__(name, "boolean")


class Integer(Type):

    def __init__(self, name: str, min: int, max: int):
        super().__init__(name, str(min) + ".." + str(max))


class BoundedInt(Integer):

    def __init__(self, name: str):
        super().__init__(name, min=-100, max=100)


class BoundedNat(Integer):

    def __init__(self, name: str):
        super().__init__(name, min=0, max=100)


class GeneralPort(Type):

    def __init__(self, port_type: str, name: str, var_type: str):
        self.port_type = port_type
        super().__init__(name, var_type)

    def nuxmv_variable_type(self):
        return self.port_type + ": " + self.nuxmvtype + ";\n"


class IntegerPort(GeneralPort):

    def __init__(self, port_type: str, name: str, min: int, max: int):
        super().__init__(port_type, name, str(min) + ".." + str(max))


class BoundedIntPort(IntegerPort):

    def __init__(self, port_type: str, name: str):
        super().__init__(port_type, name, min=-100, max=100)


class BoundedNatPort(IntegerPort):

    def __init__(self, port_type: str, name: str):
        super().__init__(port_type, name, min=0, max=100)


def have_shared_variables(list_a: List[Type], list_b: List[Type]):
    """Returns true if the two list have at least a type with the same name in common"""

    for elem_a in list_a:
        for elem_b in list_b:
            if elem_a == elem_b:
                return True
    return False
