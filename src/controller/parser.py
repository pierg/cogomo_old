from typing import Tuple

from checks.tools import And

ASSUMPTIONS_HEADER = 'ASSUMPTIONS'
CONSTRAINTS_HEADER = 'CONSTRAINTS'
GUARANTEES_HEADER = 'GUARANTEES'
INS_HEADER = 'INPUTS'
OUTS_HEADER = 'OUTPUTS'
END_HEADER = 'END'
COMMENT_CHAR = '#'
FILE_HEADER_INDENT = 0
DATA_INDENT = 1
TAB_WIDTH = 2


def parse_controller(file_path: str) -> Tuple[str, str, str, str]:
    """Returns: assumptions, guarantees, inputs, outputs"""

    assumptions = []
    guarantees = []
    inputs = []
    outputs = []

    file_header = ""

    with open(file_path, 'r') as ifile:
        for line in ifile:
            line, ntabs = _count_line(line)

            # skip empty lines
            if not line:
                continue

            # parse file header line
            elif ntabs == FILE_HEADER_INDENT:

                if ASSUMPTIONS_HEADER == line:
                    if file_header == "":
                        file_header = line
                    else:
                        Exception("File format not supported")

                elif CONSTRAINTS_HEADER == line:
                    if file_header == ASSUMPTIONS_HEADER:
                        file_header = line
                    else:
                        Exception("File format not supported")

                elif GUARANTEES_HEADER == line:
                    if file_header == CONSTRAINTS_HEADER:
                        file_header = line
                    else:
                        Exception("File format not supported")

                elif INS_HEADER == line:
                    if file_header == GUARANTEES_HEADER:
                        file_header = line
                    else:
                        Exception("File format not supported")

                elif OUTS_HEADER == line:
                    if file_header == INS_HEADER:
                        file_header = line
                    else:
                        Exception("File format not supported")

                elif END_HEADER == line:
                    if file_header == OUTS_HEADER:
                        if len(assumptions) == 0:
                            assumptions.append("true")
                        return And(assumptions), And(guarantees), ",".join(inputs), ",".join(outputs)
                    else:
                        Exception("File format not supported")
                else:
                    raise Exception("Unexpected File Header: " + line)

            else:

                if ASSUMPTIONS_HEADER == file_header:
                    if ntabs == DATA_INDENT:
                        assumptions.append(line.strip())

                if CONSTRAINTS_HEADER == file_header:
                    if ntabs == DATA_INDENT:
                        guarantees.append(line.strip())

                if GUARANTEES_HEADER == file_header:
                    if ntabs == DATA_INDENT:
                        guarantees.append(line.strip())

                if INS_HEADER == file_header:
                    if ntabs == DATA_INDENT:
                        inputs.append(line.strip())

                if OUTS_HEADER == file_header:
                    if ntabs == DATA_INDENT:
                        outputs.append(line.strip())


def _count_line(line):
    """Returns a comment-free, tab-replaced line with no whitespace and the number of tabs"""
    line = line.split(COMMENT_CHAR, 1)[0]  # remove comments
    tab_count = 0
    space_count = 0
    for char in line:
        if char == ' ':
            space_count += 1
        elif char == '\t':
            tab_count += 1
        else:
            break
    tab_count += int(space_count / 4)
    line = line.replace('\t', ' ' * TAB_WIDTH)  # replace tabs with spaces
    return line.strip(), tab_count
