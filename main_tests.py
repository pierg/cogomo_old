import os
import shutil
import sys

from checks.tools import Implies
from controller.parser import parse_controller
from controller.synthesis import create_controller_if_exists
from goals.helpers import extract_saturated_guarantees_from, extract_ltl_rules, extract_variables_name_from_dics, \
    generate_general_controller_from_goals, generate_controller_input_text
from goals.operations import create_contextual_clusters, create_cgt, CGTFailException, pretty_cgt_exception, \
    pretty_print_summary_clustering
from helper.tools import save_to_file, traslate_boolean
from src.goals.cgtgoal import *
from src.typescogomo.assumption import *
from src.typescogomo.patterns import *
from typescogomo.formula import OrLTL, AndLTL
from typescogomo.scopes import *

file_path = os.path.dirname(os.path.abspath(__file__)) + "/output/clustering"
try:
    shutil.rmtree(file_path)
except:
    pass

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

    list_of_goals_with_integers = [
        CGTGoal(
            name="always-avoid-humans",
            contracts=[PContract([
                GlobalAvoidance(LTL("human"))
            ])]
        ),
        CGTGoal(
            context=(Context(
                OrLTL([
                    AndLTL([
                        P_global(LTL("time > 20")),
                        P_global(LTL("time < 24")),
                    ]),
                    AndLTL([
                        P_global(LTL("time > 0")),
                        P_global(LTL("time < 8")),
                    ])
                ])
            )),
            name="night-time-patroling",
            contracts=[PContract([
                Patroling([LTL("wlocA"), LTL("wlocB"), LTL("slocA"), LTL("slocB")])
            ])]
        ),
        CGTGoal(
            context=(Context(P_global(LTL("battery < 20")))),
            name="charge-on-low-battery",
            contracts=[PContract([
                Visit([LTL("charge_station")]),
                PromptReaction(LTL("low_battery"), LTL("contact_station"))
            ])]
        ),
        CGTGoal(
            context=(Context(
                AndLTL([
                    P_global(LTL("entrance")),
                    P_global(LTL("time > 9")),
                    P_global(LTL("time < 17")),
                ])
            )),
            name="welcome-visitors",
            contracts=[PContract([
                Visit([LTL("slocA")]),
                PromptReaction(LTL("get_med"), LTL("wlocA")),
                PromptReaction(LTL("wlocA"), LTL("slocA"))
            ])]
        ),
        CGTGoal(
            context=(Context(
                AndLTL([
                    P_global(LTL("shop")),
                    P_global(LTL("time > 9")),
                    P_global(LTL("time < 17"))
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
        ],
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

    ctx, dom, gs, unc, cont = generate_general_controller_from_goals(list_of_goals, list(sns.keys()), context_rules,
                                                                     domain_rules)

    controller_file_name = file_path + "/controller-general.txt"

    save_to_file(generate_controller_input_text(ctx, dom, gs, unc, cont), controller_file_name)

    create_controller_if_exists(controller_file_name)

    """Create cgt with the goals, it will automatically compose/conjoin them based on the context"""
    context_goals = create_contextual_clusters(list_of_goals, "MUTEX", context_rules)

    save_to_file(pretty_print_summary_clustering(context_goals), file_path + "/context-goals.txt")

    for ctx, goals in context_goals.items():
        from helper.buchi import generate_buchi

        g_name = "||".join(g.name for g in goals)
        generate_buchi(ctx, file_path + "/buchi/" + g_name)

    for i, (ctx, ctx_goals) in enumerate(context_goals.items()):
        controller_file_name = file_path + "/controller-context_" + str(i) + ".txt"

        ctx, dom, gs, unc, cont = generate_general_controller_from_goals(ctx_goals, list(sns.keys()), context_rules,
                                                                         domain_rules, ctx)
        save_to_file(generate_controller_input_text(ctx, dom, gs, unc, cont), controller_file_name)

        create_controller_if_exists(controller_file_name)

    try:
        cgt = create_cgt(context_goals)
    except CGTFailException as e:
        print(pretty_cgt_exception(e))
        sys.exit()

    save_to_file(str(cgt), file_path + "/context-based-cgt.txt")
