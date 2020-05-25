import os

from src.goals.cgtgoal import *
from src.typescogomo.assumption import *
from src.typescogomo.patterns import *
from typescogomo.formula import OrLTL, AndLTL, NotLTL
from typescogomo.scopes import *


def get_inputs():
    """The designer specifies a mission using the predefined catalogue of patterns
       In addition to the patterns to use the designer specifies also in which context each goal can be active"""

    print("CUSTOM SPEC c2:")
    print(os.path.dirname(os.path.abspath(__file__)))

    """ Atomic propositions divided in
            s - sensor propositions (uncontrollable)
            l - location propositions (controllable e.g. goto)
            a - action propositions (controllable)"""
    ap = {
        "s": {
            "night_time": LTL("night_time"),
            "day_time": LTL("day_time"),
            "low_battery": LTL("low_battery"),
            "entrance": LTL("entrance"),
            "shop": LTL("shop"),
            "get_med": LTL("get_med"),
            "warehouse": LTL("warehouse"),
            "human_entered": LTL("human_entered"),
            "alarm": LTL("alarm")
        },
        "l": {
            "wlocA": LTL("wlocA"),
            "wlocB": LTL("wlocB"),
            "slocA": LTL("slocA"),
            "slocB": LTL("slocB"),
            "safe_loc": LTL("safe_loc"),
            "charging_point": LTL("charging_point")
        },
        "a": {
            "contact_station": LTL("contact_station"),
            "welcome_client": LTL("welcome_client"),
            "take_med": LTL("take_med")
        }
    }

    """ Contexts rules, e.g. shop xor warehouse etc..
        Domain rules, e.g. different locations
        Liveness rules, i.e. assumptions when generating the controller e.g. GF alarm, GF !alarm"""
    rules = {
        "context": {
            "mutex": [
                [ap["s"]["shop"], ap["s"]["warehouse"]],
                [ap["s"]["day_time"], ap["s"]["night_time"]]
            ],
            "inclusion": [
                [ap["s"]["entrance"], ap["s"]["shop"]],
                [ap["s"]["human_entered"], ap["s"]["shop"]],
                [ap["s"]["get_med"], ap["s"]["entrance"]],

            ]
        },
        "domain": {
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
        },
        "environment": {
            "liveness": [
                ap["s"]["alarm"],
                NotLTL(ap["s"]["alarm"])
            ]
        }
    }

    """List of specifications / goals"""
    list_of_goals = [
        CGTGoal(
            name="night-time-patroling",
            description="patrol warehouse and shop during the night",
            context=(Context(
                P_global(
                    ap["s"]["night_time"]
                )
            )),
            contracts=[PContract([
                Patroling([
                    ap["l"]["wlocA"], ap["l"]["wlocB"], ap["l"]["slocA"], ap["l"]["slocB"]
                ])
            ])]
        ),
        CGTGoal(
            name="get-meds-to-clients",
            description="if a clients request a medicine go to the warehouse, take the medicine and come back",
            context=(Context(
                AndLTL([
                    P_global(ap["s"]["shop"]),
                    P_global(ap["s"]["day_time"])
                ])
            )),
            contracts=[PContract([
                Visit([ap["l"]["slocA"]]),
                DelayedReaction(
                    trigger=ap["s"]["get_med"],
                    reaction=AndLTL([
                        OrderedVisit([ap["l"]["wlocA"], ap["l"]["slocA"]]),
                        BoundDelay(
                            trigger=ap["l"]["wlocA"],
                            reaction=ap["a"]["take_med"]
                        ),
                        PromptReaction(
                            trigger=ap["a"]["take_med"],
                            reaction=ap["l"]["slocA"]
                        )]
                    ))
            ])]
        ),
        CGTGoal(
            name="always-charge-on-low-battery",
            description="always go the charging point and contact the main station when the battery is low",
            contracts=[PContract([
                P_after_Q(
                    q=ap["s"]["low_battery"],
                    p=AndLTL([
                        Visit([
                            ap["l"]["charging_point"]
                        ]),
                        ap["a"]["contact_station"]
                    ])
                )
            ])]
        ),
        CGTGoal(
            name="welcome-visitors",
            description="welcome people at the entrance",
            context=(Context(
                AndLTL([
                    P_global(ap["s"]["day_time"]),
                    P_global(ap["s"]["entrance"])
                ])
            )),
            contracts=[PContract([
                PromptReaction(
                    trigger=ap["s"]["human_entered"],
                    reaction=ap["a"]["welcome_client"]),
            ])]
        ),
        CGTGoal(
            name="go-to-safe-zone-during-alarm",
            description="if the alarm goes off at any time go to safety location and stay there until there is no more alarm",
            contracts=[PContract([
                P_after_Q(
                    p=P_until_R(
                        p=ap["l"]["safe_loc"],
                        r=NotLTL(ap["s"]["alarm"])),
                    q=ap["s"]["alarm"])
            ])]
        )
    ]

    return ap, rules, list_of_goals
