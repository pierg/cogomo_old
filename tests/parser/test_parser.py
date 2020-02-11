from src.components.operations import *
from src.goals.operations import *
from src.helper.parser import *


def test_parser_pattern():
    list_of_goals = parse("robots_test.txt")

    components = parse("robots_components_simple.txt")


    print(components)
