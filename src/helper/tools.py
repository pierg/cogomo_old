import re
import subprocess

from typescogomo.formulae import *
from typescogomo.formulae import LTL
from typescogomo.variables import Type
from graphviz import Source

OPERATORS = r'(^==|\*|\/|-|<=|>=|<|>|\+|!=|!|=|\(|\)|\||->|&|\s)'
TEMPORALOPS = r'^F|^G|^X|^U'
VARIABLE = r'^[A-Za-z]\w*'
INTEGER = r'^[+-]\d*|^\d*$'


def generate_buchi(formula: LTL, name: str, path: str=""):
    try:
        print(formula)
        output = subprocess.check_output(["ltl2tgba", "-B", str(formula), "-d"], encoding='UTF-8',
                                         stderr=subprocess.DEVNULL).splitlines()
        output = [x for x in output if not ('[Büchi]' in x)]

        output = "".join(output)

        src = Source(output, directory="output", filename=name, format="eps")

        src.render()

    except Exception as e:
        raise e


if __name__ == '__main__':
    formula = "GFa & GFb"
    generate_buchi(BeforeR(LTL("p"), LTL("r")), "before-r")
    generate_buchi(AfterQ(LTL("p"), LTL("q")), "after-q")

    generate_buchi(BetweenQandR(LTL("p"), LTL("q"), LTL("r")), "between-q-and-r")
    generate_buchi(AfterQuntilR(LTL("p"), LTL("q"), LTL("r")), "after-q-until-r")

    generate_buchi(UntilR(LTL("p"), LTL("r")), "until-r")
    generate_buchi(WeakUntilR(LTL("p"), LTL("r")), "weak-until-r")
    generate_buchi(ReleaseR(LTL("r"), LTL("p")), "release-r")
    generate_buchi(StrongReleaseR(LTL("r"), LTL("p")), "strong-release-r")


    generate_buchi(AfterQ(ReleaseR(LTL("!alarm"), LTL("warehouse")), LTL("alarm")), "after-alarm-release")

    generate_buchi(AfterQ(UntilR(ReleaseR(LTL("!alarm"), LTL("warehouse")), LTL("!alarm")), LTL("alarm")), "release-alarm-until-not-alarm")

    generate_buchi(AfterQ(UntilR(LTL("warehouse"), LTL("!alarm")), LTL("alarm")), "after-alarm-warehouse-until-not-alarm")

    generate_buchi(AfterQuntilR(LTL("warehouse"), LTL("alarm"), LTL("!alarm")), "after-alarm-until-not-alarm-previous")

    generate_buchi(BetweenQandR(LTL("warehouse"), LTL("alarm"), LTL("!alarm")), "between-alarm-not-alarm-previous")






def extract_variables_from_LTL(variables: List[Type],
                               expression: LTL) -> List[Type]:
    """Extract the varialbes from 'variables' in a formula"""
    var_names = extract_variables_name(expression)
    variables_set = []
    for t in variables:
        for v in var_names:
            if t.name == v:
                variables_set.append(t)
    return variables_set


def extract_variables_types(variables: List[Type],
                            expression: LTL) -> List[str]:
    """Extract the types of variables from 'variables' in a formula"""
    var_names = extract_variables_name(expression)
    var_types = []
    for t in variables:
        for v in var_names:
            if t.name == v:
                try:
                    port_type = t.port_type
                except:
                    port_type = t.name
                var_types.append(port_type)
    return var_types


def extract_variables_name(expression: LTL) -> List[str]:
    integer_pattern = re.compile(INTEGER)
    list_terms = extract_terms(expression)

    """Excluding the numbers"""
    for term in list(list_terms):
        if integer_pattern.match(term):
            list_terms.remove(term)

    return list_terms


def extract_terms(expression: LTL) -> List[str]:
    list_terms = []
    variable_pattern = re.compile(VARIABLE)
    integer_pattern = re.compile(INTEGER)
    temporal_ops = re.compile(TEMPORALOPS)

    tokens = re.split(OPERATORS, expression.formula)
    tokens = list(filter(None, tokens))
    tokens_stripped = []
    for elem in tokens:
        stripped = elem.strip()
        stripped = re.sub(OPERATORS, '', stripped)
        if stripped is not '':
            tokens_stripped.append(stripped)
    for token in tokens_stripped:
        if not (temporal_ops.match(token)
                or token == "FALSE"
                or token == "TRUE"):
            if variable_pattern.match(token) or \
                    integer_pattern.match(token):
                list_terms.append(token)
            else:
                raise Exception("The syntax of the formula invalid: " + token)
    return list_terms


def save_to_file(text: str, file_path: str):
    with open(file_path + ".txt", 'w') as f:
        f.write(text)

    f.close()
