import os
import subprocess
import platform

from graphviz import Source

from helper.tools import traslate_boolean, save_to_file
from typescogomo.formula import AndLTL
from typescogomo.scopes import *
from typescogomo.variables import Boolean


def generate_buchi(formula: LTL, file_path: str):
    # if platform.system() != "Linux":
    #     print(platform.system() + " is not supported for buchi generation")
    #     return
    try:
        print(formula)
        b_formula, new_vars, old_vars = traslate_boolean(formula.formula)
        print(b_formula)
        result = subprocess.check_output(["ltl2tgba", "-B", b_formula, "-d"], encoding='UTF-8',
                                         stderr=subprocess.DEVNULL).splitlines()
        result = [x for x in result if not ('[Büchi]' in x)]
        result = "".join(result)

        dot_file_path = os.path.dirname(file_path)
        dot_file_name = os.path.splitext(file_path)[0]

        save_to_file(result, dot_file_name + ".dot")
        src = Source(result, directory=dot_file_path, filename=dot_file_name, format="eps")
        src.render(cleanup=True)
        print(dot_file_name + ".eps  ->   buchi generated")

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


def examples():
    generate_buchi(
        AndLTL([
            P_between_Q_and_R(
                q=LTL("day"),
                r=LTL("night"),
                p=LTL("entrance")
            ),
            LTL("((day & !night) | (!day & night))", Variables([Boolean("day"), Boolean("night")]))
        ]),
        "context_with_scope"
    )
    generate_buchi(
        AndLTL([
            P_global(
                p=LTL("entrance")
            ),
            P_global(
                p=LTL("day")
            ),
            LTL("((day & !night) | (!day & night))", Variables([Boolean("day"), Boolean("night")]))
        ]),
        "context_without_scope"
    )


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


if __name__ == '__main__':
    examples()
    # generate_buchi(
    #     AndLTL([
    #         P_eventually(LTL("alarm")),
    #         P_after_Q(
    #             p=P_until_R(
    #                 p=LTL("warehouse"),
    #                 r=LTL("!alarm")),
    #             q=LTL("alarm"))
    #     ]), "strong-after-alarm")
    #
    # generate_buchi(
    #     AndLTL([
    #         P_eventually(LTL("alarm")),
    #         P_until_R(
    #             p=LTL("warehouse"),
    #             r=LTL("!alarm"))
    #     ]), "strong-after-alarm2")
    #
    # generate_buchi(
    #     AndLTL([
    #         P_eventually(LTL("alarm")),
    #         P_after_Q(
    #             p=LTL("warehouse"),
    #             q=LTL("alarm"))
    #     ]), "strong-after-alarm2")

    # basic_scopes()
    # composition_scopes()
    # clean_up()
