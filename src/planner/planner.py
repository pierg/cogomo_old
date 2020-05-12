import os
import subprocess
from typing import List

import docker




from graphviz import Source

from checks.tools import And, Implies


def get_planner(assumptions: List[str], guarantees: List[str], ins: List[str], outs: List[str]):
    client = docker.from_env()
    client.containers.run("ubuntu", "echo hello world")

    assumptions = And(assumptions)
    guarantees = And(guarantees)
    ins = ", ".join(ins)
    outs = ", ".join(outs)

    filepath = os.getcwd()

    params = ' -f "' + Implies(assumptions, guarantees) + '" --ins="' + ins + '" --outs="' + outs + '"'
    # params = '-f "true -> true" --ins="a" --outs="b"'

    # args = ['./strix', params]
    # subprocess.call(args)

    output = subprocess.check_output(['strix', params])

    return output