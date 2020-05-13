import subprocess
from typing import Tuple, List, Union
from checks.tools import And, Not, Implies


def get_controller(assumptions: str, guarantees: str, ins: str, outs: str) -> str:
    try:
        params = ' -f "' + Implies(assumptions, guarantees) + '" --ins="' + ins + '" --outs="' + outs + '"'
        print(params)
        output = subprocess.check_output(['strix', params], encoding='UTF-8', stderr=subprocess.DEVNULL)
    except Exception as e:
        raise e
    print("\n\nOUTPUT\n\n" + output)
    return output
