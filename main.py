import os
import sys

from src.patterns.patterns import *
from src.goals.operations import *
from src.components.operations import *

sys.path.append(os.path.join(os.getcwd(), os.path.pardir))

if __name__ == "__main__":

    """The designer specifies a mission using the patterns (also a structured txt file)"""
    mission = [
        OrderedVisit("visit_locations_A_B", ("locA", "locB")),
        DelayedReaction("pickup_HI_when_in_A", "locA", "HI_pickup")
    ]

    """Create a goal for each element of the mission"""
    goal_list = []

    for element in mission:
        goal_list.append(CGTGoal(element.get_name(), contracts=[element]))

    mission_cgt = compose_goals(goal_list)

    """Adding physical assumptions to the mission (e.g. locations cannot be the same)"""
    for element in mission:
        element.add_physical_assumptions()

    """Adding contextual assumptions to the mission (e.g. the item weights 10 kg)"""
    contextual_assumptions = [
        Contract(variables={"weight_power": "0..15"}, assumptions=["G(weight_power > 10)"])
    ]

    for element in mission:
        element.add_context(
            name="pickup",
            context=contextual_assumptions
        )

    """Building  the CGT with the Mission"""

    """Create a goal for each element of the mission"""
    goal_list = []

    for element in mission:
        goal_list.append(CGTGoal(element.get_name(), contracts=[element]))

    mission_cgt = compose_goals(goal_list)

    """Instantiating a Library of Componenents"""
    component_library = ComponentsLibrary(name="robots")

    component_library.add_components(
        [
            Component(
                id="robot_1",
                variables={"robot_power": "0..15"},
                guarantees=["robot_power = 7"],
            ),
            Component(
                id="robot_2",
                variables={"robot_power": "0..15"},
                guarantees=["robot_power >= 8"],
            ),
            Component(
                id="robot_3",
                variables={"robot_power": "0..15"},
                guarantees=["robot_power >= 9"],
            ),
            Component(
                id="collaborate",
                variables={"robot_power": "0..15",
                           "weight_power": "0..15"},
                assumptions=["robot_power_port_1 >= 8", "robot_power_port_2 >= 8"],
                guarantees=["G(weight_power > 12)"]
            )
        ])

    print(mission_cgt)


    """Looking in the library for components that can relax the contextual assumptions"""

    specification = Contract(variables=contextual_assumptions[0].get_variables(),
                             guarantees=contextual_assumptions[0].get_list_assumptions())

    components = components_selection(component_library, specification)

    if len(components) > 0:
        new_goal = mapping_to_goal(components, name="new_goal", abstract_on=specification)
        print("CGT BEFORE:\n" + str(mission_cgt))
        mission_cgt = compose_goals([mission_cgt, new_goal])
        print("\n\nCGT AFTER:\n" + str(mission_cgt))



