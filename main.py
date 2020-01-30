import os
import sys

from src.patterns.patterns import *
from src.goals.operations import *
from src.components.operations import *

sys.path.append(os.path.join(os.getcwd(), os.path.pardir))

if __name__ == "__main__":

    """The designer specifies a mission using the patterns and building a tree (CGT)
        The input can also be from a txt file or json
        In addition to the patterns to use the designer specifies also in which context the goal can be active"""

    list_of_goals = [
        CGTGoal(
            context=({"time": "boolean", "day": "boolean"},
                     ["time = day"]),
            name="visit_locA_locB",
            contracts=[OrderedVisit(["locA", "locB", "locC"])]
        ),
        CGTGoal(
            context=({"time": "boolean", "night": "boolean"},
                     ["time = day"]),
            name="visit_locA_locB",
            contracts=[OrderedVisit(["locA", "locB"])]
        ),
        CGTGoal(
            context=({"time": "boolean", "night": "boolean"},
                     ["time = night"]),
            name="visit_locA_locB",
            contracts=[GlobalAvoidance(["locC"])]
        ),
        CGTGoal(
            context=None,
            name="pickup_HI_when_in_locA",
            contracts=[DelayedReaction("locB", "HI_pickup")]
        )
    ]

    """Create cgt with the goals, it will automatically compose/conjoin them based on the context"""
    mission_cgt = create_contextual_cgt(list_of_goals)

    """Adding contextual/instantiations assumptions to the mission (e.g. the item weights 10 kg)"""
    contextual_assumptions = [
        Contract(variables={"weight_power": "0..15"}, assumptions=["G(weight_power > 10)"])
    ]

    """Adding physical assumptions to the mission (e.g. locations cannot be the same)"""
    for element in mission:
        element.add_physical_assumptions()

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

    mission_cgt = composition(goal_list)

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
        new_goal = mapping(components, name="new_goal", abstract_on=specification)
        print("CGT BEFORE:\n" + str(mission_cgt))
        mission_cgt = composition([mission_cgt, new_goal])
        print("\n\nCGT AFTER:\n" + str(mission_cgt))
