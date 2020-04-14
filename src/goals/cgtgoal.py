from typing import List

from contracts.contract import Contract
from src.typescogomo.contexts import Context
from typescogomo.assumptions import Expectation
from typescogomo.guarantees import Guarantees, deepcopy
from src.checks.tools import Or, And


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
        """Return a list of contexts, each is in OR with each other"""
        contexts = []
        for contract in self.contracts:
            cs = contract.assumptions.get_kind("context")
            if cs is not None:
                f = []
                v = []
                for c in cs:
                    f.append(c.formula)
                    v.extend(c.variables.list)
                from typescogomo.variables import Variables
                c = Context(formula=And(f), variables=Variables(v))
                contexts.append(c)
        if len(contexts) > 0:
            return contexts
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

    def get_all_goals_with_name(self, name, copies=False):
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
                    result.extend(child.get_all_goals_with_name(name, copies))
        return result

    def get_goal_with_name(self, name) -> 'CGTGoal':
        """Return the goal of name 'name'"""
        res = self.get_all_goals_with_name(name)
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
            contract.refines(
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
        for contract in self.contracts:
            contract.remove_contextual_assumptions()
            contract.add_assumptions(context)
        self.consolidate_bottom_up()

    def add_context(self, context: Context):
        """Add the context as assumptions of all the contracts in the node"""
        if context is not None:
            for contract in self.contracts:
                contract.add_assumptions(context)

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
        for contract in self.contracts:
            for expectation in expectations:
                if len(list(set(contract.variables.list) & set(expectation.variables.list))) > 0:
                    if contract.guarantees.are_satisfiable_with(expectation.guarantees):
                        contract.add_assumptions(expectation.assumptions.list)

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

        goals_to_substitute = self.get_all_goals_with_name(goal_name)
        goals_substitute = self.get_all_goals_with_name(goal_name_update)

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

    def abstract_guarantees_of(self, goal_name: str, guarantees: Guarantees, abstract_name: str = None):

        goals = self.get_all_goals_with_name(goal_name)
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
            a_list.append(c.assumptions.formula)
        return Or(a_list)

    def get_ltl_guarantees(self):
        g_list = []
        for c in self.contracts:
            g_list.append(c.guarantees.formula)
        return And(g_list)

    def __str__(self, level=0):
        """Override the print behavior"""
        ret = "\t" * level + "GOAL:\t" + repr(self.name) + "\n"
        for n, contract in enumerate(self.contracts):
            if n > 0:
                ret += "\t" * level + "\t/\\ \n"

            a_context = contract.assumptions.get_kind("context")
            a_domain = contract.assumptions.get_kind("domain")
            a_expectation = contract.assumptions.get_kind("expectation")

            if a_context is not None:
                ret += "\t" * level + " CTX:\t" + ', '.join(map(str, a_context)) + "\n"

            if a_domain is not None:
                ret += "\t" * level + " DOM:\t" + ', '.join(map(str, a_domain)) + "\n"

            if a_expectation is not None:
                ret += "\t" * level + " EXP:\t" + ', '.join(map(str, a_expectation)) + "\n"

            ret += "\t" * level + "  A:\t" + str(contract.assumptions) + "\n"
            ret += "\t" * level + "  G:\t" + str(contract.guarantees) + "\n"

        ret += "\n"
        if self.refined_by is not None:
            ret += "\t" * level + "\t" + self.refined_with + "\n"
            level += 1
            for child in self.refined_by:
                try:
                    ret += child.__str__(level + 1)
                except:
                    print("ERROR IN PRINT")
        return ret
