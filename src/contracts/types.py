
class Type(object):

    def __init__(self, name: str, var_type: str):
        self.name = name
        self.nuxmvtype = var_type

    def __str__(self):
        return self.name + ": " + self.nuxmvtype + ";"


class Boolean(Type):

    def __init__(self, name: str):
        super().__init__(name, "boolean")


class Integer(Type):

    def __init__(self, name: str, min: int, max: int):
        super().__init__(name, str(min) + ".." + str(max))


class BoundedInt(Integer):

    def __init__(self, name: str):
        super().__init__(name, str(-100) + ".." + str(100))


class BoundedNat(Integer):

    def __init__(self, name: str):
        super().__init__(name, str(0) + ".." + str(100))
