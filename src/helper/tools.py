import re
from typing import List, Union, Dict

from contracts.types import Type

OPERATORS = r'(^==|\*|\/|-|<=|>=|<|>|\+|!=|!|=|\(|\)|\||->|&|\s)'
TEMPORALOPS = r'^F|^G|^X|^U'
VARIABLE = r'^[A-Za-z]\w*'
INTEGER = r'^[+-]\d*|^\d*$'


def have_shared_keys(d_1:Dict[str, str], d_2: Dict[str, str]):
    for k_1 in d_1.keys():
        for k_2 in d_2.keys():
            if k_1 == k_2:
                return True
    return False


def have_shared_keys(d_1:Dict[str, str], d_2: Dict[str, str]):
    for k_1 in d_1.keys():
        for k_2 in d_2.keys():
            if k_1 == k_2:
                return True
    return False


def extract_variables_name(formula: Union[List[str], str]) -> List[str]:
    if isinstance(formula, list):
        list_variables = []
        for elem in formula:
            list_variables.extend(_extract_variables_from_string(elem))
        return list_variables
    elif isinstance(formula, str):
        return _extract_variables_from_string(formula)
    else:
        raise AttributeError


def extract_variables_types(variables: List[Type], formula: str) -> List[str]:
    """Extract the types of variables from 'variables' in a formula"""
    var_names = extract_variables_name(formula)
    var_types = []
    for t in variables:
        for v in var_names:
            if t.name == v:
                try:
                    port_type = t.port_type
                except Exception as e:
                    port_type = t.name
                var_types.append(port_type)
    return var_types


def _extract_variables_from_string(formula: str) -> List[str]:
    list_variable_names = []
    variable_pattern = re.compile(VARIABLE)
    integer_pattern = re.compile(INTEGER)
    temporal_ops = re.compile(TEMPORALOPS)
    tokens = re.split(OPERATORS, formula)
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
            if variable_pattern.match(token):
                list_variable_names.append(token)
            elif not integer_pattern.match(token):
                raise Exception("The syntax of the formula invalid: " + token)
    return list_variable_names


def save_to_file(text: str, file_path: str):
    with open(file_path + ".txt", 'w') as f:
        f.write(text)

    f.close()
