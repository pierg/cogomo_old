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
            context=(Context(Always(AP("home")))),
            name="always-home",
            contracts=[OrderedVisit(["locA", "locB", "locC"])]
        ),
        CGTGoal(
            context=(Context(Always(AP("warehouse")))),
            name="always-warehouse",
            contracts=[GlobalAvoidance("locC")]
        )
    ]

    context_rules = {
        "mutex": [
            [LTL("home"), LTL("warehouse")],
            [LTL("home"), LTL("alarm")]
        ],
        "inclusion": [
            [LTL("kitchen"), LTL("home")]
        ]
    }

    """Create cgt with the goals, it will automatically compose/conjoin them based on the context"""
    cgt = create_contextual_simple_cgt(list_of_goals, context_rules)

    save_to_file(str(cgt), file_path + "/cgt_1_contexual")

