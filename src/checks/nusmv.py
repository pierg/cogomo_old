import subprocess
from typing import Tuple, List, Union
from checks.tools import And, Not

smvfile = "nusmvfile.smv"


def check_satisfiability(variables: List[str],
                         propositions: Union[List[str], str]) -> bool:
    if isinstance(propositions, str):
        propositions = [propositions]

    if len(propositions) == 1 and propositions[0] == "TRUE":
        return True
    if len(propositions) == 0:
        return True

    """Write the NuSMV file"""
    with open(smvfile, 'w') as ofile:

        ofile.write('MODULE main\n')

        ofile.write('VAR\n')

        for v in list(set(variables)):
            ofile.write('\t' + v + ";\n")

        ofile.write('\n')
        ofile.write('LTLSPEC ')
        ofile.write(str(Not(And(propositions))))

        ofile.write('\n')

    try:
        output = subprocess.check_output(['nuXmv', smvfile], encoding='UTF-8', stderr=subprocess.DEVNULL).splitlines()
        output = [x for x in output if not (x[:3] == '***' or x[:7] == 'WARNING' or x == '')]
        for line in output:
            if line[:16] == '-- specification':
                if 'is false' in line:
                    print("\t\t\tSAT:\t" + str(And(propositions)))
                    return True
                elif 'is true' in line:
                    return False

    except Exception as e:
        raise e


def check_validity(variables: List[str],
                   proposition: str) -> bool:
    proposition = proposition

    """Write the NuSMV file"""
    with open(smvfile, 'w') as ofile:

        ofile.write('MODULE main\n')

        ofile.write('VAR\n')

        for v in list(set(variables)):
            ofile.write('\t' + v + ";\n")

        ofile.write('\n')
        ofile.write('LTLSPEC ' + proposition)

    try:
        output = subprocess.check_output(['nuXmv', smvfile], encoding='UTF-8', stderr=subprocess.DEVNULL).splitlines()
        output = [x for x in output if not (x[:3] == '***' or x[:7] == 'WARNING' or x == '')]
        for line in output:
            if line[:16] == '-- specification':
                if 'is false' in line:
                    return False
                elif 'is true' in line:
                    print("\t\t\tVALID:\t" + proposition)
                    return True

    except Exception as e:
        with open(smvfile, 'r') as fin:
            print(fin.read())
        raise e
