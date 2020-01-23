#!/usr/bin/env python
"""Test Library module provides a test suite for LTL contract verifier"""

import os
import sys

from src.parser import parse
from src.cgtgoal import *

from src.operations import *

sys.path.append(os.path.join(os.getcwd(), os.path.pardir))



if __name__ == "__main__":

    goals = parse('../input_files/incorrect_refinement.txt')

    refine_goal(goals["abstraction"], goals["refinement_a"])


