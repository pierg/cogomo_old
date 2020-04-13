import os
import random
import string

from src.goals.cgtgoal import *
from src.components.components import *

from contracts.patterns import *
from typescogomo.formulae import Context
from typescogomo.variables import *

# contract file attributes
TAB_WIDTH = 2
FILE_HEADER_INDENT = 0

CONSTANTS_HEADER_INDENT = 0
CONSTANTS_DATA_INDENT = 1
GOAL_HEADER_INDENT = 0
GOAL_SUBHEADER_INDENT = 1
GOAL_DATA_INDENT = 2

COMPONENT_HEADER_INDENT = 0
COMPONENT_SUBHEADER_INDENT = 1
COMPONENT_DATA_INDENT = 2

COMMENT_CHAR = '#'
ASSIGNMENT_CHAR = ':='

CONSTANTS_HEADER = 'CONSTANTS'

GOAL_HEADER = 'GOAL'
ENDGOALS_HEADER = 'ENDGOALS'
COMPONENT_HEADER = 'COMPONENT'
ENDCOMPONENT_HEADER = 'ENDCOMPONENTS'
COMPONENT_ID_HEADER = 'ID'
GOAL_NAME_HEADER = 'NAME'
DESCRIPTION_HEADER = 'DESCRIPTION'
CONTEXT_HEADER = 'CONTEXT'
PATTERN_HEADER = 'PATTERN'
PARAMETERS_HEADER = 'PARAMETERS'
VARIABLES_HEADER = 'VARIABLES'
ASSUMPTIONS_HEADER = 'ASSUMPTIONS'
GUARANTEES_HEADER = 'GUARANTEES'



def parse_from_string(string_to_parse):

    temp_text_file_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)) + ".txt"

    with open(temp_text_file_name, "w") as text_file:
        text_file.write(string_to_parse)

    goals = parse(temp_text_file_name)

    if os.path.exists(temp_text_file_name):
        os.remove(temp_text_file_name)
    else:
        print("The file does not exist")

    return goals



def parse(specfile):
    """Parses the system specification file and returns the contracts and checks

    Args:
        specfile: a string input file name for the system specification file

    Returns:
        A tuple containing a contracts object and a checks object
    """

    cgt_goal = CGTGoal()
    contract = Contract()
    component = None
    context = None
    description = None

    goal_dictionary = {}
    components_dictionary = {}

    constants = {}
    file_header = ''
    goal_header = ''

    with open(specfile, 'r') as ifile:
        for line in ifile:
            line, ntabs = _count_line(line)

            # skip empty lines
            if not line:
                continue

            # parse file header line
            elif ntabs == FILE_HEADER_INDENT:
                # store previously parsed contract
                if GOAL_HEADER in file_header or ENDGOALS_HEADER in file_header:
                    if contract.is_full():
                        goal_dictionary[cgt_goal.name] = CGTGoal(name=cgt_goal.name,
                                                                 description= description,
                                                                 context= context,
                                                                 contracts=[contract])
                    else:
                        raise Exception("The Goal has Incomplete Parameters")
                if COMPONENT_HEADER in file_header or ENDCOMPONENT_HEADER in file_header:
                    if component is not None and component.is_full():
                        components_dictionary[component.id] = component
                    else:
                        raise Exception("The Component has Incomplete Parameters")

                if CONSTANTS_HEADER in line:
                    file_header = line
                elif GOAL_HEADER in line:
                    file_header = line
                elif COMPONENT_HEADER in line:
                    file_header = line
                else:
                    raise Exception("Unexpected File Header: " + line)

            else:

                if CONSTANTS_HEADER in file_header:
                    if ntabs == CONSTANTS_DATA_INDENT:
                        var, init = line.split(ASSIGNMENT_CHAR, 1)
                        if "." in init.strip():
                            constants[var.strip()] = float(init.strip())
                        else:
                            constants[var.strip()] = int(init.strip())

                elif COMPONENT_HEADER in file_header:
                    if ntabs == COMPONENT_HEADER_INDENT:
                        component_header = line
                    elif ntabs == COMPONENT_SUBHEADER_INDENT:
                        component_header = line
                    elif ntabs == COMPONENT_DATA_INDENT:
                        if COMPONENT_ID_HEADER in component_header:
                            component = Component(component_id=line.strip())
                        elif DESCRIPTION_HEADER in component_header:
                            component.description = line.strip()
                        elif VARIABLES_HEADER in component_header:
                            component.add_variables([eval(line.strip())])
                        elif ASSUMPTIONS_HEADER in component_header:
                            component.add_assumptions(line.strip())
                        elif GUARANTEES_HEADER in component_header:
                            component.add_guarantee(line.strip())
                        else:
                            raise Exception("Unexpected Component Header: " + component_header)


                elif GOAL_HEADER in file_header:
                    goal_pattern = None
                    if ntabs == GOAL_HEADER_INDENT:
                        goal_header = line
                    elif ntabs == GOAL_SUBHEADER_INDENT:
                        goal_header = line
                    elif ntabs == GOAL_DATA_INDENT:
                        if GOAL_NAME_HEADER in goal_header:
                            cgt_goal.name = line.strip()
                            for key, value in constants.items():
                                var = Type(str(key), str(value))
                                contract.add_variable(var)
                        elif DESCRIPTION_HEADER in goal_header:
                            description = line.strip()
                        elif CONTEXT_HEADER in goal_header:
                            context = Context(LTL(line.strip()))
                        elif PATTERN_HEADER in goal_header:
                            pattern = line.strip()
                            contract = eval(pattern)
                        elif VARIABLES_HEADER in goal_header:
                            key, value = line.split(ASSIGNMENT_CHAR, 1)
                            var = Type(str(key), str(value))
                            contract.add_variable(var)
                        elif ASSUMPTIONS_HEADER in goal_header:
                            contract.add_assumptions(Assumption(line.strip()))
                        elif GUARANTEES_HEADER in goal_header:
                            contract.add_guarantee(Guarantee(line.strip()))
                        else:
                            raise Exception("Unexpected Goal Header: " + goal_header)

    print("Loaded Goals:\n\n____________________________________________________________________\n\n")
    for key, value in goal_dictionary.items():
        print(str(value) + "____________________________________________________________________\n\n")
    if len(components_dictionary) > 0:
        return components_dictionary
    if len(goal_dictionary) > 0:
        return goal_dictionary


def _is_string_number(string):
    """Returns true if string is a float or int"""
    try:
        int(string)
        return True
    except:
        try:
            float(string)
            return True
        except:
            return False


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
