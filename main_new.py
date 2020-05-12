import os
import sys

from checks.tools import Implies
from goals.helpers import extract_saturated_guarantees_from
from goals.operations import create_contextual_cgt
from helper.tools import save_to_file, traslate_boolean
from planner.planner import get_planner
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
            context=(Context(
                AndScopes([
                    P_global(LTL("warehouse")),
                    OrScopes([
                        AndScopes([
                            P_global(LTL("time > 20")),
                            P_global(LTL("time < 24")),
                        ]),
                        AndScopes([
                            P_global(LTL("time > 0")),
                            P_global(LTL("time < 8")),
                        ])
                    ])
                ])
            )),
            name="night-time",
            contracts=[OrderedVisit(["locA", "locB", "locC"])]
        ),
        CGTGoal(
            context=(Context(P_global(LTL("warehouse")))),
            name="always-warehouse",
            contracts=[OrderedVisit(["locA", "locB", "locC"])]
        ),
        CGTGoal(
            context=(Context(
                AndScopes([
                    P_global(LTL("shop")),
                    P_global(LTL("time > 9")),
                    P_global(LTL("time < 17")),
                ])
            )),
            name="always-shop-working-hours",
            contracts=[OrderedVisit(["locA", "locB", "locC"])]
        ),
        CGTGoal(
            context=(Context(P_global(LTL("shop")))),
            name="always-shop",
            contracts=[OrderedVisit(["locA", "locB", "locC"])]
        ),
        CGTGoal(
            context=(Context(P_global(LTL("alarm")))),
            name="always-alarm",
            contracts=[OrderedVisit(["locA", "locB", "locC"])]
        ),
        CGTGoal(
            context=(Context(
                AndScopes([
                    P_eventually(LTL("alarm")),
                    P_after_Q(
                        p=P_until_R(
                            p=LTL("warehouse"),
                            r=LTL("!alarm")),
                        q=LTL("alarm"))
                ])
            )),
            name="after-alarm-warehouse-until",
            contracts=[OrderedVisit(["locA", "locB", "locC"])]
        )
    ]

    context_rules = {
        "mutex": [
            [LTL("home"), LTL("warehouse")]
        ],
        "inclusion": [
            [LTL("kitchen"), LTL("home")]
        ],
        "bounds": [
            ("time", "0..24")
        ]
    }

    assumptions, guarantees, variables = extract_saturated_guarantees_from(list_of_goals)

    with open(file_path + "/output/controller_inputs.txt", 'w') as f:
        f.write("\nASSUMPTIONS:\n\n")
        for a in assumptions:
            f.write(a + "\n")
        f.write("\n\n\nGUARANTEES:\n\n")
        for g in guarantees:
            f.write(g + "\n")
        f.write("\n\n\nOUTPUTS:\n\n")
        f.write(", ".join(variables))

    f.close()

    """Create cgt with the goals, it will automatically compose/conjoin them based on the context"""
    cgt, context_goals = create_contextual_cgt(list_of_goals, "MUTEX", context_rules)

    contexts_goals_str = ""
    for ctx, ctx_goals in context_goals.items():
        contexts_goals_str += "\n" + str(ctx.formula) + "\n-->\t" + str(len(ctx_goals)) + " goals: " + str(
            [c.name for c in ctx_goals]) + "\n"

    save_to_file(str(cgt), file_path + "/output/context-based-clustering", )
    save_to_file(contexts_goals_str, file_path + "/output/context-goals")

    assumptions_guarantee_pairs = []

    for contract in cgt.contracts:
        assumptions_guarantee_pairs.append((str(contract.assumptions.formula), str(contract.guarantees.formula)))

    assumptions_overall = " | ".join(a for (a, g) in assumptions_guarantee_pairs)
    guarantees_overall = " & ".join(Implies(a, g) for (a, g) in assumptions_guarantee_pairs)

    save_to_file(assumptions_overall, file_path + "/output/assumptions.txt", )
    save_to_file(guarantees_overall, file_path + "/output/guarantees.txt", )
