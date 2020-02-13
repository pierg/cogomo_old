from copy import deepcopy
from typing import List, Tuple, Dict

from contracts.contract import Contract, Type
from contracts.formulas import Assumption
from goals.context import Context

from helper.logic import And, Or
from helper.tools import extract_variables_from_LTL


class CGTGoal:
    """Contract-based Goal Tree"""

    def __init__(self,
                 name: str = None,
                 description: str = None,
                 contracts: List[Contract] = None,
                 refined_by: List['CGTGoal'] = None,
                 refined_with: str = None,
                 context: Context = None):

        self.__connected_to = None

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
            self.__refined_by = None
            self.__refined_with = None
        elif refined_by is not None and refined_with is not None:
            self.__refined_by: List['CGTGoal'] = refined_by
            self.__refined_with: str = refined_with
            for goal in refined_by:
                goal.connected_to = self
        else:
            raise AttributeError

        if context is not None:
            self.add_context(context)


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
    def refined_by(self, goals: List['CGTGoal']):
        self.__refined_by = goals
        if goals is not None:
            for goal in goals:
                goal.connected_to = self

    @property
    def refined_with(self):
        return self.__refined_with

    @refined_with.setter
    def refined_with(self, value):
        self.__refined_with = value

    @property
    def context(self):
        contexts = []
        variables = []
        for contract in self.contracts:
            context = []
            variables.extend(contract.variables)
            for a in contract.assumptions:
                if a.kind == "context":
                    context.append(a)
            if len(context) > 0:
                context = And(context)
                contexts.append(context)
        if len(contexts) > 0:
            contexts = Or(contexts)
            variables = extract_variables_from_LTL(variables, contexts)
            return Context(variables=variables, expression=contexts)
        else:
            return None

    @context.setter
    def context(self, value):
        self.add_context(value)

    @property
    def connected_to(self):
        return self.__connected_to

    @connected_to.setter
    def connected_to(self, value):
        self.__connected_to = value

    def get_refinement_by(self):
        return self.refined_by, self.refined_with

    def get_goal(self, name: str):
        """Search the CGT and get the first goal with name == str"""
        if self.name == name:
            return self
        elif self.refined_by is not None:
            res = None
            for child in self.refined_by:
                res = child.get_goal(name)
            return res
        else:
            return None

    def get_all_goal(self, name):
        """Return all goals are name or a copy of"""
        curr_name = self.name.replace('_copy', '')
        if curr_name == name:
            return [self]
        elif self.refined_by is not None:
            res = []
            for child in self.refined_by:
                res.extend(child.get_all_goal(name))
            return res
        else:
            return []

    def refine_by(self, refined_by: List['CGTGoal'], consolidate=True):
        """Refine by 'refined_by' with 'refined_with'"""
        """If type 'REFINEMENT', propagating the assumptions from the refined goal"""
        if len(refined_by) != 1:
            raise Exception("At the moment the refinement of one goal must be performed by another single goal")
        for i, contract in enumerate(self.contracts):
            contract.propagate_assumptions_from(
                refined_by[0].contracts[i]
            )
            contract.is_refined_by(
                refined_by[0].contracts[i]
            )
        self.__refined_by = refined_by
        self.__refined_with = "REFINEMENT"
        if consolidate:
            self.consolidate_bottom_up()

    def provided_by(self, goal):
        """Indicates that the assumptions of 'self' are provided by the guarantees of 'goal'.
        Connects the two goal by a 'PROVIDED BY' link"""
        self.__refined_by = [goal]
        self.__refined_with = "PROVIDED_BY"
        goal.connected_to = self

    def add_context(self, context: Context):
        """Set the context as assumptions of all the contracts in the node"""
        if context is not None:
            variables, context_assumptions = context.get_context()
            context_assumptions = Assumption(str(context_assumptions), kind="context")
            for contract in self.contracts:
                contract.add_variables(variables)
                contract.add_assumption(context_assumptions)

            if self.refined_by is None:
                self.consolidate_bottom_up()
            else:
                for goal in self.refined_by:
                    goal.add_context(context)

    def add_domain_properties(self):
        """Adding Domain Properties to 'cgt' (i.e. descriptive statements about the problem world (such as physical laws)
        These properties are intrinsic to the Contract/Pattern and get added as assumptions"""
        for contract in self.contracts:
            try:
                contract.add_domain_properties()
            except AttributeError:
                pass
        if self.refined_by is None:
            self.consolidate_bottom_up()
        else:
            for goal in self.refined_by:
                goal.add_domain_properties()

    def add_expectations(self, expectations: List[Contract]):
        """Domain Hypothesis or Expectations (i.e. prescriptive assumptions on the environment)
        Expectations are conditional assumptions, they get added to each contract of the CGT
        only if the Contract guarantees concern the 'expectations' guarantees and are consistent with them"""
        from src.checks.nsmvhelper import are_satisfied_in
        from src.contracts.types import have_shared_variables
        for contract in self.contracts:
            for expectation in expectations:
                if have_shared_variables(contract.variables, expectation.variables):
                    if are_satisfied_in([contract.variables, expectation.variables],
                                        [contract.guarantees, expectation.guarantees]):
                        contract.add_variables(expectation.variables)
                        contract.add_assumptions(expectation.assumptions)

        if self.refined_by is None:
            self.consolidate_bottom_up()
        else:
            for goal in self.refined_by:
                goal.add_expectations(expectations)

    def update_with(self, goal: 'CGTGoal', consolidate=True):
        """Update the current node of the CGT with 'goal' keeping the connection to the current parent goal
        and consolidating the tree up to the root node"""

        if self.connected_to is not None:
            parent = self.connected_to
            for n, child in enumerate(parent.refined_by):
                if child == self:
                    parent.refined_by[n] = goal

            if consolidate:
                self.consolidate_bottom_up()
        else:
            """Update Parameters"""
            self.name = goal.name
            self.description = goal.description
            self.contracts = goal.contracts
            self.refined_by = goal.refined_by
            self.refined_with = goal.refined_with

    def consolidate_bottom_up(self):
        """It recursivly re-perfom composition and conjunction and refinement operations up to the rood node"""
        from src.goals.operations import conjunction, composition
        if self.connected_to is not None:
            node = self.connected_to
            refined_by, refined_with = node.get_refinement_by()
            if refined_with == "CONJUNCTION":
                conjunction(refined_by, connect_to=node)
            elif refined_with == "COMPOSITION":
                composition(refined_by, connect_to=node)
            elif refined_with == "REFINEMENT":
                node.refine_by(refined_by, consolidate=False)
            else:
                raise Exception(refined_with + " consolidation not supported")

            node.consolidate_bottom_up()
        else:
            return

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
        ret = "\t" * level + "NAME:\t" + repr(self.name) + "\n"
        for n, contract in enumerate(self.contracts):
            if n > 0:
                ret += "\t" * level + "\t/\\ \n"
            # ret += "\t" * level + " CTX:\t" + \
            #        ' & '.join(str(x) for x in contract.assumptions
            #                   if x.kind == "context").replace('\n', ' ') + "\n"
            # ret += "\t" * level + " EXP:\t" + \
            #        ' & '.join(str(x) for x in contract.assumptions
            #                   if x.kind == "expectation").replace('\n', ' ') + "\n"
            # ret += "\t" * level + " DOM:\t" + \
            #        ' & '.join(str(x) for x in contract.assumptions
            #                   if x.kind == "domain").replace('\n', ' ') + "\n"
            ret += "\t" * level + "  A:\t\t" + \
                   ' & '.join(str(x) for x in contract.assumptions).replace('\n', ' ') + "\n"
            ret += "\t" * level + "  G:\t\t" + \
                   ' & '.join(str(x) for x in contract.guarantees).replace('\n', ' ') + "\n"
        ret += "\n"
        if self.refined_by is not None:
            print(len(self.refined_by))
            ret += "\t" * level + "\t" + self.refined_with + "\n"
            level += 1
            for child in self.refined_by:
                try:
                    ret += child.__str__(level + 1)
                except Exception:
                    print("WAIT")
        return ret
