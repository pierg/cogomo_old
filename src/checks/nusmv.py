import re
import subprocess
from typing import Dict

from src.helper.logic import *

smvfile = "nusmvfile.smv"


def check_satisfiability(variables: Dict[str, str], propositions: List[str]) -> bool:
    propositions_copy = propositions.copy()

    for index, prop in enumerate(propositions_copy):
        """Renaming propositions"""
        propositions_copy[index] = re.sub(r"_port_\d+|_port", "", prop)

    """Write the NuSMV file"""
    with open(smvfile, 'w') as ofile:

        # write module heading declaration
        ofile.write('MODULE main\n')

        # write variable type declarations
        ofile.write('VAR\n')
        for name, type in variables.items():
            ofile.write('\t' + name + ': ' + type + ';\n')

        ofile.write('\n')

        ofile.write('LTLSPEC ')

        ofile.write(Not(And(propositions_copy)))

        ofile.write('\n')

    try:
        output = subprocess.check_output(['NuSMV', smvfile], encoding='UTF-8').splitlines()
    except Exception as e:
        print("NuSMV Exception")
        print(str(e))

    output = [x for x in output if not (x[:3] == '***' or x[:7] == 'WARNING' or x == '')]

    for line in output:

        if line[:16] == '-- specification':
            if 'is false' in line:
                print("SAT:\t" + And(propositions_copy))
                return True
            elif 'is true' in line:
                return False


def check_validity(variables, proposition):
    print("checking validity of:\t" + proposition)
    """Renaming propositions"""
    proposition_copy = re.sub(r"_port_\d+|_port", "", proposition)

    """Write the NuSMV file"""
    with open(smvfile, 'w') as ofile:

        # write module heading declaration
        ofile.write('MODULE main\n')

        # write variable type declarations
        ofile.write('VAR\n')
        for name, type in variables.items():
            ofile.write('\t' + name + ': ' + type + ';\n')

        ofile.write('\n')

        ofile.write('LTLSPEC ' + proposition_copy)

    output = subprocess.check_output(['NuSMV', smvfile], encoding='UTF-8', stderr=subprocess.STDOUT).splitlines()

    output = [x for x in output if not (x[:3] == '***' or x[:7] == 'WARNING' or x == '')]

    for line in output:

        if line[:16] == '-- specification':
            if 'is false' in line:
                return False
            elif 'is true' in line:
                print("VALID:\t" + proposition)
                return True
