from flask import request
from web import socketio
from flask_socketio import emit
import json

from multiprocessing import Lock
from multiprocessing.managers import BaseManager

from src.parser import *

lock = Lock()

# SessionID -> list of goals
sess_goals = {}

# SessionID -> CGT
sess_cgts = {}


def get_goals(session_id):
    """Get a list goals of the session_id or create new entry and return an empty list"""

    with lock:
        if session_id in sess_goals.keys():
            return sess_goals[session_id]
        else:
            sess_goals[session_id] = []
            return []


def set_goals(session_id: str, goals_to_set: list):
    """Add the goals in list of goals of the session_id"""

    with lock:
        if session_id in sess_goals.keys():
            sess_goals[session_id] = goals_to_set
        else:
            raise Exception("No session ID found")


def get_cgt(session_id):
    """Get the CGT of the session_id or None"""

    with lock:
        if session_id in sess_goals.keys():
            return sess_cgts[session_id]
        else:
            return None


def set_cgt(session_id: str, cgt: CGTGoal):
    """Set the CGT to session_id"""

    with lock:
        if session_id in sess_goals.keys():
            sess_cgts[session_id] = cgt
        else:
            raise Exception("No session ID found")


@socketio.on('goals_text')
def goals_text(message):
    print('-----------------------')
    print('Goals received from - %s' + request.sid)
    print('-----------------------')

    emit('notification',
         {'type': "success", 'content': "Goals received"})

    s_goals = get_goals(request.sid)

    n_goals = parse_from_string(message['data'])

    for n_goal in n_goals:
        if n_goal not in s_goals:
            s_goals.append(n_goal)

    set_goals(request.sid, s_goals)

    emit('notification',
         {'type': "success", 'content': "Goals saved"})

    render_goals(request.sid)


def render_goals(session_id):

    s_goals = get_goals(session_id)

    goals_json = json.dumps(s_goals)

    emit('goal_list', goals_json)



    # goal_list
    # for name, cgtgoal in s_goals.items():
    #     goal = {}
    #     goal['name'] = name
    #     goal['description'] = cgtgoal.description
    #     goal_list.append(goal)
    #
    # goals_json = json.dumps(goal_list)
    #
    # emit('goal_list', goals_json)
