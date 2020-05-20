import os
import shutil
import sys
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


def create_general_controller_from_goals(goals: List[CGTGoal], folder_path: str, type: str):
    assumptions = []
    guarantees = []
    inputs = set()
    outputs = set()

    for goal in goals:
        assum, guaran, ins, outs = generate_general_controller_inputs_from_goal(ap, rules, goal,
                                                                                context_rules_included=False)
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


def generate_controller_from_cgt(cgt: CGTGoal, folder_path):
    assum, guaran, ins, outs = generate_general_controller_inputs_from_goal(ap, rules, cgt)
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


def generate_controllers_from_cgt_clustered(cgt: CGTGoal, folder_path):
    realizables = []
    exec_times = []
    """Synthetize the controller for the branches of the CGT"""
    print("\n\nSynthetize the controller for the branches of the CGT composing it with the new context")
    for i, goal in enumerate(cgt.refined_by):
        from helper.buchi import generate_buchi
        sub_folder_path = folder_path + "cluster_" + str(i) + "/"
        generate_buchi(OrLTL(goal.context), sub_folder_path + "context")
        realizable, exec_time = generate_controller_from_cgt(goal, sub_folder_path)
        realizables.append(realizable)
        exec_times.append(exec_time)

    return realizables, exec_times


def run(list_of_goals: List[CGTGoal], result_folder: str,
        general_and=False,
        general_or=False,
        no_clusters=False,
        clusters_origianl=False,
        clusters_mutex=False):
    """Print List of Goals"""
    for g in list_of_goals:
        print(g)

    controller_generated_and = False
    trivial_and = False
    controller_generated_or = False
    trivial_or = False
    realizable_no_clusters = False
    realizables_clustered = []
    exec_times_clustered = []
    realizables_original = []
    exec_times_original = []

    summary_file_name = result_folder + "/SUMMARY.txt"
    dirname = os.path.dirname(summary_file_name)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    with open(summary_file_name, 'w') as f:
        f.write("SUMMARY\n\n")

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
            cgt = conjunction(list_of_goals)
        except CGTFailException as e:
            print(pretty_cgt_exception(e))
            sys.exit()
        save_to_file(str(cgt), result_folder + "/cgt_no_clusters/CGT.txt")

        """Generate a controller from cgt root"""
        realizable_no_clusters, no_clusters_exec_time = generate_controller_from_cgt(cgt,
                                                                                     result_folder + "/cgt_no_clusters/")

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
            cgt = create_cgt(context_goals, compose_with_context=True)
        except CGTFailException as e:
            print(pretty_cgt_exception(e))
            sys.exit()
        save_to_file(str(cgt), result_folder + "/cgt_clusters_mutex/CGT.txt")

        """Generate a controller for each branch of the CGT"""
        realizables_clustered, exec_times_clustered = generate_controllers_from_cgt_clustered(cgt,
                                                                                              result_folder + "/cgt_clusters_mutex/")

    if clusters_origianl:
        """Create the CGT composing the goals without the context"""
        try:
            cgt = create_cgt(context_goals, compose_with_context=False)
        except CGTFailException as e:
            print(pretty_cgt_exception(e))
            sys.exit()

        save_to_file(str(cgt), result_folder + "/cgt_clusters_original/CGT.txt")

        realizables_original, exec_times_original = generate_controllers_from_cgt_clustered(cgt,
                                                                                            result_folder + "/cgt_clusters_original/")

    ret = "\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
    ret += "CGT WITH CLUSTERS\n"
    for i, (ctx, ctx_goals) in enumerate(context_goals.items()):
        ret += "\nCLUSTER " + str(i) + "\n"
        ret += "SCENARIO:\t" + str(ctx.formula) + "\n-->\t" + str(len(ctx_goals)) + " goals: " + str(
            [c.name for c in ctx_goals]) + "\n"
        if len(realizables_clustered) > 0:
            if realizables_clustered[i]:
                ret += "REALIZABLE\tMUTEX    \tYES\t\t" + format(exec_times_clustered[i], '.3f') + "sec\n"
            else:
                ret += "REALIZABLE\tMUTEX    \tNO\t\t" + format(exec_times_clustered[i], '.3f') + "sec\n"
        if len(realizables_original) > 0:
            if realizables_original[i]:
                ret += "REALIZABLE\tORIGINAL \tYES\t\t" + format(exec_times_original[i], '.3f') + "sec\n"
            else:
                ret += "REALIZABLE\tORIGINAL \tNO\t\t" + format(exec_times_original[i], '.3f') + "sec\n"
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

    return realizable_no_clusters, realizables_clustered, realizables_original


if __name__ == "__main__":
    realizable_no_clusters, realizables_clustered, realizables_original = run(list_of_goals=goals,
                                                                              result_folder=results_path,
                                                                              general_and=True,
                                                                              general_or=True,
                                                                              no_clusters=True,
                                                                              clusters_origianl=True,
                                                                              clusters_mutex=True)
