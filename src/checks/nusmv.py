import subprocess
from src.contracts.types import *
from src.helper.logic import *

smvfile = "nusmvfile.smv"


def check_satisfiability(variables: List[Type],
                         propositions: List[LTL]) -> bool:

    if len(propositions) == 1 and propositions[0].formula == "TRUE":
        return True
    if len(propositions) == 0:
        return True

    """Write the NuSMV file"""
    with open(smvfile, 'w') as ofile:

        ofile.write('MODULE main\n')

        ofile.write('VAR\n')

        vars_to_add = []

        for v in variables:
            vars_to_add.append((v.name, v.nuxmvtype))

        for v, t in list(set(vars_to_add)):
            ofile.write('\t' + v + ": " + t + ";\n")

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
                    print("SAT:\t" + str(And(propositions)))
                    return True
                elif 'is true' in line:
                    return False

    except Exception as e:
        raise e


def check_validity(variables: List[Type],
                   proposition: LTL,
                   check_type: bool = False) -> bool:

    proposition = proposition.formula

    """Write the NuSMV file"""
    with open(smvfile, 'w') as ofile:

        # write module heading declaration
        ofile.write('MODULE main\n')

        # write variable type declarations
        ofile.write('VAR\n')
        vars_to_add = []
        """Change name of the ports with their type"""
        for v in variables:
            if check_type and hasattr(v, "port_type"):
                vars_to_add.append((v.port_type, v.nuxmvtype))
                proposition = proposition.replace(v.name, v.port_type)
            else:
                vars_to_add.append((v.name, v.nuxmvtype))

        for v, t in list(set(vars_to_add)):
            ofile.write('\t' + v + ": " + t + ";\n")

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
                    print("VALID:\t" + proposition)
                    return True

    except Exception as e:
        raise e
