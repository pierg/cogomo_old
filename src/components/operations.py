from src.components.components import *
import itertools as it
import operator


def components_selection(component_library: ComponentsLibrary, specification: Contract):
    if not isinstance(component_library, ComponentsLibrary):
        raise AttributeError

    if not isinstance(specification, Contract):
        raise AttributeError

    spec_variables = specification.get_variables()
    spec_assumptions = specification.get_list_assumptions()
    spec_guarantees = specification.get_list_guarantees()

    set_components_to_return = []

    try:
        candidates_compositions = component_library.extract_selection(spec_variables, spec_assumptions, spec_guarantees)
    except Exception as e:
        print("No further refinement possible")
        print(e)
        return []

    first_selected_components = greedy_selection(candidates_compositions)
    print("Selected components " + str([component.get_id() for component in first_selected_components]) + " out of " +
          str(len(candidates_compositions)) + " candidates")

    set_components_to_return.append(first_selected_components)

    components_to_search = first_selected_components.copy()
    component_already_searched = []

    while len(components_to_search) != 0:

        print("Looking for components that refine the assumptions")
        components_to_search_copy = components_to_search.copy()

        for component in components_to_search_copy:

            """Remove component from list of components to search 
            and keep track that it has been searched (avoid loops)"""
            components_to_search.remove(component)
            component_already_searched.append(component)

            component_variables = component.get_variables()
            component_assumptions = component.get_list_assumptions()

            if "TRUE" in component_assumptions:
                continue

            variables = component_variables.copy()
            variables.update(spec_variables)

            """Extract all candidate compositions that can provide the assumptions, if they exists"""
            try:
                candidates_compositions = component_library.extract_selection(variables, spec_assumptions,
                                                                              component_assumptions)
            except Exception as e:
                print(e)
                print("No selection found")
                continue

            """Greedly select one composition"""
            new_selected_components = greedy_selection(candidates_compositions)
            print("Selected components " + str(
                [component.get_id() for component in new_selected_components]) + " out of " +
                  str(len(candidates_compositions)) + " candidates")

            if new_selected_components not in set_components_to_return:
                set_components_to_return.append(new_selected_components)

            """Add components to be searched only if they have not already been searched before"""
            for comp in new_selected_components:
                if comp not in component_already_searched:
                    components_to_search.append(comp)

    """Flattening list of selections and eliminating duplicates"""
    flat_list_refining_components = list(set([item for sublist in set_components_to_return for item in sublist]))

    print(str(len(flat_list_refining_components)) +
          " components found in the library that composed refine the specifications:")

    for n, l in enumerate(set_components_to_return):
        ret = "\t" * n
        for component in l:
            ret += component.get_id() + " "
        print(ret)

    return flat_list_refining_components


def greedy_selection(candidate_compositions):
    """
    Scan all the possible compositions and compute costs for each of them,
    If there are multiple compositions iwth the same cost, pick the more refined one
    (bigger assumptions, smaller guarantees)
    :param: List of List
    """

    """If only one candidate return that one"""
    if len(candidate_compositions) == 1:
        print("\tgreedly seelected the only candidate")
        return candidate_compositions[0]

    best_candidates = []
    lowest_cost = float('inf')

    print("Choosing greedly one composition...")

    for composition in candidate_compositions:
        cost = 0
        for component in composition:
            cost += component.cost()
            """Adding a cost for the number of components"""
            cost += 0.1
        if cost < lowest_cost:
            best_candidates = [composition]
        elif cost == lowest_cost:
            best_candidates.append(composition)

    if len(best_candidates) == 1:
        print("\tgreedly seelected the best candidate based on cost")
        return best_candidates[0]

    else:
        """Keep score of the candidates"""

        """Dict: candidate_id -> points"""
        candidates_points = {}
        for candidate in best_candidates:
            candidates_points[tuple(candidate)] = 0

        print("Generating pairs for all " + str(len(best_candidates)) + " candidates")
        candidate_pairs = it.combinations(best_candidates, 2)

        n_comparisons = 0
        for candidate_a, candidate_b in candidate_pairs:

            contract_a = Contract()
            contract_b = Contract()

            for component_a in candidate_a:
                contract_a.add_variables(component_a.get_variables())
                contract_a.add_assumptions(component_a.get_list_assumptions())
                contract_a.add_guarantees(component_a.get_list_guarantees())

            for component_b in candidate_b:
                contract_b.add_variables(component_b.get_variables())
                contract_b.add_assumptions(component_b.get_list_assumptions())
                contract_b.add_guarantees(component_b.get_list_guarantees())

            if contract_a.is_refined_by(contract_b):
                candidates_points[tuple(candidate_a)] += 1
            else:
                candidates_points[tuple(candidate_b)] += 1

            n_comparisons += 1

        print(str(n_comparisons) + " comparisons have been made")
        """Extract the candidate with the highest score (the most refined)"""
        best_candidate = max(candidates_points.items(), key=operator.itemgetter(1))[0]

        print("\tgreedly seelected the best candidate based on biggest assumption set")
        return list(best_candidate)
