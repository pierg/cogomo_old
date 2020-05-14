from src.goals.cgtgoal import *
from src.typescogomo.assumption import *
from src.typescogomo.patterns import *
from typescogomo.formula import OrLTL, AndLTL
from typescogomo.scopes import *


def get_inputs():
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

    context_rules = {
        "mutex": [
            [sns["shop"], sns["warehouse"]],
            [sns["day_time"], sns["night_time"]]
        ],
        "inclusion": [
            [sns["entrance"], sns["shop"]]
        ],
        "dependent": [
            [sns["low_battery"]]
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

    return sns, loc, act, context_rules, domain_rules, list_of_goals
