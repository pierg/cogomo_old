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
        # # output = subprocess.check_output([strix_path, params])
        # result = subprocess.run([strix_path, params], stdout=subprocess.PIPE)
        # print(result)

        print("\n\nCOMMAND:\n\n" + strix_path + params + "\n\n")


        cmd = [strix_path, params]
        result = subprocess.run(cmd, stdout=subprocess.PIPE)

        output = result.stdout.decode('utf-8')
        print("\n\nOUTPUT\n\n" + output)

        output = subprocess.check_output(cmd, encoding='UTF-8', stderr=subprocess.DEVNULL).splitlines()
        print("\n\nOUTPUT2\n\n" + output)
        return output
    except Exception as e:
        raise e


if __name__ == '__main__':
    controller_file = sys.argv[1]
    file_path = output_path + "/" + sys.argv[1]
    a, g, i, o = parse_controller(file_path)
    controller_output = get_controller(a, g, i, o)
    print(controller_output)