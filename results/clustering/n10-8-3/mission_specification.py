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
            "full_battery": LTL("full_battery"),
            "entrance": LTL("entrance"),
            "shop": LTL("shop"),
            "get_med": LTL("get_med"),
            "warehouse": LTL("warehouse"),
            "human_entered": LTL("human_entered"),
            "guard_entered": LTL("guard_entered"),
            "door_alarm": LTL("door_alarm"),
            "fire_alarm": LTL("fire_alarm")
        },
        "l": {
            "go_entrace": LTL("go_entrace"),
            "go_counter": LTL("go_counter"),
            "go_back": LTL("go_back"),
            "go_warehouse": LTL("go_warehouse"),
            "go_charging_point": LTL("go_charging_point"),
            "go_safe_loc": LTL("go_safe_loc")
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
                [ap["s"]["fire_alarm"], ap["s"]["warehouse"]],
                [ap["s"]["door_alarm"], ap["s"]["shop"]],
                [ap["s"]["guard_entered"], ap["s"]["shop"]],
            ]
        },
        "domain": {
            "mutex": [[
                ap["l"]["go_entrace"],
                ap["l"]["go_counter"],
                ap["l"]["go_back"],
                ap["l"]["go_warehouse"],
                ap["l"]["go_charging_point"],
                ap["l"]["go_safe_loc"]
            ]],
            "inclusion": [
            ]
        },
        "environment": {
            "mutex": [
                [ap["s"]["full_battery"], ap["s"]["low_battery"]]
            ],
            "inclusion": [
                [ap["s"]["fire_alarm"], ap["s"]["full_battery"]],
                [ap["s"]["fire_alarm"], NotLTL(ap["s"]["low_battery"])]
            ],
            "liveness": [
                ap["s"]["full_battery"],
                ap["s"]["low_battery"],
                NotLTL(ap["s"]["fire_alarm"])
            ]
        }
    }

    """List of specifications / goals"""
    list_of_goals = [
        CGTGoal(
            name="night-time-patroling",
            description="patrol warehouse and shop during the night",
            context=(Context(
                    ap["s"]["night_time"]
            )),
            contracts=[PContract([
                Patroling([
                    ap["l"]["go_entrace"], ap["l"]["go_counter"], ap["l"]["go_back"], ap["l"]["go_warehouse"]
                ])
            ])]
        ),
        CGTGoal(
            name="get-meds-to-clients",
            description="if a clients request a medicine go to the warehouse, take the medicine and come back",
            context=(Context(
                AndLTL([
                    ap["s"]["shop"],
                    ap["s"]["day_time"]
                ])
            )),
            contracts=[PContract([
                DelayedReaction(
                    trigger=ap["s"]["get_med"],
                    reaction=AndLTL([
                        Visit([ap["l"]["go_back"], ap["l"]["go_warehouse"], ap["l"]["go_entrace"]]),
                        InstantReaction(
                            trigger=ap["l"]["go_warehouse"],
                            reaction=ap["a"]["take_med"]
                        ),
                        InstantReaction(
                            trigger=ap["l"]["go_entrace"],
                            reaction=ap["a"]["give_med"]
                        )
                    ])
                )
            ])]
        ),
        CGTGoal(
            name="low-battery",
            description="always go the charging point and contact the main station when the battery is low",
            contracts=[PContract([
                P_between_Q_and_R(
                    q=ap["s"]["low_battery"],
                    p=ap["l"]["go_charging_point"],
                    r=ap["s"]["full_battery"]
                )
            ])]
        ),
        CGTGoal(
            name="welcome-visitors",
            description="welcome people at the entrance",
            context=(Context(
                AndLTL([
                    ap["s"]["day_time"],
                    ap["s"]["entrance"]
                ])
            )),
            contracts=[PContract([
                DelayedReaction(
                    trigger=ap["s"]["human_entered"],
                    reaction=ap["a"]["welcome_client"]),
            ])]
        ),
        # CGTGoal(
        #     name="door-alarm",
        #     description="if the door_alarm goes off at any time go to safety "
        #                 "location and stay there until there is no more door_alarm",
        #     context=(Context(
        #         AndLTL([
        #             ap["s"]["door_alarm"]
        #         ])
        #     )),
        #     contracts=[PContract([
        #         P_until_R(
        #             p=ap["l"]["go_warehouse"],
        #             r=ap["s"]["guard_entered"]
        #         )
        #     ])]
        # ),
        CGTGoal(
            name="fire-alarm",
            description="if the door_alarm goes off at any time go to safety "
                        "location and stay there until there is no more door_alarm",
            contracts=[PContract([
                InstantReaction(
                    trigger=ap["s"]["fire_alarm"],
                    reaction=ap["l"]["go_safe_loc"]
                )
            ])]
        )
    ]

    return ap, rules, list_of_goals
