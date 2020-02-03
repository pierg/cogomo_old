import re
from typing import List

OPERATORS = '==|\*|\/|-|<=|>=|<|>|\+|!=|\(|\)|\||->|&|F|G|U|X|='



def extract_variables_name(list_a: List[str]) -> List[str]:
    list_variable_names = []

    for prop in list_a:
        list_elements = re.split(OPERATORS, prop)
        for prop in list_elements:
            prop = re.sub("[^a-zA-Z_]+", "", prop)
            prop = prop.strip()
            if prop != "":
                list_variable_names.append(prop)

    return list_variable_names


def save_to_file(text: str, file_path: str):

    with open(file_path + ".txt", 'w') as f:

        f.write(text)

    f.close()
