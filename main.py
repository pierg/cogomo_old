import os
import sys

from src.patterns.patterns import *
from src.goals.operations import *
from src.components.operations import *

file_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(os.getcwd(), os.path.pardir))

if __name__ == "__main__":
    """The designer specifies a mission using the patterns and building a tree (CGT)
        The input can also be from a txt file or json
        In addition to the patterns to use the designer specifies also in which context the goal can be active"""

    list_of_goals = [
        CGTGoal(
            context=({"time": "boolean", "day": "boolean"},
                     ["time = day"]),
            name="a-b-c",
            contracts=[OrderedVisit(["locA", "locB", "locC"])]
        ),
        CGTGoal(
            context=({"time": "boolean", "day": "boolean"},
                     ["time = !day"]),
            name="a-b",
            contracts=[OrderedVisit(["locA", "locB"])]
        ),
        CGTGoal(
            context=({"time": "boolean", "day": "boolean"},
                     ["time = !day"]),
            name="never-c",
            contracts=[GlobalAvoidance("locC")]
        ),
        CGTGoal(
            name="a->pickup",
            contracts=[DelayedReaction("locB", "heavy_item_pickup")]
        )
    ]

    """Create cgt with the goals, it will automatically compose/conjoin them based on the context"""
    cgt = create_contextual_cgt(list_of_goals)

    save_to_file(str(cgt), file_path + "/cgt_1b")

    """Adding Domain Properties (i.e. descriptive statements about the problem world (such as physical laws)
    E.g. a robot cannot be in two locations at the same time. These properties are intrinsic for each pattern"""
    cgt.add_domain_properties()

    save_to_file(str(cgt), file_path + "/cgt_2b")

    """Adding Domain Hypothesis or Expectations (i.e. prescriptive assumptions on the environment
    E.g. The item weight 10kg so in order to pick it up the weight_power must be at least 10"""
    expectations = [
        Contract(variables={"weight_power": "1..100", "heavy_item_pickup": "boolean"},
                 assumptions=["G(weight_power > 10)"],
                 guarantees=["G(heavy_item_pickup)"])
    ]

    cgt.add_expectations(expectations)

    save_to_file(str(cgt), file_path + "/cgt_3b")

    """Instantiating a Library of Components"""
    component_library = ComponentsLibrary(name="robots")

    component_library.add_components(
        [
            Component(
                component_id="robot_1",
                variables={"robot_power": "0..15"},
                guarantees=["robot_power = 7"],
            ),
            Component(
                component_id="robot_2",
                variables={"robot_power": "0..15"},
                guarantees=["robot_power >= 8"],
            ),
            Component(
                component_id="robot_3",
                variables={"robot_power": "0..15"},
                guarantees=["robot_power >= 9"],
            ),
            Component(
                component_id="collaborate",
                variables={"robot_power": "0..15",
                           "weight_power": "0..15"},
                assumptions=["robot_power_port_1 >= 8", "robot_power_port_2 >= 8"],
                guarantees=["G(weight_power > 12)"]
            ),
            Component(
                component_id="pick_up_item",
                variables={"heavy_item_pickup": "boolean",
                           "weight_power": "0..15"},
                assumptions=["G(weight_power > 12)"],
                guarantees=["G(heavy_item_pickup)"]
            )
        ])

    print(cgt)

    """Looking in the library for components that can relax the Expectation"""
    goal_to_map = cgt.get_goal("a->pickup")
    mapping(component_library, goal_to_map)

    print(cgt)
