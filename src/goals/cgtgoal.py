from copy import deepcopy
from typing import List

from contracts.contract import Contract, Type
from typescogomo.formulae import Assumption, Guarantee
from typescogomo.formulae import Context

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
            self.set_context(context)

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
    def context(self, value: Context):
        self.set_context(value)

    @property
    def connected_to(self):
        return self.__connected_to

    @connected_to.setter
    def connected_to(self, value):
        self.__connected_to = value

    def get_refinement_by(self):
        return self.refined_by, self.refined_with

    def get_all_goals(self, name, copies=False):
        """Depth-first search. Returns all goals are name"""
        result = []
        if self.refined_by is not None:
            for child in self.refined_by:
                if copies:
                    child_name = child.name.replace('_copy', '')
                else:
                    child_name = child.name
                if child_name == name:
                    result.append(child)
                else:
                    result.extend(child.get_all_goals(name, copies))
        return result

    def get_goal(self, name) -> 'CGTGoal':
        """Return the goal of name 'name'"""
        res = self.get_all_goals(name)
        if len(res) == 0:
            raise Exception("No Goal with that name")
        elif len(res) == 1:
            return res[0]
        else:
            raise Exception("Multiple goals with the same name")

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

    def set_context(self, context: Context):
        """Set the context as assumptions of all the contracts in the node"""
        variables, context_assumptions = context.get_vars_and_formula()
        context_assumptions = Assumption(str(context_assumptions), kind="context")
        for contract in self.contracts:
            contract.remove_contextual_assumptions()
            contract.add_variables(variables)
            contract.add_assumptions(context_assumptions)
        self.consolidate_bottom_up()

    def add_context(self, context: Context):
        """Add the context as assumptions of all the contracts in the node"""
        if context is not None:
            variables, context_assumptions = context.get_vars_and_formula()
            context_assumptions = Assumption(str(context_assumptions), kind="context")
            for contract in self.contracts:
                contract.add_variables(variables)
                contract.add_assumptions(context_assumptions)

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
        from typescogomo.variables import have_shared_variables
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

    def substitute_with(self, goal_name: str, goal_name_update: str):

        goals_to_substitute = self.get_all_goals(goal_name)
        goals_substitute = self.get_all_goals(goal_name_update)

        substituted = False

        for goal_to_substitute in goals_to_substitute:
            for goal_substitute in goals_substitute:
                if goal_to_substitute.refined_by == [goal_substitute] and \
                        goal_to_substitute.refined_with == "REFINEMENT":
                    goal_to_substitute.update_with(goal_substitute)
                    substituted = True

        if substituted:
            print("Substitution successful: " + goal_name + "with" + goal_name_update)
        else:
            print("No substitution has been performed")

    def abstract_guarantees_of(self, goal_name: str, guarantees: List[Guarantee], variables: List[Type], abstract_name: str = None):

        goals = self.get_all_goals(goal_name)
        if abstract_name is None:
            abstract_name = goal_name + "_abstracted"

        for goal in goals:
            if len(goal.contracts) > 1:
                raise Exception("At the moment you can only abstract goals that have only one conjunction")

            """Create a new abstract goal with 'guarantees' """
            refined_goal = CGTGoal()
            refined_goal.name = goal.name
            refined_goal.description = goal.description
            refined_goal.contracts = deepcopy(goal.contracts)
            refined_goal.refined_by = goal.refined_by
            refined_goal.refined_with = goal.refined_with

            """Goal become the abstract goal which is then refined with it self"""
            goal.name = abstract_name
            goal.contracts[0].add_variables(variables)
            goal.contracts[0].guarantees = guarantees

            goal.refine_by([refined_goal])

        print("Abstraction of " + goal_name + " completed")

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
            a_context = [str(x) for x in contract.assumptions if x.kind == "context"]
            a_domain = [str(x) for x in contract.assumptions if x.kind == "domain"]
            a_expectation = [str(x) for x in contract.assumptions if x.kind == "expectation"]
            a_assumed = [str(x) for x in contract.assumptions if x.kind == "assumed"]
            if len(a_assumed) == 0:
                a_assumed = ["TRUE"]

            if len(a_context) > 0:
                ret += "\t" * level + " CTX:\t" + \
                       ' & '.join(x for x in a_context).replace('\n', ' ') + "\n"

            if len(a_domain) > 0:
                ret += "\t" * level + " DOM:\t" + \
                       ' & '.join(x for x in a_domain).replace('\n', ' ') + "\n"

            if len(a_expectation) > 0:
                ret += "\t" * level + " EXP:\t" + \
                       ' & '.join(x for x in a_expectation).replace('\n', ' ') + "\n"

            ret += "\t" * level + "  A:\t" + \
                   ' & '.join(str(x) for x in a_assumed).replace('\n', ' ') + "\n"
            ret += "\t" * level + "  G:\t" + \
                   ' & '.join(str(x) for x in contract.guarantees).replace('\n', ' ') + "\n"
        ret += "\n"
        if self.refined_by is not None:
            ret += "\t" * level + "\t" + self.refined_with + "\n"
            level += 1
            for child in self.refined_by:
                try:
                    ret += child.__str__(level + 1)
                except Exception:
                    print("ERROR IN PRINT")
        return ret
