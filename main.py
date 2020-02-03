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
            name="visit_locA_locB",
            contracts=[OrderedVisit(["locA", "locB", "locC"])]
        ),
        CGTGoal(
            context=({"time": "boolean", "day": "boolean"},
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
            contracts=[DelayedReaction("locB", "heavy_item_pickup")]
        )
    ]

    list_of_goals_2 = [
        CGTGoal(
            context=({"time": "boolean", "day": "boolean"},
                     ["time = day"]),
            name="visit_locA_locB",
            contracts=[BooleanContract(["a"], ["b"])]
        ),
        CGTGoal(
            context=({"time": "boolean", "day": "boolean"},
                     ["time = day"]),
            name="visit_locA_locB",
            contracts=[BooleanContract(["c"], ["d"])]
        ),
        CGTGoal(
            context=({"time": "boolean", "night": "boolean"},
                     ["time = night"]),
            name="visit_locA_locB",
            contracts=[BooleanContract(["e"], ["f"])]
        ),
        CGTGoal(
            context=None,
            name="pickup_HI_when_in_locA",
            contracts=[BooleanContract(["g"], ["h"])]
        )
    ]

    """Create cgt with the goals, it will automatically compose/conjoin them based on the context"""
    mission_cgt = create_contextual_cgt(list_of_goals_2)

    save_to_file(str(mission_cgt), file_path + "/cgt_1")

    """Adding Domain Properties (i.e. descriptive statements about the problem world (such as physical laws)
    E.g. a robot cannot be in two locations at the same time. These properties are intrinsic for each pattern"""
    mission_cgt.add_domain_properties()

    save_to_file(str(mission_cgt), file_path + "/cgt_2")

    """Adding Domain Hypotesis or Expecations (i.e. prescriptive assumptions on the environment
    E.g. The item weight 10kg so in order to pick it up the weight_power must be at least 10"""

    expectations = [
        Contract(variables={"weight_power":"1..100", "heavy_item_pickup":"boolean"},
                 assumptions=["G(weight_power > 10)"],
                 guarantees=["F(heavy_item_pickup)"])
    ]

    mission_cgt.add_expectations(expectations)

    save_to_file(str(mission_cgt), file_path + "/cgt_3")

    consolidate(mission_cgt)

    save_to_file(str(mission_cgt), file_path + "/cgt_4")

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


    #
    # """Looking in the library for components that can relax the contextual assumptions"""
    #
    # specification = Contract(variables=contextual_assumptions[0].variables,
    #                          guarantees=contextual_assumptions[0].assumptions)
    #
    # components = components_selection(component_library, specification)
    #
    # if len(components) > 0:
    #     new_goal = mapping(components, name="new_goal", abstract_on=specification)
    #     print("CGT BEFORE:\n" + str(mission_cgt))
    #     mission_cgt = composition([mission_cgt, new_goal])
    #     print("\n\nCGT AFTER:\n" + str(mission_cgt))
