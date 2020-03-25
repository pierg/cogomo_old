from flask import request

from src.z3.src_z3.operations import *
from tests.component_selection_platooning import libraries
from web import socketio
from flask_socketio import emit
import json

from multiprocessing import Lock
from multiprocessing.managers import BaseManager

from src_z3.parser import *

lock = Lock()

# SessionID -> Dict[name -> CGT]
sess_goals: [str, list] = {}

# SessionID -> root CGT
sess_cgts = {}


def get_goals(session_id):
    """Get a list goals of the session_id or create new entry and return an empty list"""

    with lock:
        if session_id in sess_goals.keys():
            return sess_goals[session_id]
        else:
            sess_goals[session_id] = {}
            return {}


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
        if session_id in sess_cgts.keys():
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

    s_goals.update(n_goals)

    set_goals(request.sid, s_goals)

    emit('notification',
         {'type': "success", 'content': "Goals saved"})

    render_goals(request.sid)


@socketio.on('goals_link')
def goals_link(message):
    print('-----------------------')
    print('Goals link from - %s' + request.sid)
    print('-----------------------')

    # emit('notification',
    #      {'type': "success", 'content': "Linking goals received"})

    s_goals = get_goals(request.sid)
    s_cgt = get_cgt(request.sid)

    if message["operation"] == "composition":
        goals = message["goals"]
        comp_goals = []
        for g in goals:
            comp_goals.append(s_goals[g])

        try:
            new_goal = compose_goals(comp_goals, name=message["name"], description=message["description"])

        except Exception as e:
            txt = str(e)
            txt = "<br />".join(txt.split("\n"))
            emit('alert',
                 {'title': "Conflict detected", 'content': txt})
            return

        s_goals.update({message["name"]: new_goal})

        set_goals(request.sid, s_goals)

        emit('notification',
             {'type': "success", 'content': "New goal created"})

        render_goals(request.sid)

    elif message["operation"] == "conjunction":
        goals = message["goals"]
        conj_goals = []
        for g in goals:
            conj_goals.append(s_goals[g])

        try:
            new_goal = conjoin_goals(conj_goals, name=message["name"], description=message["description"])

        except Exception as e:
            txt = str(e)
            txt = "<br />".join(txt.split("\n"))
            emit('alert',
                 {'title': "Conflict detected", 'content': txt})
            return

        s_goals.update({message["name"]: new_goal})

        set_goals(request.sid, s_goals)

        emit('notification',
             {'type': "success", 'content': "New goal created"})

        render_goals(request.sid)


    elif message["operation"] == "refinement":
        abstract_goal_name = message["abstract"]
        refined_goal_name = message["refined"]

        abstract_goal = get_goals(request.sid)[abstract_goal_name]
        refined_goal = get_goals(request.sid)[refined_goal_name]

        try:
            refine_goal(abstract_goal, refined_goal)

        except Exception as e:
            txt = str(e)
            txt = "<br />".join(txt.split("\n"))
            emit('alert',
                 {'title': "Refinement unsuccessful", 'content': txt})
            return

        emit('alert',
             {'titles': "Refinement successful"})

        return


    elif message["operation"] == "mapping":
        goal_name_to_map = message["goal"]
        library_name = message["library"]

        s_goals = get_goals(request.sid)

        goal = s_goals[goal_name_to_map]

        library = libraries[library_name]

        try:
            new_goal, msg = mapping_complete(library, goal)

        except Exception as e:
            txt = str(e)
            txt = "<br />".join(txt.split("\n"))
            emit('alert',
                 {'title': "Mapping unsuccessful", 'content': txt})
            return

        name = new_goal.get_name()
        s_goals.update({name: new_goal})

        set_goals(request.sid, s_goals)

        emit('notification',
             {'type': "success", 'content': "Goals added"})

        msg = "<br />".join(msg.split("\n"))
        emit('alert',
             {'title': "Mapping successful", 'content': msg})

        render_goals(request.sid)
        return


    else:
        raise Exception("Unknown operation")

    print(len(s_goals))

    set_goals(request.sid, s_goals)

    emit('notification',
         {'type': "success", 'content': "Goals saved"})

    render_goals(request.sid)


def render_goals(session_id):
    s_goals = get_goals(session_id)

    goal_list = []

    for name, cgtgoal in s_goals.items():
        goal = {}
        goal['name'] = name
        goal['description'] = cgtgoal.get_description()
        a, g = cgtgoal.render_A_G()
        goal['assumptions'] = "<br />".join(a.split("\n"))
        goal['guarantees'] = "<br />".join(g.split("\n"))
        goal_list.append(goal)

    goals_json = json.dumps(goal_list)

    emit('goal_list', goals_json)
