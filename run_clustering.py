import os
import shutil
import sys
from copy import deepcopy
from typing import List

from checks.tools import And, Or
from controller.synthesis import create_controller_if_exists, SynthesisException
from goals.cgtgoal import CGTGoal
from goals.helpers import generate_general_controller_inputs_from_goal, generate_controller_input_text
from goals.operations import create_contextual_clusters, create_cgt, CGTFailException, pretty_cgt_exception, \
    pretty_print_summary_clustering, conjunction
from helper.tools import save_to_file

from mission_specification import get_inputs
from typescogomo.formula import OrLTL

results_path = os.path.dirname(os.path.abspath(__file__)) + "/output/results"
try:
    shutil.rmtree(results_path)
except:
    pass

sys.path.append(os.path.join(os.getcwd(), os.path.pardir))

ap, rules, goals = get_inputs()


def pretty_print_goals(ap: dict, rules: dict, goals: List[CGTGoal]) -> str:
    ret = ""
    for g in goals:
        ret += "name:    \t" + g.name + "\n"
        ret += "context: \t" + str(OrLTL(g.context)) + "\n"
        ret += "patterns:\t" + str(g.contracts[0].guarantees.formula) + "\n"
        ret += "\n"
    return ret


def create_general_controller_from_goals(goals: List[CGTGoal], folder_path: str, type: str):
    assumptions = []
    guarantees = []
    inputs = set()
    outputs = set()

    for goal in goals:
        assum, guaran, ins, outs = generate_general_controller_inputs_from_goal(ap, rules, goal, complete=True)
        assumptions.extend(assum)
        guarantees.extend(guaran)
        inputs.update(set(ins))
        outputs.update(set(outs))

    controller_file_name = folder_path + "specification.txt"
    if type == "AND":
        save_to_file(generate_controller_input_text(assumptions, guarantees, list(inputs), list(outputs)),
                     controller_file_name)

    elif type == "OR":
        save_to_file(generate_controller_input_text([Or(assumptions)], guarantees, list(inputs), list(outputs)),
                     controller_file_name)

    else:
        raise Exception("type error, either AND or OR")

    controller_generated = False
    trivial = False
    exec_time = 0.0
    try:
        controller_generated, exec_time = create_controller_if_exists(controller_file_name)
    except SynthesisException as e:
        if e.os_not_supported:
            print("Os not supported for synthesis. Only linux can run strix")
        elif e.trivial:
            trivial = True
            controller_generated = True
            print("The assumptions are not satisfiable. The controller is trivial.")

    return controller_generated, trivial, exec_time


def generate_controller_from_cgt(cgt: CGTGoal, folder_path, complete):
    assum, guaran, ins, outs = generate_general_controller_inputs_from_goal(ap, rules, cgt, complete)
    save_to_file(generate_controller_input_text(assum, guaran, ins, outs),
                 folder_path + "specification.txt")

    exec_time = 0.0
    realizable = False
    try:
        controller_generated, exec_time = create_controller_if_exists(folder_path + "specification.txt")
        realizable = controller_generated

    except SynthesisException as e:
        if e.os_not_supported:
            print("Os not supported for synthesis. Only linux can run strix")
        elif e.trivial:
            print("The assumptions are not satisfiable. The controller is trivial.")
            raise Exception("Assumptions unsatisfiable in a CGT is impossible.")

    return realizable, exec_time


def generate_controllers_from_cgt_clustered(cgt: CGTGoal, folder_path, complete):
    realizables = []
    exec_times = []
    """Synthetize the controller for the branches of the CGT"""
    print("\n\nSynthetize the controller for the branches of the CGT composing it with the new context")
    for i, goal in enumerate(cgt.refined_by):
        from helper.buchi import generate_buchi
        sub_folder_path = folder_path + "cluster_" + str(i) + "/"
        generate_buchi(OrLTL(goal.context), sub_folder_path + "context")
        realizable, exec_time = generate_controller_from_cgt(goal, sub_folder_path, complete)
        realizables.append(realizable)
        exec_times.append(exec_time)

    return realizables, exec_times


def run(list_of_goals: List[CGTGoal], result_folder: str,
        general_and=False,
        general_or=False,
        no_clusters=False,
        clusters_origianl=False,
        clusters_mutex=False,
        complete=True):
    """Print List of Goals"""
    for g in list_of_goals:
        print(g)

    controller_generated_and = False
    trivial_and = False
    controller_generated_or = False
    trivial_or = False
    realizable_no_clusters = False
    no_clusters_exec_time = 0.0
    realizables_clustered = []
    exec_times_clustered = []
    realizables_original = []
    exec_times_original = []

    goals_res = ""
    for g in list_of_goals:
        """Generate controller from goals as is, where the assumptions are in AND"""
        controller, trivial, exec_time = create_general_controller_from_goals([g],
                                                                              result_folder + "/goal_list/" + g.name + "/",
                                                                              "AND")
        if controller:
            goals_res += g.name + "\t" + "YES\t" + format(exec_time, '.3f') + "sec\n"
        else:
            goals_res += g.name + "\t" + "NO\t" + format(exec_time, '.3f') + "sec\n"


    summary_file_name = result_folder + "/SUMMARY.txt"
    dirname = os.path.dirname(summary_file_name)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    with open(summary_file_name, 'w') as f:
        f.write(pretty_print_goals(ap, rules, goals))
        f.write("\nREALIZABILITY OF INDIVIDUAL GOALS\n" + goals_res)
    f.close()


    if general_and:
        """Generate controller from goals as is, where the assumptions are in AND"""
        controller_generated_and, trivial_and, exec_time_and = create_general_controller_from_goals(list_of_goals,
                                                                                                    result_folder + "/general_with_and/",
                                                                                                    "AND")

        ret = "\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
        ret += "GENERAL SPECIFICATION WITH ALL GAOLS: **AND** OF ASSUMPTIONS **AND** OF GUARANTEES\n"
        ret += "-->\t" + str(len(list_of_goals)) + " goals: " + str([c.name for c in list_of_goals]) + "\n"
        if controller_generated_and:
            ret += "REALIZABLE\tYES\t\t" + format(exec_time_and, '.3f') + "sec\n"
        else:
            ret += "REALIZABLE\tNO\t\t" + format(exec_time_and, '.3f') + "sec\n"
        if trivial_and:
            ret += "TRIVIAL\tYES\t\t\n"
        else:
            ret += "TRIVIAL\tNO\t\t\n"
        ret += "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n"
        f = open(summary_file_name, "a+")
        f.write(ret)
        f.close()

    if general_or:
        """Generate controller from goals as is, where the assumptions are in OR"""
        controller_generated_or, trivial_or, exec_time_or = create_general_controller_from_goals(list_of_goals,
                                                                                                 result_folder + "/general_with_or/",
                                                                                                 "OR")
        ret = "\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
        ret += "GENERAL SPECIFICATION WITH ALL GAOLS: **OR** OF ASSUMPTIONS **AND** OF GUARANTEES\n"
        ret += "-->\t" + str(len(list_of_goals)) + " goals: " + str([c.name for c in list_of_goals]) + "\n"
        if controller_generated_and:
            ret += "REALIZABLE\tYES\t\t" + format(exec_time_or, '.3f') + "sec\n"
        else:
            ret += "REALIZABLE\tNO\t\t" + format(exec_time_or, '.3f') + "sec\n"
        if trivial_and:
            ret += "TRIVIAL\tYES\t\t\n"
        else:
            ret += "TRIVIAL\tNO\t\t\n"
        ret += "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n"
        f = open(summary_file_name, "a+")
        f.write(ret)
        f.close()

    if no_clusters:
        """No Clustering, Conjunction of all the goals (with saturated G = A->G)"""
        try:
            cgt = conjunction(deepcopy(list_of_goals))
        except CGTFailException as e:
            print(pretty_cgt_exception(e))
            sys.exit()
        save_to_file(str(cgt), result_folder + "/cgt_no_clusters/CGT.txt")

        """Generate a controller from cgt root"""
        realizable_no_clusters, no_clusters_exec_time = generate_controller_from_cgt(cgt,
                                                                                     result_folder + "/cgt_no_clusters/", complete)

        ret = "\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
        ret += "CGT WITH CONJUNCTION OF GOALS\n"
        ret += "-->\t" + str(len(list_of_goals)) + " goals: " + str([c.name for c in list_of_goals]) + "\n"
        if realizable_no_clusters:
            ret += "REALIZABLE\tYES\t\t" + format(no_clusters_exec_time, '.3f') + "sec\n"
        else:
            ret += "REALIZABLE\tNO\t\t" + format(no_clusters_exec_time, '.3f') + "sec\n"
        ret += "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n"
        f = open(summary_file_name, "a+")
        f.write(ret)
        f.close()

    """Clustering"""
    """Create cgt with the goals, it will automatically compose/conjoin them based on the context"""
    context_goals = create_contextual_clusters(list_of_goals, "MUTEX", rules["context"])

    if clusters_mutex:
        """Create the CGT composing the goals with the context"""
        try:
            cgt_1 = create_cgt(context_goals, compose_with_context=True)
        except CGTFailException as e:
            print(pretty_cgt_exception(e))
            sys.exit()
        save_to_file(str(cgt_1), result_folder + "/cgt_clusters_mutex/CGT.txt")

        """Generate a controller for each branch of the CGT"""
        realizables_clustered, exec_times_clustered = generate_controllers_from_cgt_clustered(cgt_1,
                                                                                              result_folder + "/cgt_clusters_mutex/", complete)

        ret = "\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
        ret += "CGT WITH MUTEX CLUSTERS \t  " + str(sum(realizables_clustered)) + "/" + str(
            len(realizables_clustered)) + " REALIZABLE \n"
        cluster_goals = cgt_1.refined_by
        ret += "FEASIBLE CLUSTERS:\t " + str(len(cluster_goals)) + "/" + str(len(context_goals.keys()))
        for i, goal in enumerate(cluster_goals):
            ret += "\nCLUSTER " + str(i) + "\n"
            ret += "SCENARIO:\t" + str(OrLTL(goal.context).formula) + "\n-->\t" + str(
                len(goal.refined_by)) + " goals: " + str(
                [g.name for g in goal.refined_by]) + "\n"
            if len(realizables_clustered) > 0:
                if realizables_clustered[i]:
                    ret += "REALIZABLE\tMUTEX    \tYES\t\t" + format(exec_times_clustered[i], '.3f') + "sec\n"
                else:
                    ret += "REALIZABLE\tMUTEX    \tNO\t\t" + format(exec_times_clustered[i], '.3f') + "sec\n"
        ret += "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n"

        f = open(summary_file_name, "a+")
        f.write(ret)
        f.close()

    if clusters_origianl:
        """Create the CGT composing the goals without the context"""
        try:
            cgt_2 = create_cgt(context_goals, compose_with_context=False)
        except CGTFailException as e:
            print(pretty_cgt_exception(e))
            sys.exit()

        save_to_file(str(cgt_2), result_folder + "/cgt_clusters_original/CGT.txt")

        realizables_original, exec_times_original = generate_controllers_from_cgt_clustered(cgt_2,
                                                                                            result_folder + "/cgt_clusters_original/", complete)

        unrealizable_goals = {}

        ret = "\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
        ret += "CGT WITH CLUSTERS \t" + str(sum(realizables_original)) + "/" + str(
            len(realizables_original)) + " REALIZABLE\n"
        original_goals = cgt_2.refined_by
        ret += "FEASIBLE CLUSTERS:\t " + str(len(original_goals)) + "/" + str(len(context_goals.keys()))
        for i, goal in enumerate(original_goals):
            ret += "\nCLUSTER " + str(i) + "\n"
            ret += "SCENARIO:\t" + str(OrLTL(goal.context).formula) + "\n-->\t" + str(
                len(goal.refined_by)) + " goals: " + str(
                [g.name for g in goal.refined_by]) + "\n"
            if len(realizables_original) > 0:
                if realizables_original[i]:
                    ret += "REALIZABLE \tYES\t\t" + format(exec_times_original[i], '.3f') + "sec\n"
                else:
                    ret += "REALIZABLE \tNO\t\t" + format(exec_times_original[i], '.3f') + "sec\n"
                    for g_name in [g.name for g in goal.refined_by]:
                        if g_name in unrealizable_goals.keys():
                            unrealizable_goals[g_name] += 1
                        else:
                            unrealizable_goals[g_name] = 1
        ret += "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n"

        ret += "\n~~~~~~~~~~'UNSAT-CORE' -  UNREALIZABLE GOALS~~~~~~~~~~~~~~~~\n"
        sorted_unrealizable_goals = sorted(unrealizable_goals.items(), key=lambda x: x[1], reverse=True)
        for (g, v) in sorted_unrealizable_goals:
            ret += g + "\t" + str(v) + "\n"
        ret += "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n"
        f = open(summary_file_name, "a+")
        f.write(ret)
        f.close()



    # save_to_file(pretty_print_summary_clustering(list_of_goals,
    #                                              controller_generated_and,
    #                                              trivial_and,
    #                                              controller_generated_or,
    #                                              trivial_or,
    #                                              realizable_no_clusters,
    #                                              context_goals,
    #                                              realizables_clustered,
    #                                              realizables_original),
    #              result_folder + "/SUMMARY.txt")

    print("\nClustering process finished. Results generated.")

    return realizable_no_clusters, realizables_clustered, realizables_original, no_clusters_exec_time, exec_times_clustered, exec_times_original


if __name__ == "__main__":
    realizable_no_clusters, realizables_clustered, realizables_original, no_clusters_exec_time, exec_times_clustered, exec_times_original = run(
        list_of_goals=goals,
        result_folder=results_path,
        general_and=False,
        general_or=False,
        no_clusters=True,
        clusters_origianl=True,
        clusters_mutex=False,
        complete=False)

    crealizable_no_clusters, crealizables_clustered, crealizables_original, cno_clusters_exec_time, cexec_times_clustered, cexec_times_original = run(
        list_of_goals=goals,
        result_folder=results_path + "/complete",
        general_and=False,
        general_or=False,
        no_clusters=True,
        clusters_origianl=True,
        clusters_mutex=False,
        complete=True)
