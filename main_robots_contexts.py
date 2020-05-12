import os
import sys

from goals.operations import create_contextual_cgt
from helper.tools import save_to_file
from src.goals.cgtgoal import *
from src.typescogomo.contexts import *
from src.contracts.patterns import *

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
            context=(Context(P_global(LTL("home")))),
            name="always-home",
            contracts=[OrderedVisit(["locA", "locB", "locC"])]
        ),
        CGTGoal(
            context=(Context(P_weakuntil_R(LTL("warehouse"), LTL("alarm")))),
            name="warehouse-pre-alarm",
            contracts=[OrderedVisit(["locX", "locY"])]
        ),
        CGTGoal(
            context=(Context(P_after_Q(P_until_R(LTL("warehouse"), LTL("!alarm")), LTL("alarm")))),
            name="warehouse-after-alarm",
            contracts=[OrderedVisit(["locAlarm"])]
        ),
        CGTGoal(
            context=(Context(P_after_Q_until_R(LTL("warehouse"), LTL("alarm"), LTL("!alarm")))),
            name="warehouse-after-alarm",
            contracts=[OrderedVisit(["locAlarm"])]
        ),
        CGTGoal(
            context=(Context(P_global(LTL("warehouse")))),
            name="always-warehouse",
            contracts=[GlobalAvoidance("locBad")]
        ),
        CGTGoal(
            context=(Context(P_global(LTL("kitchen")))),
            name="kitchen",
            contracts=[GlobalAvoidance("locSink")]
        ),
        CGTGoal(
            name="always",
            contracts=[DelayedReaction("heavy_item", "heavy_item_pickup")]
        )
    ]

    for g in list_of_goals:
        print(g)

    context_rules = {
        "mutex": [
            [LTL("home"), LTL("warehouse")],
            [LTL("home"), LTL("alarm")],
        ],
        "inclusion": [
            [LTL("kitchen"), LTL("home")],
            [LTL("alarm"), LTL("warehouse")],
        ]
    }

    """Create cgt with the goals, it will automatically compose/conjoin them based on the context"""
    cgt, context_goals = create_contextual_cgt(list_of_goals, "MINIMAL", context_rules)

    save_to_file(str(cgt), file_path + "/cgt_1_contexual_MINIMAL")

    """Create cgt with the goals, it will automatically compose/conjoin them based on the context"""
    cgt = create_contextual_cgt(list_of_goals, "MUTEX")

    save_to_file(str(cgt), file_path + "/cgt_1_contexual_MUTEX")
