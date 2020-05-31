import os

from src.controller.strix import get_controller
from src.controller.parser import parse_controller


file_path = os.path.dirname(os.path.abspath(__file__)) + "/tests"

if __name__ == "__main__":

    try:
        a, g, i, o = parse_controller(file_path + "/controller-input.txt")
        controller = get_controller(a, g, i, o)
        print(controller)
    except Exception as e:
        print(e)

    try:
        a, g, i, o = parse_controller(file_path + "/controller-input_0.txt")
        controller = get_controller(a, g, i, o)
        print(controller)
    except Exception as e:
        print(e)

    try:
        a, g, i, o = parse_controller(file_path + "/controller-input_1.txt")
        controller = get_controller(a, g, i, o)
        print(controller)
    except Exception as e:
        "Exception1"

    try:
        a, g, i, o = parse_controller(file_path + "/controller-input_2.txt")
        controller = get_controller(a, g, i, o)
        print(controller)
    except Exception as e:
        "Exception2"

    try:
        a, g, i, o = parse_controller(file_path + "/controller-input_3.txt")
        controller = get_controller(a, g, i, o)
        print(controller)
    except Exception as e:
        "Exception3"

    try:
        a, g, i, o = parse_controller(file_path + "/controller-input_4.txt")
        controller = get_controller(a, g, i, o)
        print(controller)
    except Exception as e:
        "Exception4"

    try:
        a, g, i, o = parse_controller(file_path + "/controller-input_5.txt")
        controller = get_controller(a, g, i, o)
        print(controller)
    except Exception as e:
        "Exception5"

    try:
        a, g, i, o = parse_controller(file_path + "/controller-input_6.txt")
        controller = get_controller(a, g, i, o)
        print(controller)
    except Exception as e:
        "Exception6"
