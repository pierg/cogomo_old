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
                 refined_by: List['CGTGoal'] = None,
                 refined_with: str = None,
                 connected_to: 'CGTGoal' = None,
                 connected_with: str = None):

        if name is None:
            self.name = ""
        else:
            self.set_name(name)

        if description is None:
            self.description = ""
        else:
            self.set_description(description)

        if contracts is None:
            self.contracts = []
        elif isinstance(contracts, list):
            self.contracts = contracts
        else:
            raise AttributeError

        if refined_by is None and refined_with is None:
            self.refined_by = []
            self.refined_with = ""
        else:
            self.refine_by(refined_by, refined_with)

        if connected_to is None and connected_with is None:
            self.connected_to = None
            self.conected_with = ""
        else:
            self.connect_to(connected_to, connected_with)

        if context is None:
            self.context = ({}, ["TRUE"])
        elif isinstance(context, tuple):
            self.context = context
            self.propagate_context(context)
        else:
            raise AttributeError

    # def update(self,
    #            name: str = None,
    #            description: str = None,
    #            contracts: List[Contract] = None,
    #            sub_goals: List['CGTGoal'] = None,
    #            sub_operation: str = None
    #            ):
    #
    #     if name is None:
    #         self.name = ""
    #     elif isinstance(name, str):
    #         self.name = name
    #     else:
    #         raise AttributeError
    #
    #     if description is None:
    #         self.description = ""
    #     elif isinstance(description, str):
    #         self.description = description
    #     else:
    #         raise AttributeError
    #
    #     if contracts is None:
    #         self.contracts = []
    #     elif isinstance(contracts, list):
    #         self.contracts = contracts
    #     else:
    #         raise AttributeError
    #
    #     if sub_goals is None:
    #         self.refined_by = []
    #     elif isinstance(sub_goals, list) and \
    #             all(isinstance(x, CGTGoal) for x in sub_goals):
    #         self.refined_by = sub_goals
    #     else:
    #         raise AttributeError
    #
    #     if sub_operation is None:
    #         self.refined_with = ""
    #     elif isinstance(sub_operation, str):
    #         self.refined_with = sub_operation
    #     else:
    #         raise AttributeError


    def connect_to(self, parent_goal: 'CGTGoal', parent_operation: str):
        """Connect to 'parent_goal' with the 'parent_operation'"""
        if not (isinstance(parent_goal, CGTGoal) and isinstance(parent_operation, str)):
            raise AttributeError

        self.connected_to = parent_goal
        self.conected_with = parent_operation

    def refine_by(self, sub_goals: list, sub_operation: str):
        """Refine by 'sub_goals' with 'sub_operation'"""
        if not (isinstance(sub_goals, list) and isinstance(sub_operation, str)):
            raise AttributeError

        self.refined_by = sub_goals
        self.refined_with = sub_operation



    def propagate_context(self, context: Tuple[Dict[str, str], str]):
        """Set the context as assumptions of all the contracts in the node"""
        variables, context_assumptions = context
        for contract in self.contracts:
            contract.add_variables(variables)
            contract.add_assumptions(context_assumptions)

    def get_context(self):
        return self.context


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
        return self.refined_with

    def get_sub_goals(self):
        return self.refined_by

    def get_parent(self):
        return self.connected_to

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
        if self.refined_by is not None and len(self.refined_by) > 0:
            ret += "\t" * level + "\t" + self.refined_with + "\n"
            level += 1
            for child in self.refined_by:
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
