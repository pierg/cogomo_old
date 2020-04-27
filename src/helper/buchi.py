import os
import subprocess
from graphviz import Source
from src.typescogomo.contexts import *


def clean_up():
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    ouput_dir = os.path.join(curr_dir, "output")
    items = os.listdir(ouput_dir)
    for item in items:
        if not item.endswith(".eps"):
            os.remove(os.path.join(ouput_dir, item))


def generate_buchi(formula: LTL, name: str, path: str = ""):
    try:
        print(formula)
        output = subprocess.check_output(["ltl2tgba", "-B", str(formula), "-d"], encoding='UTF-8',
                                         stderr=subprocess.DEVNULL).splitlines()
        output = [x for x in output if not ('[Büchi]' in x)]

        output = "".join(output)

        src = Source(output, directory="output", filename=name, format="eps")

        src.render()

    except Exception as e:
        raise e


def basic_scopes():
    # Dwyer
    generate_buchi(P_global(p=LTL("p")), "P_global")
    generate_buchi(P_before_R(p=LTL("p"), r=LTL("r")), "P_before_R")
    generate_buchi(P_after_Q(p=LTL("p"), q=LTL("q")), "P_after_Q")
    generate_buchi(P_between_Q_and_R(p=LTL("p"), q=LTL("q"), r=LTL("r")), "P_between_Q_and_R")
    generate_buchi(P_after_Q_until_R(p=LTL("p"), q=LTL("q"), r=LTL("r")), "P_after_Q_until_R")

    # Other
    generate_buchi(P_until_R(p=LTL("p"), r=LTL("r")), "P_until_R")
    generate_buchi(P_weakuntil_R(p=LTL("p"), r=LTL("r")), "P_weakuntil_R")
    generate_buchi(P_release_R(p=LTL("p"), r=LTL("r")), "P_release_R")
    generate_buchi(P_strongrelease_R(p=LTL("p"), r=LTL("r")), "P_strongrelease_R")


def composition_scopes():
    generate_buchi(P_after_Q(P_release_R(LTL("!alarm"), LTL("warehouse")), LTL("alarm")), "after-alarm-release")

    generate_buchi(P_after_Q(P_until_R(P_release_R(LTL("!alarm"), LTL("warehouse")), LTL("!alarm")), LTL("alarm")),
                   "release-alarm-until-not-alarm")

    generate_buchi(P_after_Q(P_until_R(LTL("warehouse"), LTL("!alarm")), LTL("alarm")),
                   "after-alarm-warehouse-until-not-alarm")

    generate_buchi(P_after_Q_until_R(LTL("warehouse"), LTL("alarm"), LTL("!alarm")),
                   "after-alarm-until-not-alarm-previous")

    generate_buchi(P_between_Q_and_R(LTL("warehouse"), LTL("alarm"), LTL("!alarm")), "between-alarm-not-alarm-previous")

    generate_buchi(P_strongrelease_R(LTL("alarm"), P_until_R(LTL("warehouse"), LTL("!alarm"))),
                   "strong-release-alarm-warehouse-until-not-alarm")

    generate_buchi(P_release_R(LTL("alarm"), P_until_R(LTL("warehouse"), LTL("!alarm"))),
                   "release-alarm-warehouse-until-not-alarm")

    generate_buchi(P_after_Q(P_until_R(LTL("warehouse"), LTL("!alarm")), LTL("warehouse & alarm")),
                   "after-alarm-global-warehouse-until-not-alarm")

    generate_buchi(P_after_Q(P_until_R(LTL("warehouse & alarm"), LTL("warehouse & !alarm")), LTL("warehouse & alarm")),
                   "after-alarm-global-warehouse-until-not-alarmAND")

    generate_buchi(P_after_Q(LTL("warehouse & alarm"), P_until_R(LTL("warehouse"), LTL("warehouse & !alarm"))),
                   "after-warehouseandalarm-until-not-alarm")

    generate_buchi(
        P_after_Q(
            p=P_until_R(
                p=LTL("warehouse & alarm"),
                r=LTL("warehouse & !alarm")),
            q=LTL("warehouse & alarm"))
        , "after-alarm-global-warehouse-until-not-alarmAND")

    generate_buchi(
        P_after_Q(
            p=P_until_R(
                p=LTL("warehouse"),
                r=LTL("!alarm")),
            q=LTL("alarm")
        ), "after_until_alarm_compost")

    generate_buchi(
        P_strongrelease_R(
            p=P_until_R(
                p=LTL("warehouse"),
                r=LTL("!alarm")),
            r=LTL("warehouse & alarm")
        ), "case_release2")

    generate_buchi(
        P_after_Q(
            p=P_weakuntil_R(
                p=LTL("warehouse"),
                r=LTL("!alarm")),
            q=LTL("alarm")
        ), "after_weak_until_alarm_compost")

    generate_buchi(
        P_after_Q_until_R(
            p=LTL("warehouse"),
            q=LTL("alarm"),
            r=LTL("!alarm")
        ), "case_after_until_alarm")

    generate_buchi(
        P_between_Q_and_R(
            p=LTL("warehouse"),
            q=LTL("alarm"),
            r=LTL("!alarm")
        ), "case_between_alarm")

    generate_buchi(
        P_strongrelease_R(
            p=P_until_R(
                p=LTL("warehouse"),
                r=LTL("!alarm")),
            r=LTL("alarm")
        ), "robot-release-strong")

    generate_buchi(
        P_release_R(
            p=P_until_R(
                p=LTL("warehouse"),
                r=LTL("!alarm")),
            r=LTL("alarm")
        ), "robot-release")

    generate_buchi(
        P_strongrelease_R(
            r=P_until_R(
                p=LTL("warehouse"),
                r=LTL("!alarm")),
            p=LTL("alarm")
        ), "robot-release-strong2")

    generate_buchi(
        P_release_R(
            r=P_until_R(
                p=LTL("warehouse"),
                r=LTL("!alarm")),
            p=LTL("alarm")
        ), "robot-release2")

    generate_buchi(
        P_global(
            p=P_until_R(
                p=P_until_R(
                    p=LTL("warehouse"),
                    r=LTL("alarm")),
                r=LTL("!alarm"))
        ), "robot-global")

    generate_buchi(
        P_release_R(
            p=LTL("warehouse"),
            r=LTL("alarm")
        ), "robot-release2-alarm")

    generate_buchi(
        P_release_R(
            r=LTL("warehouse"),
            p=LTL("alarm")
        ), "robot-release-alarm")

    generate_buchi(
        P_after_Q(
            q=P_release_R(
                r=LTL("warehouse"),
                p=LTL("alarm")
            ),
            p=P_until_R(
                p=LTL("warehouse"),
                r=LTL("!alarm")
            )
        ), "robot-release-alarm-after-composot")

    clean_up()


if __name__ == '__main__':
    basic_scopes()
    composition_scopes()
    clean_up()
