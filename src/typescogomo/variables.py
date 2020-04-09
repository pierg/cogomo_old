from typing import List


class Type(object):
    """Base Type Class, a Type is a variable with a name, basic_type for nuxmv (e.g. boolean),
    and variable_type: used for example when a component requires multiple variables of the same type
    but having different names. If the port_type is not specified then it's the same as the name of the variable"""

    def __init__(self, name: str, basic_type: str, port_type: str = None):

        """Name of the variable"""
        self.name = name

        """Basic type, for nuxmv """
        self.basic_type = basic_type

        """Type of the variable, if it is not specified then it's the same as the name"""
        self.port_type = port_type if port_type is not None else name

    def __str__(self):
        return self.name

    def nuxmv_variable(self):
        return self.name + ": " + self.basic_type + ";\n"

    def __eq__(self, other):
        return self.name == other.name and self.basic_type == other.basic_type and self.port_type == other.port_type

    def __hash__(self):
        return hash(self.name + self.basic_type)


class Boolean(Type):

    def __init__(self, name: str, port_type: str = None):
        super().__init__(name, "boolean", port_type=port_type)


class Integer(Type):

    def __init__(self, name: str, min: int, max: int, port_type: str = None):
        super().__init__(name, str(min) + ".." + str(max), port_type=port_type)


class BoundedInt(Integer):

    def __init__(self, name: str, port_type: str = None):
        super().__init__(name, min=-100, max=100, port_type=port_type)


class BoundedNat(Integer):

    def __init__(self, name: str, port_type: str = None):
        super().__init__(name, min=0, max=100, port_type=port_type)


def have_shared_variables(list_a: List[Type], list_b: List[Type]):
    """Returns true if the two list have at least a type with the same name in common"""

    for elem_a in list_a:
        for elem_b in list_b:
            if elem_a == elem_b:
                return True
    return False
