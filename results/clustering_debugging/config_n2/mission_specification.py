from src.goals.cgtgoal import *
from src.typescogomo.assumption import *
from src.typescogomo.patterns import *
from typescogomo.formula import OrLTL, AndLTL, NotLTL
from typescogomo.scopes import *


def get_inputs():
    """The designer specifies a mission using the predefined catalogue of patterns
       In addition to the patterns to use the designer specifies also in which context each goal can be active"""
    print("~~~~USING CUSTOM FILE~~~~")
    """List of sensor propositions (uncontrollable)"""
    sns = {
        "night_time": LTL("night_time"),
        "day_time": LTL("day_time"),
        "low_battery": LTL("low_battery"),
        "entrance": LTL("entrance"),
        "shop": LTL("shop"),
        "get_med": LTL("get_med"),
        "warehouse": LTL("warehouse"),
        "human_entered": LTL("human_entered"),
        "alarm": LTL("alarm")
    }

    """List of location propositions (controllable e.g. goto)"""
    loc = {
        "wlocA": LTL("wlocA"),
        "wlocB": LTL("wlocB"),
        "slocA": LTL("slocA"),
        "slocB": LTL("slocB"),
        "safe_loc": LTL("safe_loc"),
        "charge_station": LTL("charge_station")
    }

    """List of action propositions (controllable)"""
    act = {
        "contact_station": LTL("contact_station"),
        "welcome_client": LTL("welcome_client"),
        "take_med": LTL("take_med")
    }

    """Contexts rules, e.g. shop xor warehouse etc.."""
    context_rules = {
        "mutex": [
            [sns["shop"], sns["warehouse"]],
            [sns["day_time"], sns["night_time"]]
        ],
        "inclusion": [
            [sns["entrance"], sns["shop"]],
            [sns["get_med"], sns["shop"]],
            [sns["human_entered"], sns["shop"]]
        ],
        "dependent": [
            [sns["low_battery"]]
        ]
    }
    """TODO: dependent is not used at the moment"""

    """Domain rules, e.g. different locations"""
    domain_rules = {
        "mutex": [[
            loc["wlocA"],
            loc["wlocB"],
            loc["slocA"],
            loc["slocB"],
            loc["safe_loc"],
            loc["charge_station"]
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
                PromptReaction(
                    trigger=sns["human_entered"],
                    reaction=act["welcome_client"]),
            ])]
        ),
        CGTGoal(
            context=(Context(
                AndLTL([
                    P_global(sns["shop"]),
                    P_global(sns["day_time"])
                ])
            )),
            name="shop-day-visitors",
            contracts=[PContract([
                Visit([loc["slocA"]]),
                PromptReaction(
                    trigger=sns["get_med"],
                    reaction=AndLTL([
                        OrderedVisit([loc["wlocA"], loc["slocA"]]),
                        PromptReaction(
                            trigger=sns["wlocA"],
                            reaction=act["take_med"]
                        )]
                ))
            ])]
        ),
        CGTGoal(
            context=(Context(
                AndLTL([
                    P_global(sns["night_time"])
                ])
            )),
            name="go-to-safe-zone-during-alarm",
            contracts=[PContract([
                P_after_Q(
                    p=P_until_R(
                        p=Visit([loc["safe_loc"]]),
                        r=NotLTL(sns["alarm"])),
                    q=sns["alarm"])
            ])]
        )
    ]

    return sns, loc, act, context_rules, domain_rules, list_of_goals
