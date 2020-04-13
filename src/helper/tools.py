import re
import subprocess
from typing import List

from graphviz import Source

OPERATORS = r'(^==|\*|\/|-|<=|>=|<|>|\+|!=|!|=|\(|\)|\||->|&|\s)'
TEMPORALOPS = r'^F|^G|^X|^U'
VARIABLE = r'^[A-Za-z]\w*'
INTEGER = r'^[+-]\d*|^\d*$'





def extract_variables_name(expression: str) -> List[str]:
    integer_pattern = re.compile(INTEGER)
    list_terms = extract_terms(expression)

    """Excluding the numbers"""
    for term in list(list_terms):
        if integer_pattern.match(term):
            list_terms.remove(term)

    return list_terms


def extract_terms(expression: str) -> List[str]:
    list_terms = []
    variable_pattern = re.compile(VARIABLE)
    integer_pattern = re.compile(INTEGER)
    temporal_ops = re.compile(TEMPORALOPS)

    tokens = re.split(OPERATORS, expression)
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
