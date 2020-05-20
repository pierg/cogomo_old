from src.goals.cgtgoal import *
from src.typescogomo.assumption import *
from src.typescogomo.patterns import *
from typescogomo.formula import OrLTL, AndLTL, NotLTL
from typescogomo.scopes import *


def get_inputs():
    """The designer specifies a mission using the predefined catalogue of patterns
       In addition to the patterns to use the designer specifies also in which context each goal can be active"""

    print("~~USING CUSTOM FILE~~")

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
        "charging_point": LTL("charging_point")
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
            [ap["s"]["shop"], ap["s"]["warehouse"]],
            [ap["s"]["day_time"], ap["s"]["night_time"]]
        ],
        "inclusion": [
            [ap["s"]["entrance"], ap["s"]["shop"]],
            [ap["s"]["human_entered"], ap["s"]["shop"]],
            [ap["s"]["get_med"], ap["s"]["entrance"]],

        ],
        "dependent": [
            [ap["s"]["low_battery"]]
        ]
    }
    """TODO: dependent is not used at the moment"""

    """Domain rules, e.g. different locations"""
    domain_rules = {
        "mutex": [[
            ap["l"]["wlocA"],
            ap["l"]["wlocB"],
            ap["l"]["slocA"],
            ap["l"]["slocB"],
            ap["l"]["safe_loc"],
            ap["l"]["charging_point"]
        ]],
        "inclusion": [
        ]
    }

    liveness_rules = {
        ap["s"]["alarm"],
        NotLTL(ap["s"]["alarm"])
    }

    """List of specifications / goals"""
    list_of_goals = [
        CGTGoal(
            name="go-to-safe-zone-during-alarm",
            description="if the alarm goes off during the night go to safety location and stay there until there is no more alarm",
            context=(Context(
                AndLTL([
                    P_global(ap["s"]["night_time"])
                ])
            )),
            contracts=[PContract([
                P_after_Q(
                    p=P_until_R(
                        p=Visit([ap["l"]["safe_loc"]]),
                        r=ap["s"]["human_entered"]),
                    q=ap["s"]["alarm"])
            ])]
        ),
        CGTGoal(
            name="go-to-safe-zone-during-alarm2",
            description="if the alarm goes off during the night go to safety location and stay there until there is no more alarm",
            context=(Context(
                AndLTL([
                    P_global(ap["s"]["night_time"])
                ])
            )),
            contracts=[PContract([
                PromptReaction(
                    trigger=ap["s"]["alarm"],
                    reaction=P_until_R(
                        p=Visit([ap["l"]["safe_loc"]]),
                        r=ap["s"]["human_entered"])
                )
            ])]
        ),
        CGTGoal(
            name="go-to-safe-until-not-alarm",
            description="if the alarm goes off during the night go to safety location and stay there until there is no more alarm",
            context=(Context(
                AndLTL([
                    P_global(ap["s"]["night_time"])
                ])
            )),
            contracts=[PContract([
                P_after_Q(
                    p=P_until_R(
                        p=Visit([ap["l"]["safe_loc"]]),
                        r=NotLTL(ap["s"]["alarm"])),
                    q=ap["s"]["alarm"])
            ])]
        )
    ]

    return sns, loc, act, context_rules, domain_rules, liveness_rules, list_of_goals
