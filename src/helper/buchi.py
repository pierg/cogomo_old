import subprocess
from graphviz import Source
from src.typescogomo.contexts import *


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


if __name__ == '__main__':
    formula = "GFa & GFb"
    generate_buchi(BeforeR(LTL("p"), LTL("r")), "before-r")
    generate_buchi(AfterQ(LTL("p"), LTL("q")), "after-q")

    generate_buchi(BetweenQandR(LTL("p"), LTL("q"), LTL("r")), "between-q-and-r")
    generate_buchi(AfterQuntilR(LTL("p"), LTL("q"), LTL("r")), "after-q-until-r")

    generate_buchi(UntilR(LTL("p"), LTL("r")), "until-r")
    generate_buchi(WeakUntilR(LTL("p"), LTL("r")), "weak-until-r")
    generate_buchi(ReleaseR(LTL("r"), LTL("p")), "release-r")
    generate_buchi(StrongReleaseR(LTL("r"), LTL("p")), "strong-release-r")

    generate_buchi(AfterQ(ReleaseR(LTL("!alarm"), LTL("warehouse")), LTL("alarm")), "after-alarm-release")

    generate_buchi(AfterQ(UntilR(ReleaseR(LTL("!alarm"), LTL("warehouse")), LTL("!alarm")), LTL("alarm")),
                   "release-alarm-until-not-alarm")

    generate_buchi(AfterQ(UntilR(LTL("warehouse"), LTL("!alarm")), LTL("alarm")),
                   "after-alarm-warehouse-until-not-alarm")

    generate_buchi(AfterQuntilR(LTL("warehouse"), LTL("alarm"), LTL("!alarm")), "after-alarm-until-not-alarm-previous")

    generate_buchi(BetweenQandR(LTL("warehouse"), LTL("alarm"), LTL("!alarm")), "between-alarm-not-alarm-previous")

    generate_buchi(StrongReleaseR(LTL("alarm"), UntilR(LTL("warehouse"), LTL("!alarm"))),
                   "strong-release-alarm-warehouse-until-not-alarm")

    generate_buchi(ReleaseR(LTL("alarm"), UntilR(LTL("warehouse"), LTL("!alarm"))),
                   "release-alarm-warehouse-until-not-alarm")

    generate_buchi(AfterQ(UntilR(LTL("G (warehouse)"), LTL("!alarm")), LTL("warehouse & alarm")),
                       "after-alarm-global-warehouse-until-not-alarm")

    generate_buchi(AfterQ(UntilR(LTL("G (warehouse)"), LTL("!alarm")), LTL("warehouse & alarm")),
                       "after-alarm-global-warehouse-until-not-alarm")

