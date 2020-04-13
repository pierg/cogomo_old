from copy import deepcopy
from typing import List, Union
from helper.tools import extract_terms

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


class Variables(object):

    def __init__(self, variables: Union[List['Type'], Type]):
        if isinstance(variables, Type):
            variables = [variables]
        self.__variables = variables

    @property
    def list(self):
        return self.__variables

    @list.setter
    def list(self, value):
        self.__variables = value

    def __add__(self, other):
        res = deepcopy(self)
        res.extend(other)
        return res

    def get_list_str(self):
        """Get List[str] for nuxmv"""
        tuple_vars = []
        for v in self.list:
            tuple_vars.append(v.port_type + ": " + v.basic_type)
        return tuple_vars

    def extend(self, other: 'Variables'):
        for v in other.list:
            self.add(v)

    def add(self, var: Union['Type', List['Type']]):
        if isinstance(var, Type):
            var = [var]

        for v in var:
            for ex_v in self.list:
                if v.name == ex_v.name:
                    type_a = type(v).__name__
                    type_b = type(ex_v).__name__
                    if type_a != type_b:
                        Exception("Variable " + str(v) + " is already present but "
                                                         "is of tyoe " + type_a + " instead of " + type_b)
                    else:
                        return

            self.list.append(v)

    def remove(self, var: Union['Type', List['Type']]):

        if isinstance(var, Type):
            var = [var]

        for v in var:
            if v in self.list:
                self.list.remove(v)
            else:
                Exception("Variable " + v.name + " not found, it cannot be removed")



def extract_variable(formula: str) -> 'Variables':

    var_names = extract_terms(formula)

    context_vars: List[Type] = []

    try:
        int(var_names[1])
        context_vars.append(BoundedInt(var_names[0]))
    except:
        for var_name in var_names:
            context_vars.append(Boolean(var_name))

    return Variables(context_vars)