import os
import sys

from goals.context import Context
from src.patterns.patterns import *
from src.goals.operations import *
from src.components.operations import *
from src.helper.parser import *

file_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(os.getcwd(), os.path.pardir))

if __name__ == "__main__":
    """Check out example.py"""
