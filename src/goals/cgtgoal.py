from typing import List, Tuple, Dict

from contracts.contract import Contract


# from src.goals.operations import compostion, conjunction


class CGTGoal:
    """
    Contract-based Goal Tree

    Attributes:
        contracts: a list of contract objects
        alphabet: a list of tuples containing the shared alphabet among all contracts
    """

    def __init__(self,
                 name: str = None,
                 context: Tuple[Dict[str, str], List[str]] = None,
                 description: str = None,
                 contracts: List[Contract] = None,
                 sub_goals: List['CGTGoal'] = None,
                 sub_operation: str = None,
                 parent_goal: 'CGTGoal' = None,
                 parent_operation: str = None):

        if name is None:
            self.name = ""
        elif isinstance(name, str):
            self.name = name
        else:
            raise AttributeError

        if description is None:
            self.description = ""
        elif isinstance(description, str):
            self.description = description
        else:
            raise AttributeError

        if contracts is None:
            self.contracts = []
        elif isinstance(contracts, list):
            self.contracts = contracts
        else:
            raise AttributeError

        if sub_goals is None:
            self.sub_goals = []
        elif isinstance(sub_goals, list) and \
                all(isinstance(x, CGTGoal) for x in sub_goals):
            self.sub_goals = sub_goals
        else:
            raise AttributeError

        if sub_operation is None:
            self.sub_operation = ""
        elif isinstance(sub_operation, str):
            self.sub_operation = sub_operation
        else:
            raise AttributeError

        if parent_goal is None:
            self.parent_goal = None
        elif isinstance(parent_goal, CGTGoal):
            self.parent_goal = parent_goal
        else:
            raise AttributeError

        if parent_operation is None:
            self.parent_operation = ""
        elif isinstance(parent_operation, str):
            self.description = description
        else:
            raise AttributeError

        if context is None:
            self.context = ({}, ["TRUE"])
        elif isinstance(context, tuple):
            self.context = context
            self.propagate_context(context)
        else:
            raise AttributeError

    def update(self,
               name: str = None,
               description: str = None,
               contracts: List[Contract] = None,
               sub_goals: List['CGTGoal'] = None,
               sub_operation: str = None
               ):

        if name is None:
            self.name = ""
        elif isinstance(name, str):
            self.name = name
        else:
            raise AttributeError

        if description is None:
            self.description = ""
        elif isinstance(description, str):
            self.description = description
        else:
            raise AttributeError

        if contracts is None:
            self.contracts = []
        elif isinstance(contracts, list):
            self.contracts = contracts
        else:
            raise AttributeError

        if sub_goals is None:
            self.sub_goals = []
        elif isinstance(sub_goals, list) and \
                all(isinstance(x, CGTGoal) for x in sub_goals):
            self.sub_goals = sub_goals
        else:
            raise AttributeError

        if sub_operation is None:
            self.sub_operation = ""
        elif isinstance(sub_operation, str):
            self.sub_operation = sub_operation
        else:
            raise AttributeError


    def propagate_context(self, context: Tuple[Dict[str, str], str]):
        """Set the context as assumptions of all the contracts in the node"""
        variables, context_assumptions = context
        for contract in self.contracts:
            contract.add_variables(variables)
            contract.add_assumptions(context_assumptions)

    def get_context(self):
        return self.context

    def set_parent(self, parent_goal: 'CGTGoal', parent_operation: str):
        if not isinstance(parent_goal, CGTGoal):
            raise AttributeError

        if not isinstance(parent_operation, str):
            raise AttributeError

        self.parent_goal = parent_goal
        self.parent_operation = parent_operation

    def set_subgoals(self, sub_goals: list, sub_operation: str):
        if not isinstance(sub_goals, list):
            raise AttributeError

        if not isinstance(sub_operation, str):
            raise AttributeError

        self.sub_goals = sub_goals
        self.sub_operation = sub_operation

    def set_name(self, name):
        if not isinstance(name, str):
            raise AttributeError
        self.name = name

    def get_name(self):
        return self.name

    def set_description(self, description):
        if not isinstance(description, str):
            raise AttributeError
        self.description = description

    def get_description(self):
        return self.description

    def get_contracts(self):
        return self.contracts

    def get_sub_operation(self):
        return self.sub_operation

    def get_sub_goals(self):
        return self.sub_goals

    def get_parent(self):
        return self.parent_goal

    def __str__(self, level=0):
        """Override the print behavior"""
        ret = "\t" * level + repr(self.name) + "\n"
        # ret += "\t" * level + repr(self.description) + "\n"
        for n, contract in enumerate(self.contracts):
            if n > 0:
                ret += "\t" * level + "\t/\\ \n"
            ret += "\t" * level + "A:\t\t" + \
                   ' & '.join(str(x) for x in contract.get_list_assumptions()).replace('\n', ' ') + "\n"
            ret += "\t" * level + "G:\t\t" + \
                   ' & '.join(str(x) for x in contract.get_list_guarantees()).replace('\n', ' ') + "\n"
        ret += "\n"
        if self.sub_goals is not None and len(self.sub_goals) > 0:
            ret += "\t" * level + "\t" + self.sub_operation + "\n"
            level += 1
            for child in self.sub_goals:
                try:
                    ret += child.__str__(level + 1)
                except Exception:
                    print("WAIT")
        return ret

    def __eq__(self, other):
        """Override the default Equals behavior"""
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        """Define a non-equality test"""
        return not self.__eq__(other)
