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
            "take_med": LTL("take_med"),
            "give_med": LTL("give_med")
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
                StrictOrderPatroling([
                    ap["l"]["wlocA"], ap["l"]["wlocB"], ap["l"]["slocA"], ap["l"]["slocB"]
                ])
            ])]
        ),
        CGTGoal(
            name="order-visit",
            description="patrol warehouse and shop during the night",
            context=(Context(
                P_global(
                    ap["s"]["shop"]
                )
            )),
            contracts=[PContract([
                StrictOrderVisit([
                    ap["l"]["wlocB"], ap["l"]["wlocA"], ap["l"]["slocB"], ap["l"]["slocA"]
                ])
            ])]
        ),
    ]

    return ap, rules, list_of_goals
