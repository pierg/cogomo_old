import os
import subprocess
import sys
import platform
import time
from typing import Tuple


from graphviz import Source

from checks.nusmv import check_satisfiability
from checks.tools import Implies
from controller.parser import parse_controller
from helper.tools import save_to_file

strix_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'bin', 'ubuntu_19_10', 'strix'))

output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'output', 'clustering'))


class SynthesisException(Exception):
    def __init__(self, reason: "str"):

        self.os_not_supported = False
        self.trivial = True

        if reason == "os_not_supported":
            self.os_not_supported = True
        elif reason == "trivial":
            self.trivial = True
        else:
            raise Exception("Unknown exeption: " + reason)


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


def get_controller(assumptions: str, guarantees: str, ins: str, outs: str) -> Tuple[str, float]:
    try:
        print("Formatting TRUE as true for strix")
        assumptions = assumptions.replace("TRUE", "true")
        guarantees = guarantees.replace("TRUE", "true")
        params = ' -k --dot -f "' + Implies(assumptions, guarantees) + '" --ins="' + ins + '" --outs="' + outs + '"'
        command = strix_path + params
        print("\n\nRUNNING COMMAND:\n\n" + command + "\n\n")
        start_time = time.time()
        result = []
        try:
            # result = subprocess.check_output([strix_path + params], shell=True, timeout=1800, encoding='UTF-8').split()
            result = subprocess.check_output([strix_path + params], shell=True, encoding='UTF-8').split()
        except subprocess.TimeoutExpired as e:
            print("TIMEOUT for synthesis, more than 100 sec")
            return "UNREALIZABLE", -100
        except Exception as e:
            print("EXEPTION OCCURRED:\n" + str(e))
            print("FINISH EXEPTION\n\n")
        exec_time = time.time() - start_time
        if result[0] == "REALIZABLE":
            dot_format = ""
            for i, line in enumerate(result):
                if "digraph" not in line:
                    continue
                else:
                    dot_format = "".join(result[i:])
                    break
            return dot_format, exec_time
        if result[0] == "UNREALIZABLE":
            return "UNREALIZABLE", exec_time
        else:
            print("\n\nSTRIX RESPONSE:\n\n")
            for l in result:
                print(l)
            raise Exception("Unknown strix response: " + result[0])
    except Exception as e:
        raise e


def create_controller_if_exists(controller_input_file: str) -> Tuple[bool, float]:
    """Return true if controller has been synthesized False otherwise.
    It also return the time needed"""
    if platform.system() != "Linux":
        print(platform.system() + " is not supported for synthesis")
        raise SynthesisException("os_not_supported")

    a, g, i, o = parse_controller(controller_input_file)

    variables = [var.strip() + ": boolean" for var in i.split(',')]
    assumptions_satisfiable = check_satisfiability(variables, a)

    if not assumptions_satisfiable:
        raise SynthesisException("trivial")

    result, exec_time = get_controller(a, g, i, o)

    if result.startswith("UNREALIZABLE"):
        print("UNREALIZABLE")
        return False, exec_time

    print(controller_input_file + " IS REALIZABLE")
    dot_file_path = os.path.dirname(controller_input_file)
    dot_file_name = os.path.splitext(controller_input_file)[0]

    dot_file_name = dot_file_name.replace("specification", "controller")

    save_to_file(result, dot_file_name + ".dot")
    print("DOT file generated")

    #
    # src = Source(result, directory=dot_file_path, filename=dot_file_name, format="eps")
    # src.render(cleanup=True)
    # print(dot_file_name + ".eps  ->   mealy machine generated")
    return True, exec_time


if __name__ == '__main__':
    controller_file = sys.argv[1]
    file_path = output_path + "/" + sys.argv[1]
    controller_output = create_controller_if_exists(file_path)
