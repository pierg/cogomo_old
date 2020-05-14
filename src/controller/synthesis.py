import os
import subprocess
import sys
from typing import Tuple, List, Union
from checks.tools import And, Not, Implies
from controller.parser import parse_controller

strix_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'bin', 'ubuntu_19.10', 'strix'))

output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'output', 'clustering'))


def get_controller(assumptions: str, guarantees: str, ins: str, outs: str) -> str:
    try:
        params = ' -f "' + Implies(assumptions, guarantees) + '" --ins="' + ins + '" --outs="' + outs + '"'
        print("\n\n" + params + "\n\n")
        output = subprocess.check_output([strix_path, params], encoding='UTF-8', stderr=subprocess.DEVNULL)
        print("\n\nOUTPUT\n\n" + output)
        return output
    except Exception as e:
        raise e


if __name__ == '__main__':
    controller_file = sys.argv[1]
    file_path = output_path + "/" + sys.argv[1]
    a, g, i, o = parse_controller(file_path)
    controller_output = get_controller(a, g, i, o)
    print(controller_output)