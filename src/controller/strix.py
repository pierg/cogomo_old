import os
import subprocess
from typing import Tuple, List, Union
from checks.tools import And, Not, Implies

strix_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..', 'bin', 'ubuntu_19.10', 'strix'))

def get_controller(assumptions: str, guarantees: str, ins: str, outs: str) -> str:
    try:
        params = ' -f "' + Implies(assumptions, guarantees) + '" --ins="' + ins + '" --outs="' + outs + '"'
        print("\n\n" + params + "\n\n")
        output = subprocess.check_output([strix_path, params], encoding='UTF-8', stderr=subprocess.DEVNULL)
        print("\n\nOUTPUT\n\n" + output)
        return output
    except Exception as e:
        raise e