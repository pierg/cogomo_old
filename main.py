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
            context=([Boolean("time"), Boolean("day")],
                     ["time = day"]),
            name="a-b-c",
            contracts=[OrderedVisit(["locA", "locB", "locC"])]
        ),
        CGTGoal(
            context=([Boolean("time"), Boolean("day")],
                     ["time = !day"]),
            name="a-b",
            contracts=[OrderedVisit(["locA", "locB"])]
        ),
        CGTGoal(
            context=([Boolean("time"), Boolean("day")],
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

    save_to_file(str(cgt), file_path + "/cgt_1_contexual")

    """Adding Domain Properties (i.e. descriptive statements about the problem world (such as physical laws)
    E.g. a robot cannot be in two locations at the same time. These properties are intrinsic for each pattern"""
    cgt.add_domain_properties()

    save_to_file(str(cgt), file_path + "/cgt_2_domain")

    """Adding Domain Hypothesis or Expectations (i.e. prescriptive assumptions on the environment
    E.g. The item weight 10kg so in order to pick it up the weight_power must be at least 10"""
    expectations = [
        Contract(variables=[BoundedNat("weight_power"), Boolean("heavy_item_pickup")],
                 assumptions=["G(weight_power > 10)"],
                 guarantees=["G(heavy_item_pickup)"])
    ]

    cgt.add_expectations(expectations)

    save_to_file(str(cgt), file_path + "/cgt_3_expectations")

    """Instantiating a Library of Components"""
    component_library = ComponentsLibrary(name="robots")

    component_library.add_components(
        [
            Component(
                component_id="robot_1",
                variables=[BoundedNat("robot_power")],
                guarantees=["robot_power = 7"],
            ),
            Component(
                component_id="robot_2",
                variables=[BoundedNat("robot_power")],
                guarantees=["robot_power >= 8"],
            ),
            Component(
                component_id="robot_3",
                variables=[BoundedNat("robot_power")],
                guarantees=["robot_power >= 9"],
            ),
            Component(
                component_id="collaborate",
                variables=[BoundedNatPort(port_type="robot_power", name="power1"),
                           BoundedNatPort(port_type="robot_power", name="power2"),
                           BoundedNat("weight_power")],
                assumptions=["power1 >= 8", "power2 >= 8"],
                guarantees=["G(weight_power > 12)"]
            ),
            Component(
                component_id="pick_up_item",
                variables=[Boolean("heavy_item_pickup"), BoundedNat("weight_power")],
                assumptions=["G(weight_power > 12)"],
                guarantees=["G(heavy_item_pickup)"]
            )
        ])

    """Looking in the library for components that can relax the Expectation"""
    goals_to_map = cgt.get_all_goal("a->pickup")

    for goal in goals_to_map:
        mapping(component_library, goal)

    save_to_file(str(cgt), file_path + "/cgt_4_mapping")
