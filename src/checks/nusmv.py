import re
import subprocess
from src.helper.logic import *

smvfile = "nusmvfile.smv"

def check_satisfiability(variables, propositions):
    print("checking sat of: " + str(propositions))

    propositions_copy = propositions.copy()

    for index, prop in enumerate(propositions_copy):
        """Renaming propositions"""
        propositions_copy[index] = re.sub("_port_\d+|_port", "", prop)

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
    except Exception:
        print("NuSMV Exception")
    output = [x for x in output if not (x[:3] == '***' or x[:7] == 'WARNING' or x == '')]

    for line in output:

        if line[:16] == '-- specification':
            if 'is false' in line:
                print(And(propositions_copy) + "\nis SAT\n")
                return True
            elif 'is true' in line:
                print(And(propositions_copy) + "\nis UNSAT\n")
                return False


def check_validity(variables, proposition):
    print("checking validity of: " + str(proposition))

    """Renaming propositions"""
    proposition_copy = re.sub("_port_\d+|_port", "", proposition)

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

    output = subprocess.check_output(['NuSMV', smvfile], encoding='UTF-8').splitlines()

    output = [x for x in output if not (x[:3] == '***' or x[:7] == 'WARNING' or x == '')]

    for line in output:

        if line[:16] == '-- specification':
            if 'is false' in line:
                # print(proposition_copy + "\nis NOT VALID\n")
                return False
            elif 'is true' in line:
                print(proposition_copy + "\nis VALID\n")
                return True

