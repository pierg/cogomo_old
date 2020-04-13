from typing import Dict
from src.contracts.helpers import incomposable_check
from src.contracts.contract import *

import itertools as it

from typescogomo.formulae import LTL, LTLs


class NoComponentsAvailable(Exception):
    pass


class Component(Contract):
    """Component class extending Contract"""

    def __init__(self,
                 component_id: str,
                 description: str = None,
                 assumptions: Assumptions = None,
                 guarantees: Guarantees = None):
        super().__init__(assumptions=assumptions,
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
        astr += '  variables:\t[ '
        for var in self.variables.list:
            astr += str(var) + ', '
        astr = astr[:-2] + ' ]\n  assumptions      :\t[ '
        for assumption in self.assumptions.list:
            astr += assumption.formula + ', '
        astr = astr[:-2] + ' ]\n  guarantees_satur :\t[ '
        for guarantee in self.guarantees.list:
            astr += guarantee.saturated + ', '
        astr = astr[:-2] + ' ]\n  guarantees_unsat :\t[ '
        for guarantee in self.guarantees.list:
            astr += guarantee.unsaturated + ', '
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

    def extract_selection(self,
                          assumptions: Assumptions,
                          to_be_refined: LTLs) -> List[List['Component']]:
        """Extract all candidate compositions in the library whose guarantees, once combined, refine 'to_be_refined'
        and are consistent 'assumptions'. It also performs other tasks (filters and select the candidates)."""

        """How many different variables are needed for each port"""
        ports_n: Dict[str, int] = {}
        variables = to_be_refined.variables
        for v in variables.list:
            if hasattr(v, "port_type"):
                if v.port_type not in ports_n:
                    ports_n[v.port_type] = 1
                else:
                    ports_n[v.port_type] += 1
            else:
                if v.name not in ports_n:
                    ports_n[v.name] = 1
                else:
                    ports_n[v.name] += 1

        candidates_for_each_proposition = {}

        if len(to_be_refined.list) == 0:
            return []

        for formula in to_be_refined.list:

            """Check if any component guarantees refine the to_be_refined"""
            for component in self.components:

                if component.guarantees.formula <= formula:

                    """Check if contracts have compatible assumptions with the one provided"""
                    compatible = assumptions.are_satisfiable_with(component.assumptions)

                    """If the contract has compatible assumptions, add it to the list of contracts 
                    that can refine to_be_refined"""
                    if compatible:
                        if formula in candidates_for_each_proposition:
                            if component not in candidates_for_each_proposition[formula]:
                                candidates_for_each_proposition[formula].append(component)
                        else:
                            candidates_for_each_proposition[formula] = [component]

        """Check that all the propositions of to_be_refined can be refined"""
        if not all(props in candidates_for_each_proposition for props in to_be_refined.list):
            raise NoComponentsAvailable(
                "The specification cannot be refined further with the components in the library")

        """Create candidate compositions, each refining to_be_refined"""
        candidates_compositions = [[value for (key, value) in zip(candidates_for_each_proposition, values)]
                                   for values in it.product(*candidates_for_each_proposition.values())]

        """Eliminate duplicate components (a component might refine multiple propositions)"""
        for i, c in enumerate(candidates_compositions):
            c = list(set(c))
            candidates_compositions[i] = c

        """Eliminate candidates that cannot be composed"""
        candidates_compositions[:] = it.filterfalse(incomposable_check, candidates_compositions)

        """List of candidates to remove"""
        candidates_compositions_filtered = []

        """Filter candidates that cannot provide for all the ports"""
        for candidate in list(candidates_compositions):

            comps_id = set()
            for comp in candidate:
                comps_id.add(comp.id)

            already_there = False

            for candidate_filtered in candidates_compositions_filtered:

                comps_id_filtered = set()

                for comp in candidate_filtered:
                    comps_id_filtered.add(comp.id)

                if all(c in comps_id for c in comps_id_filtered):
                    already_there = True

            if already_there:
                continue

            ports_n_candidate: Dict[str, int] = {}

            for component in candidate:
                for v in component.variables.list:
                    if v.port_type not in ports_n_candidate:
                        ports_n_candidate[v.port_type] = 1
                    else:
                        ports_n_candidate[v.port_type] += 1

            all_covered = True
            for port, n in ports_n_candidate.items():
                if port in ports_n and ports_n_candidate[port] < ports_n[port]:
                    all_covered = False
            if all_covered:
                candidates_compositions_filtered.append(candidate)

        print(str(len(candidates_compositions_filtered)) + " candidate compositions found:")
        for i, candidate in enumerate(candidates_compositions_filtered):
            print("\tcandidate_" + str(i) + ":")
            for component in candidate:
                print(str(component))
            print("\n")

        if len(candidates_compositions_filtered) == 0:
            raise NoComponentsAvailable

        else:
            return candidates_compositions_filtered


class BooleanComponent(Component):

    def __init__(self,
                 component_id: str,
                 assumptions_str: List[str],
                 guarantees_str: List[str]):

        assumptions = []
        guarantees = []

        for a in assumptions_str:
            assumptions.append(Assumption(a, Variables(Boolean(a))))

        for g in guarantees_str:
            guarantees.append(Guarantee(g, Variables(Boolean(g))))

        assumptions = Assumptions(assumptions)
        guarantees = Guarantees(guarantees)

        guarantees.saturate_with(assumptions)

        super().__init__(component_id=component_id,
                         assumptions=assumptions,
                         guarantees=guarantees)


class SimpleComponent(Component):

    def __init__(self,
                 component_id: str,
                 assumptions: List[str],
                 guarantees: List[str]):

        assumptions_obj = []
        guarantees_obj = []

        from typescogomo.variables import extract_variable

        for a in assumptions:
            assumptions_obj.append(Assumption(a, extract_variable(a)))

        for g in guarantees:
            guarantees_obj.append(Guarantee(g, extract_variable(g)))

        assumptions_obj = Assumptions(assumptions_obj)
        guarantees_obj = Guarantees(guarantees_obj)

        guarantees_obj.saturate_with(assumptions_obj)

        super().__init__(component_id=component_id,
                         assumptions=assumptions_obj,
                         guarantees=guarantees_obj)
