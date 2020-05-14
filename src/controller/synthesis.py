import os
import subprocess
import sys
from typing import Tuple, List, Union
from checks.tools import And, Not, Implies
from controller.parser import parse_controller

strix_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'bin', 'ubuntu_19.10', 'strix'))

output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'output', 'clustering'))


def is_realizable(assumptions: str, guarantees: str, ins: str, outs: str) -> bool:
    try:
        params = ' --realizability -f "' + Implies(assumptions,
                                                   guarantees) + '" --ins="' + ins + '" --outs="' + outs + '"'
        command = strix_path + params
        print("\n\nRUNNING COMMAND:\n\n" + command + "\n\n")
        stdoutdata = subprocess.getoutput(command).splitlines()
        if stdoutdata[0] == "REALIZABLE":
            return True
        if stdoutdata[0] == "UNREALIZABLE":
            return False
        else:
            raise Exception("Unknown strix response: " + stdoutdata[0])
    except Exception as e:
        raise e


def get_controller(assumptions: str, guarantees: str, ins: str, outs: str) -> str:
    try:
        params = ' --dot -f "' + Implies(assumptions, guarantees) + '" --ins="' + ins + '" --outs="' + outs + '"'
        command = strix_path + params
        print("\n\nRUNNING COMMAND:\n\n" + command + "\n\n")
        stdoutdata = subprocess.getoutput(command)
        return stdoutdata
    except Exception as e:
        raise e


if __name__ == '__main__':
    controller_file = sys.argv[1]
    file_path = output_path + "/" + sys.argv[1]
    a, g, i, o = parse_controller(file_path)
    controller_output = get_controller(a, g, i, o)
    print("\n\nCONTROLLER_RESPONSE:\n\n" + controller_output)
