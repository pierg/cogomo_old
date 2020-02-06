from typing import List, Dict
from src.contracts.helpers import incomposable_check, duplicate_contract
from src.contracts.contract import Contract
from src.checks.nsmvhelper import *
import itertools as it


class Component(Contract):
    """Component class extending Contract"""

    def __init__(self,
                 component_id: str,
                 description: str = None,
                 variables: Dict[str, str] = None,
                 assumptions: List[str] = None,
                 guarantees: List[str] = None):
        super().__init__(assumptions=assumptions,
                         variables=variables,
                         guarantees=guarantees)

        """Component ID"""
        self.__id = component_id

        """Component Description"""
        if description is None:
            self.__description = ""
        else:
            self.__description = description

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, value: str):
        self.__id = value

    @property
    def description(self):
        return self.__description

    @description.setter
    def description(self, value: str):
        self.__description = value

    def __str__(self):
        """Override the print behavior"""
        astr = '  component id:\t ' + self.id + '\n'
        astr += '  assumptions:\t[ '
        for assumption in self.assumptions:
            astr += str(assumption) + ', '
        astr = astr[:-2] + ' ]\n  guarantees:\t[ '
        for guarantee in self.unsaturated_guarantees:
            astr += str(guarantee) + ', '
        return astr[:-2] + ' ]\n'


class ComponentsLibrary:
    """Component Library defined a list of components and the operations on them"""

    def __init__(self,
                 name: str,
                 components: List[Component] = None):

        """Name of the Component Library"""
        self.__name = name

        """List of Components in the Library"""
        if components is None:
            self.__components = []
        else:
            self.__components = components

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def components(self):
        return self.__components

    @components.setter
    def components(self, value: List[Component]):
        self.__components = value

    def add_component(self, component: Component):

        self.components.append(component)

    def add_components(self, components: List[Component]):

        for component in components:
            self.add_component(component)

    def _search_candidate_compositions(self,
                                       variables: Dict[str, str],
                                       assumptions: List[str],
                                       to_be_refined: List[str]) -> List[List['Component']]:
        """Extract all candidate compositions in the library whose guarantees, once combined,
        refine 'to_be_refined' and are consistent 'assumptions'"""

        candidates_for_each_proposition = {}

        if len(to_be_refined) == 0:
            return []

        for proposition in to_be_refined:

            """Check if any component refine the to_be_refined"""
            for component in self.components:

                if are_implied_in([component.variables, variables], component.unsaturated_guarantees, [proposition]):

                    if len(assumptions) > 0 and assumptions[0] is not "TRUE":

                        """Check if contracts have compatible assumptions with the one provided"""
                        props_to_check = set()

                        for assumption in assumptions:
                            props_to_check.add(assumption)

                        for assumption in component.assumptions:
                            props_to_check.add(assumption)

                        all_variables = variables.copy()
                        all_variables.update(component.variables)

                        compatible = check_satisfiability(all_variables, list(props_to_check))
                    else:
                        compatible = True

                    """If the contract has compatible assumptions, add it to the list of contracts 
                    that can refine to_be_refined"""
                    if compatible:
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

    def extract_selection(self,
                          variables: Dict[str, str],
                          assumptions: List[str],
                          to_be_refined: List[str]) -> List[List['Component']]:
        """Extract all candidate compositions in the library whose guarantees, once combined, refine 'to_be_refined'
        and are consistent 'assumptions'. It also performs other tasks (filters and select the candidates)."""

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


class BooleanComponent(Component):

    def __init__(self,
                 component_id: str,
                 assumptions: List[str],
                 guarantees: List[str]):

        variables: Dict[str, str] = {}

        for a in assumptions:
            variables.update({a: "boolean"})
        for g in guarantees:
            variables.update({g: "boolean"})

        super().__init__(component_id=component_id,
                         variables=variables,
                         assumptions=assumptions,
                         guarantees=guarantees)
