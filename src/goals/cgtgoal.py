from typing import List, Tuple, Dict

from contracts.contract import Contract

# from src.goals.operations import compostion, conjunction
from helper.logic import And, Or
from patterns.patterns import *


class CGTGoal:
    """Contract-based Goal Tree"""

    def __init__(self,
                 name: str = None,
                 description: str = None,
                 contracts: List[Contract] = None,
                 refined_by: List['CGTGoal'] = None,
                 refined_with: str = None,
                 context: Tuple[Dict[str, str], List[str]] = None):

        if name is None:
            self.__name: str = ""
        else:
            self.__name: str = name

        if description is None:
            self.__description: str = ""
        else:
            self.__description: str = description

        if contracts is None:
            self.__contracts: List[Contract] = []
        else:
            self.__contracts: List[Contract] = contracts

        if refined_by is None and refined_with is None:
            self.__refined_by: List['CGTGoal'] = []
            self.__refined_with = None
        elif refined_by is not None and refined_with is not None:
            self.__refined_by: List['CGTGoal'] = refined_by
            self.__refined_with: str = refined_with
        else:
            raise AttributeError

        if context is None:
            self.__context: Tuple[Dict[str, str], List[str]] = ({}, ["TRUE"])
        elif isinstance(context, tuple):
            self.__context: Tuple[Dict[str, str], List[str]] = context
            self._propagate_context(context)
        else:
            raise AttributeError

        self.__connected_to = None
        self.__connected_with = ""

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def description(self):
        return self.__description

    @description.setter
    def description(self, value):
        self.__description = value

    @property
    def contracts(self):
        return self.__contracts

    @contracts.setter
    def contracts(self, value):
        self.__contracts = value

    @property
    def refined_by(self):
        return self.__refined_by

    @refined_by.setter
    def refined_by(self, value):
        self.__refined_by = value

    @property
    def refined_with(self):
        return self.__refined_with

    @refined_with.setter
    def refined_with(self, value):
        self.__refined_with = value

    @property
    def context(self):
        return self.__context

    @context.setter
    def context(self, value):
        self.__context = value
        self._propagate_context(value)

    @property
    def connected_to(self):
        return self.__connected_to

    @connected_to.setter
    def connected_to(self, value):
        self.__connected_to = value

    def add_domain_properties(self):
        """Add domain properties to each Pattern in each Goal of the CGT"""
        for contract in self.__contracts:
            try:
                contract.add_physical_assumptions()
            except AttributeError:
                pass
        if self.__refined_by is None:
            return
        else:
            for goal in self.__refined_by:
                goal.add_domain_properties()

    def add_expectations(self, expectations: List[Contract]):
        """Add expectetions when needed to each Contract in each Goal of the CGT"""
        for contract in self.__contracts:
            contract.add_expectations(expectations)
        if self.__refined_by is None:
            return
        else:
            for goal in self.__refined_by:
                goal.add_expectations(expectations)

    def get_refinement_by(self):
        return self.refined_by, self.refined_with

    def refine_by(self, refined_by: List['CGTGoal'], refined_with: str):
        """Refine by 'refined_by' with 'refined_with'"""

        if refined_with == "REFINEMENT":
            """If type 'REFINEMENT', propagating the assumptions to all the CGT"""
            if len(refined_by) != 1:
                raise Exception("At the moment the refinement of one goal must be performed by another single goal")
            for i, contract in enumerate(self.contracts):
                contract.propagate_assumptions_from(
                    refined_by[0].contracts[i]
                )
                contract.is_refined_by(
                    refined_by[0].contracts[i]
                )
        elif refined_with == "COMPOSITION" or \
                refined_with == "CONJUNCTION" or \
                refined_with == "REFINEMENT" or \
                refined_with == "MAPPING":
            self.__refined_by = refined_by
            self.__refined_with = refined_with
            for goal in refined_by:
                goal.connected_to = self
        else:
            raise AttributeError

    def _propagate_context(self, context: Tuple[Dict[str, str], List[str]]):
        """Set the context as assumptions of all the contracts in the node"""
        variables, context_assumptions = context
        for contract in self.contracts:
            contract.add_variables(variables)
            contract.add_assumptions(context_assumptions)

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
