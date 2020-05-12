import os
import sys

from checks.tools import Implies
from goals.helpers import extract_saturated_guarantees_from, extract_ltl_rules, extract_variables_name_from_dics, \
    generate_controller_inputs_from, generate_controller_input_text
from goals.operations import create_contextual_cgt
from helper.tools import save_to_file, traslate_boolean
from planner.planner import get_planner
from src.goals.cgtgoal import *
from src.typescogomo.assumption import *
from src.typescogomo.patterns import *
from typescogomo.formula import OrLTL, AndLTL
from typescogomo.scopes import *

file_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(os.getcwd(), os.path.pardir))

if __name__ == "__main__":
    """The designer specifies a mission using the predefined catalogue of patterns 
       In addition to the patterns to use the designer specifies also in which context each goal can be active"""

    """List of sensor propositions (uncontrollable)"""
    sns = {
        "night_time": LTL("night_time"),
        "day_time": LTL("day_time"),
        "low_battery": LTL("low_battery"),
        "entrance": LTL("entrance"),
        "shop": LTL("shop"),
        "get_med": LTL("get_med"),
        "warehouse": LTL("warehouse"),
        "human_entered": LTL("human_entered")
    }

    """List of location propositions"""
    loc = {
        "wlocA": LTL("wlocA"),
        "wlocB": LTL("wlocB"),
        "slocA": LTL("slocA"),
        "slocB": LTL("slocB"),
        "welcome": LTL("welcome"),
        "charge_station": LTL("charge_station")
    }

    """List of action propositions"""
    act = {
        "contact_station": LTL("contact_station")
    }

    """List of specifications / goals"""
    list_of_goals = [
        CGTGoal(
            context=(Context(
                P_global(
                    sns["night_time"]
                )
            )),
            name="night-time-patroling",
            contracts=[PContract([
                Patroling([
                    loc["wlocA"], loc["wlocB"], loc["slocA"], loc["slocB"]
                ])
            ])]
        ),
        CGTGoal(
            context=(Context(
                P_global(
                    sns["low_battery"]
                )
            )),
            name="charge-on-low-battery",
            contracts=[PContract([
                Visit([
                    loc["charge_station"]
                ]),
                PromptReaction(
                    trigger=sns["low_battery"],
                    reaction=act["contact_station"])
            ])]
        ),
        CGTGoal(
            context=(Context(
                AndLTL([
                    P_global(
                        sns["entrance"]
                    ),
                    P_global(
                        sns["day_time"]
                    )
                ])
            )),
            name="welcome-visitors",
            contracts=[PContract([
                PromptReaction(LTL("human_entered"), LTL("welcome")),
            ])]
        ),
        CGTGoal(
            context=(Context(
                AndLTL([
                    P_global(LTL("shop")),
                    P_global(LTL("day_time"))
                ])
            )),
            name="shop-day-visitors",
            contracts=[PContract([
                Visit([LTL("slocA")]),
                PromptReaction(
                    trigger=LTL("get_med"),
                    reaction=AndLTL([
                        Visit([LTL("wlocA")]),
                        PromptReaction(LTL("wlocA"), LTL("slocA"))
                    ])),
            ])]
        )
    ]

    context_rules = {
        "mutex": [
            [sns["shop"], sns["warehouse"]],
            [sns["day_time"], sns["night_time"]]
        ],
        "inclusion": [
            [sns["entrance"], sns["shop"]]
        ]
    }

    domain_rules = {
        "mutex": [[
            loc["wlocA"],
            loc["wlocB"],
            loc["slocA"],
            loc["slocB"],
            loc["charge_station"],
            loc["wlocA"],
            loc["slocA"]
        ]],
        "inclusion": [
        ]
    }

    for g in list_of_goals:
        print(g)

    ctx, dom, gs, unc, cont = generate_controller_inputs_from(list_of_goals, list(sns.keys()), context_rules,
                                                              domain_rules)
    save_to_file(generate_controller_input_text(ctx, dom, gs, unc, cont), file_path + "/output/controller-input")

    """Create cgt with the goals, it will automatically compose/conjoin them based on the context"""
    cgt, context_goals = create_contextual_cgt(list_of_goals, "MUTEX", context_rules)

    contexts_goals_str = ""
    for i, (ctx, ctx_goals) in enumerate(context_goals.items()):
        contexts_goals_str += "\n" + str(ctx.formula) + "\n-->\t" + str(len(ctx_goals)) + " goals: " + str(
            [c.name for c in ctx_goals]) + "\n"

        ctx, dom, gs, unc, cont = generate_controller_inputs_from(ctx_goals, list(sns.keys()), context_rules,
                                                                  domain_rules, ctx)
        save_to_file(generate_controller_input_text(ctx, dom, gs, unc, cont), file_path + "/output/controller-input_" + str(i))

    save_to_file(str(cgt), file_path + "/output/context-based-clustering", )
    save_to_file(contexts_goals_str, file_path + "/output/context-goals")

    # assumptions_guarantee_pairs = []
    #
    # for contract in cgt.contracts:
    #     assumptions_guarantee_pairs.append((str(contract.assumptions.formula), str(contract.guarantees.formula)))
    #
    # assumptions_overall = " | ".join(act for (act, g) in assumptions_guarantee_pairs)
    # guarantees_overall = " & ".join(Implies(act, g) for (act, g) in assumptions_guarantee_pairs)
    #
    # save_to_file(assumptions_overall, file_path + "/output/assumptions.txt", )
    # save_to_file(guarantees_overall, file_path + "/output/guarantees.txt", )
