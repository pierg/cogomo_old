import os

from src.controller.strix import get_controller
from src.controller.parser import parse_controller


file_path = os.path.dirname(os.path.abspath(__file__)) + "/clustering"

if __name__ == "__main__":

    a, g, i, o = parse_controller(file_path + "/controller-input.txt")
    controller = get_controller(a, g, i, o)

    print(controller)
