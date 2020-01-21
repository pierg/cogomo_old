import os
import sys

from src.patterns import *
from src.context import *

from src.operations import *

sys.path.append(os.path.join(os.getcwd(), os.path.pardir))

if __name__ == "__main__":

    Collaborate("collaborate", "weight_power > 10")

    """The designer specifies the mission"""
    visit_locations = OrderedVisit("visit_locations_A_B", ("locA", "locB"))
    pickup_object = DelayedReaction("pickup_HI_when_in_A", "locA", "HI_pickup")


    """Adding contextual assumptions relative to location and the lifting the weight"""
    visit_locations.add_physical_assumptions()
    pickup_object.add_variable(("weight_power", "5..15"))
    pickup_object.add_assumption("G(weight_power > 10)")


    """Building  the CGT with the Mission"""
    goals = {}
    goals["visit_locations"] = CGTGoal("visit_locations", contracts=[visit_locations])
    goals["pickup_object"] = CGTGoal("pickup_object", contracts=[pickup_object])

    goals["mission"] = compose_goals([goals["visit_locations"], goals["pickup_object"]])

    # print(goals["mission"])

    """Istanciating a Library of Componenents"""
    component_library = ComponentsLibrary(name="robots")

    component_library.add_components(
        [
            Component(
                id="robot_1",
                variables={"robot_power": "0..15"},
                guarantees="robot_power = 7",
            ),
            Component(
                id="robot_2",
                variables={"robot_power": "0..15"},
                guarantees="robot_power >= 8",
            ),
            Component(
                id="robot_3",
                variables={"robot_power": "0..15"},
                guarantees="robot_power >= 9",
            ),
            Component(
                id="collaborate",
                variables={"robot_power": "0..15",
                           "weight_power": "0..15"},
                assumptions=["robot_power_port_1 >= 8", "robot_power_port_2 >= 8"],
                guarantees="G(weight_power > 12)"
            )
        ])

    print(goals["mission"])

    specification = Contract(variables={"weight_power": "0..15"}, guarantees=["G(weight_power > 10)"])

    components = components_selection(component_library, specification)

    if len(components) > 0:
        new_goal = mapping_to_goal(components, name="new_goal", abstract_on=specification)
        goals["mission"] = compose_goals([goals["mission"], new_goal])
        print(goals["mission"])



