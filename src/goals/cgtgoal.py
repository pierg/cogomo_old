from typing import List, Tuple, Dict

from contracts.contract import Contract

# from src.goals.operations import compostion, conjunction
from helper.logic import And, Or
from patterns.patterns import *

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
                 refined_with: str = None):

        if name is None:
            self.name = ""
        else:
            self.set_name(name)

        if description is None:
            self.description = ""
        else:
            self.set_description(description)

        if contracts is None:
            self.contracts: List[Contract] = []
        elif isinstance(contracts, list):
            self.contracts: List[Contract] = contracts
        else:
            raise AttributeError

        if refined_by is None and refined_with is None:
            self.refined_by = None
            self.refined_with = None
        else:
            self.refine_by(refined_by, refined_with)

        if context is None:
            self.context = ({}, ["TRUE"])
        elif isinstance(context, tuple):
            self.context = context
            self._propagate_context(context)
        else:
            raise AttributeError

        self.connected_to = None
        self.conected_with = ""

    def add_domain_properties(self):
        """Add domain properties to each Pattern in each Goal of the CGT"""
        for contract in self.contracts:
            try:
                contract.add_physical_assumptions()
            except AttributeError:
                pass
        if self.refined_by is None:
            return
        else:
            for goal in self.refined_by:
                goal.add_domain_properties()

    def add_expectations(self, expectations: List[Contract]):
        """Add expectetions when needed to each Contract in each Goal of the CGT"""
        for contract in self.contracts:
            contract.add_expectations(expectations)
        if self.refined_by is None:
            return
        else:
            for goal in self.refined_by:
                goal.add_expectations(expectations)

    def get_refinement(self):
        return (self.refined_by, self.refined_with)

    def get_parent(self):
        return self.connected_to

    def update_contracts(self, contracts: List[Contract]):
        self.contracts = contracts

    def refine_by(self, sub_goals: List['CGTGoal'], sub_operation: str):
        """Refine by 'sub_goals' with 'sub_operation' by first propagating the assumptions to all the CGT"""
        if not (isinstance(sub_goals, list) and isinstance(sub_operation, str)):
            raise AttributeError

        if sub_operation == "REFINEMENT":
            if len(sub_goals) != 1:
                raise Exception("Refinement of one goal must be performed by another single goal")
            for i, contract in enumerate(self.get_list_contracts()):
                contract.propagate_assumptions_from(
                    sub_goals[0].get_list_contracts()[i]
                )
                contract.is_refined_by(
                    sub_goals[0].get_list_contracts()[i]
                )
        elif sub_operation == "COMPOSITION" or \
                sub_operation == "CONJUNCTION" or \
                sub_operation == "REFINEMENT" or \
                sub_operation == "MAPPING":
            self.refined_by = sub_goals
            self.refined_with = sub_operation
            for goal in sub_goals:
                goal._set_connection_to(self)
        else:
            raise AttributeError

    def _set_connection_to(self, parent_goal: 'CGTGoal'):
        """Connect to 'parent_goal' with the 'parent_operation'"""
        if not isinstance(parent_goal, CGTGoal):
            raise AttributeError
        self.connected_to = parent_goal

    def _propagate_context(self, context: Tuple[Dict[str, str], List[str]]):
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

    def get_list_contracts(self) -> List[Contract]:
        return self.contracts

    def get_ltl_assumptions(self):
        a_list = []
        for c in self.contracts:
            a_list.append(And(c.assumptions))
        return Or(a_list)

    def get_ltl_guarantees(self):
        g_list = []
        for c in self.contracts:
            g_list.append(And(c.guarantees))
        return And(g_list)

    def __str__(self, level=0):
        """Override the print behavior"""
        ret = "\t" * level + repr(self.name) + "\n"
        # ret += "\t" * level + repr(self.description) + "\n"
        for n, contract in enumerate(self.contracts):
            if n > 0:
                ret += "\t" * level + "\t/\\ \n"
            ret += "\t" * level + "A:\t\t" + \
                   ' & '.join(str(x) for x in contract.assumptions).replace('\n', ' ') + "\n"
            ret += "\t" * level + "G:\t\t" + \
                   ' & '.join(str(x) for x in contract.guarantees).replace('\n', ' ') + "\n"
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
