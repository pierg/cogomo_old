#!/usr/bin/env python
"""Test Library module provides a test suite for LTL contract verifier"""

import os
import sys

from src_z3.parser import parse
from src_z3.cgtgoal import *

from src_z3.operations import *

import pathlib


def platooning_example():
    """Parse Goals from Structured Text File"""

    curpath = os.path.dirname(os.path.realpath(__file__))

    goals = parse(os.path.join(curpath, 'input_files/example_platooning.txt'))

    keep_short_distance = conjoin_goals(
        [goals["accelerate_distance"], goals["decelerate_distance"], goals["maintainspeed_distance"]],
        name="keep_short_distance",
        description="keep a short distance from the vehicle ahead")


    follow_leader = conjoin_goals(
        [goals["accelerate_follow"], goals["decelerate_follow"], goals["maintainspeed_follow"]],
        name="follow_leader",
        description="follow the leader vehicle by keeping its speed")

    prioritize_goal(keep_short_distance, follow_leader)

    speed_control = conjoin_goals(
        [keep_short_distance, follow_leader],
        name="speed_control",
        description="control the speed of the vehicle based either on the distance to the vehicle in front "
                    "or according the the leader of the platoon")

    communicate_with_platoon_leader_refined = compose_goals([
        goals['enstablish_connection_fixed'],
        goals['retrieve_information']], "communicate_with_platoon_leader_refined")


    refine_goal(goals['communicate_with_platoon_leader'],
                communicate_with_platoon_leader_refined)

    following_communication = compose_goals(
        [speed_control, goals['communicate_with_platoon_leader']],
        name="following_communication",
        description="followin mode of the platoon"
    )

    goals["keep_short_distance"] = keep_short_distance
    goals["follow_leader"] = follow_leader
    goals["speed_control"] = speed_control
    goals["communicate_with_platoon_leader_refined"] = communicate_with_platoon_leader_refined
    goals["following_communication"] = following_communication

    print(str(following_communication.n_children()) + " NODES TOTAL")

    return goals, following_communication


if __name__ == '__main__':
    platooning_example()


