from typing import List, Dict

from src.contracts.helpers import incomposable_check, duplicate_contract
from src.contracts.contract import Contract
from src.checks.nsmvhelper import *

import itertools as it


class Component(Contract):

    def __init__(self,
                 id: str = None,
                 description: str = None,
                 variables: Dict[str, str] = None,
                 assumptions: List[str] = None,
                 guarantees: List[str] = None):
        super().__init__(assumptions=assumptions,
                         variables=variables,
                         guarantees=guarantees)
        self.id = id

        if description is None:
            self.description = ""
        elif isinstance(description, str):
            self.description = description
        else:
            raise AttributeError

    def get_id(self):
        return self.id

    def __str__(self):
        """Override the print behavior"""
        astr = 'componend id:\t' + self.id + '\n'
        astr += 'assumptions:\t'
        for assumption in self.assumptions:
            astr += str(assumption) + ', '
        astr = astr[:-2] + '\nguarantees:\t'
        for guarantee in self.guarantees:
            astr += str(guarantee) + ', '
        return astr[:-2] + '\n'


class ComponentsLibrary:

    def __init__(self,
                 name=None,
                 list_of_components=None):

        if name is None:
            raise AttributeError
        elif isinstance(name, str):
            self.name = name
        else:
            raise AttributeError

        if list_of_components is None:
            self.list_of_components = []
        elif isinstance(list_of_components, list):
            self.list_of_components = list_of_components
        else:
            raise AttributeError

    def add_component(self, component):
        if isinstance(component, Component):
            self.list_of_components.append(component)
        else:
            raise AttributeError

    def add_components(self, components_list):
        if isinstance(components_list, list):
            for component in components_list:
                self.add_component(component)
        else:
            raise AttributeError

    def get_components(self):
        return self.list_of_components

    def _search_candidate_compositions(self, variables: Dict[str, str], assumptions: List[str], to_be_refined: List[str]):

        candidates_for_each_proposition = {}

        if len(to_be_refined) == 0:
            return []

        for proposition in to_be_refined:

            """Check if any component refine the to_be_refined"""
            for component in self.get_components():

                if are_implied_in([component.variables, variables], component.guarantees, [proposition]):

                    """Check Assumptions Consistency"""
                    if len(assumptions) > 0:

                        props_to_check = set()

                        for assumption in assumptions:
                            props_to_check.add(assumption)

                        for assumption in component.assumptions:
                            props_to_check.add(assumption)

                        all_variables = variables.copy()
                        all_variables.update(component.variables)

                        satis = check_satisfiability(all_variables, list(props_to_check))

                        """If the contract has compatible assumptions, add it to the list of contracts 
                        that can refine to_be_refined"""
                        if satis:
                            if proposition in candidates_for_each_proposition:
                                candidates_for_each_proposition[proposition].append(component)
                            else:
                                candidates_for_each_proposition[proposition] = [component]
                    else:
                        if proposition in candidates_for_each_proposition:
                            candidates_for_each_proposition[proposition].append(component)
                        else:
                            candidates_for_each_proposition[proposition] = [component]

        """Check that all the propositions of to_be_refined can be refined"""
        if not all(props in candidates_for_each_proposition for props in to_be_refined):
            raise Exception("The specification cannot be refined further with the components in the library")

        """Create candidate compositions, each refining to_be_refined"""
        candidates_compositions = [[value for (key, value) in zip(candidates_for_each_proposition, values)]
                                   for values in it.product(*candidates_for_each_proposition.values())]

        """Filter incomposable candidates"""
        candidates_compositions[:] = it.filterfalse(incomposable_check, candidates_compositions)

        return candidates_compositions

    def extract_selection(self, variables: Dict[str, str], assumptions: List[str], to_be_refined: List[str]):
        """
        Extract all candidate compositions in the library that once combined refine 'to_be_refined'
        and are consistent with assumptions
        :param variables: 
        :param assumptions: List of assumptions
        :param to_be_refined: List of propositions
        :return: List
        """

        """Dividing the propositions to be refined, if they are general ports or not"""
        general_to_be_refined = []
        specific_to_be_refined = []

        for prop in to_be_refined:
            if "port" in prop:
                general_to_be_refined.append(prop)
            else:
                specific_to_be_refined.append(prop)

        specific_candidates_compositions = self._search_candidate_compositions(variables, assumptions,
                                                                               specific_to_be_refined)

        general_candidates_compositions = self._search_candidate_compositions(variables, assumptions,
                                                                              general_to_be_refined)

        """Remove the candidates that having the same component refining more general ports"""
        general_candidates_compositions[:] = it.filterfalse(duplicate_contract, general_candidates_compositions)

        all_candidates = []

        if len(specific_candidates_compositions) > 0:
            all_candidates = specific_candidates_compositions
            for candidate_specific in specific_candidates_compositions:
                for candidate_general in general_candidates_compositions:
                    candidate_specific.append(candidate_general)

        elif len(general_candidates_compositions) > 0:
            all_candidates = general_candidates_compositions

        """Eliminate duplicate components (a component might refine multiple propositions)"""
        for i, c in enumerate(all_candidates):
            c = list(set(c))
            all_candidates[i] = c

        print(str(len(all_candidates)) + " candidate compositions found:")
        for i, candidate in enumerate(all_candidates):
            print("\tcandidate_" + str(i) + ":")
            for component in candidate:
                print(str(component))
            print("\n")

        if len(all_candidates) == 0:
            raise Exception("No candidate available")

        return all_candidates

