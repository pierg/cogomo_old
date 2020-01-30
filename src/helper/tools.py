import re
from typing import List

OPERATORS = '==|\*|\/|-|<=|>=|<|>|\+|!=|\(|\)|\||->|&'

def extract_variables_name(list_a: List[str]) -> List[str]:
    list_variable_names = []

    for prop in list_a:
        list_elements = re.split(OPERATORS, prop)
        for prop in list_elements:
            prop = re.sub("[^a-zA-Z]+", "", prop)
            prop = prop.strip()
            if prop != "":
                list_variable_names.append(prop)

    return list_variable_names
