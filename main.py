import os
import sys

from goals.context import Context
from src.patterns.patterns import *
from src.goals.operations import *
from src.components.operations import *
from src.helper.parser import *

file_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(os.getcwd(), os.path.pardir))

if __name__ == "__main__":
    """The designer specifies a mission using the predefined catalogue of patterns 
       In addition to the patterns to use the designer specifies also in which context each goal can be active"""

    """Import the goals from file"""
    # list_of_goals = parse("./input_files/robots_patterns_simple.txt")

    """Or define them here"""
    """Order Visit pattern of 3 locations in the context 'day'"""
    """Order Visit pattern of 2 locations in the context '!day'"""
    """Global Avoidance pattern of 1 location in the context '!day'"""
    """DelayedReaction pattern in all contexts (always pickup an item when in locaction A)"""
    list_of_goals = [
        CGTGoal(
            context=(Context(LTL("day"))),
            name="a-b-c",
            contracts=[OrderedVisit(["locA", "locB", "locC"])]
        ),
        CGTGoal(
            context=(Context(LTL("!day"))),
            name="a-b",
            contracts=[OrderedVisit(["locA", "locB"])]
        ),
        CGTGoal(
            context=(Context(LTL("!day"))),
            name="never-c",
            contracts=[GlobalAvoidance("locC")]
        ),
        CGTGoal(
            name="a->pickup",
            contracts=[DelayedReaction("locB", "heavy_item_pickup")]
        )
    ]

    """Create cgt with the goals, it will automatically compose/conjoin them based on the context"""
    cgt = create_contextual_simple_cgt(list_of_goals)

    save_to_file(str(cgt), file_path + "/cgt_1_contexual")

    """Adding Domain Properties (i.e. descriptive statements about the problem world (such as physical laws)
    E.g. a robot cannot be in two locations at the same time. These properties are intrinsic in each pattern"""
    cgt.add_domain_properties()

    save_to_file(str(cgt), file_path + "/cgt_2_domain")

    """Adding Domain Hypothesis or Expectations (i.e. prescriptive assumptions on the environment
    E.g. In the environment of deployment of the mission the item weight 10kg so in order to pick it up 
    there is a new assumption where the 'weight_power' must be at least 10"""
    expectations = [
        Contract(variables=[BoundedNat("weight_power"), Boolean("heavy_item_pickup")],
                 assumptions=[Assumption("G(weight_power > 10)", kind="expectation")],
                 guarantees=[Guarantee("G(heavy_item_pickup)")])
    ]

    cgt.add_expectations(expectations)

    save_to_file(str(cgt), file_path + "/cgt_3_expectations")

    """Import library of components from file"""

    """Instantiating a Library of Components"""
    component_library = ComponentsLibrary(name="robots")

    """Import library of components from file"""
    # list_of_components = parse("./input_files/robots_components_simple.txt")

    """Or define them here"""
    component_library.add_components(
        [
            Component(
                component_id="robot_1",
                variables=[BoundedNat("robot_power")],
                guarantees=[Guarantee("robot_power = 7")],
            ),
            Component(
                component_id="robot_2",
                variables=[BoundedNat("robot_power")],
                guarantees=[Guarantee("robot_power >= 8")],
            ),
            Component(
                component_id="robot_3",
                variables=[BoundedNat("robot_power")],
                guarantees=[Guarantee("robot_power >= 9")],
            ),
            Component(
                component_id="collaborate",
                variables=[BoundedNatPort(port_type="robot_power", name="power1"),
                           BoundedNatPort(port_type="robot_power", name="power2"),
                           BoundedNat("weight_power")],
                assumptions=[Assumption("power1 >= 8"),
                             Assumption("power2 >= 8")],
                guarantees=[Guarantee("G(weight_power > 12)")]
            ),
            Component(
                component_id="pick_up_item",
                variables=[Boolean("heavy_item_pickup"), BoundedNat("weight_power")],
                assumptions=[Assumption("G(weight_power > 12)")],
                guarantees=[Guarantee("G(heavy_item_pickup)")]
            )
        ]
    )

    """Looking in the library for components for goals that can refine all the goals to pickup an object 'a->pickup'"""
    goals_to_map = cgt.get_all_goals("a->pickup")

    for goal in goals_to_map:
        mapping(component_library, goal)

    save_to_file(str(cgt), file_path + "/cgt_4_mapping")

    """Refinements formalize a notion of substitutability. We can substitute goals with most refined one.
    For example, from 'cgt_4_mapping' we can substitute 'a->pickup' with 'collaborate||robot_2||pick_up_item||robot_3'"""

    cgt.substitute_with("a->pickup", "collaborate||pick_up_item||robot_2||robot_3")

    """Notice how all the tree is consistent with the substitution 
    that had relaxed the expectation 'G(weight_power > 10)' from all the CGT"""
    save_to_file(str(cgt), file_path + "/cgt_5_substitution")

    """The designer can specify to 'abstract' a goal to have fewer guarantees, however CoGoMo will keep the guarantees
    that are needed to 'relax' assumptions in other goals of the trees"""

    variables = [Boolean("locB"), Boolean("heavy_item_pickup")]
    guarantees = [Guarantee("G(locB -> F(heavy_item_pickup))")]
    cgt.abstract_guarantees_of("collaborate||pick_up_item||robot_2||robot_3",
                               guarantees, variables, "pick_up_item_abstracted")
    save_to_file(str(cgt), file_path + "/cgt_6_abstracted")


