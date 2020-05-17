import os
import shutil
import sys

from controller.synthesis import create_controller_if_exists, SynthesisException
from goals.cgtgoal import CGTGoal
from goals.helpers import generate_general_controller_from_goals, generate_controller_input_text
from goals.operations import create_contextual_clusters, create_cgt, CGTFailException, pretty_cgt_exception, \
    pretty_print_summary_clustering
from helper.tools import save_to_file

from mission_specification import get_inputs
from typescogomo.formula import OrLTL

file_path = os.path.dirname(os.path.abspath(__file__)) + "/output/results"
try:
    shutil.rmtree(file_path)
except:
    pass

sys.path.append(os.path.join(os.getcwd(), os.path.pardir))

sns, loc, act, context_rules, domain_rules, list_of_goals = get_inputs()


def create_general_specification(and_assumptions: bool):

    assum, guaran, ins, outs = generate_general_controller_from_goals(list_of_goals,
                                                                      list(sns.keys()),
                                                                      context_rules,
                                                                      domain_rules,
                                                                      include_context=True,
                                                                      and_assumptions=and_assumptions)

    if and_assumptions:
        controller_file_name = file_path + "/general_specification_AND.txt"
    else:
        controller_file_name = file_path + "/general_specification_OR.txt"


    save_to_file(generate_controller_input_text(assum, guaran, ins, outs), controller_file_name)

    controller_generated = False
    trivial = False
    try:
        controller_generated = create_controller_if_exists(controller_file_name)
    except SynthesisException as e:
        if e.os_not_supported:
            print("Os not supported for synthesis. Only linux can run strix")
        elif e.trivial:
            trivial = True
            controller_generated = True
            print("The assumptions are not satisfiable. The controller is trivial.")

    return controller_generated, trivial


def generate_controller_from_cgt(cgt: CGTGoal, folder_name):

    folder_path = file_path + "/" + folder_name + "/"
    realizables = []
    """Synthetize the controller for the branches of the CGT"""
    print("\n\nSynthetize the controller for the branches of the CGT composing it with the new context")
    for i, goals in enumerate(cgt.refined_by):
        from helper.buchi import generate_buchi

        file_name_base = folder_path + "cluster_" + str(i) + "_"

        generate_buchi(OrLTL(goals.context), file_name_base + "context")

        assum, guaran, ins, outs = generate_general_controller_from_goals(goals,
                                                                          list(sns.keys()),
                                                                          context_rules,
                                                                          domain_rules,
                                                                          include_context=False)

        save_to_file(generate_controller_input_text(assum, guaran, ins, outs),
                     file_name_base + "specification.txt")

        try:
            controller_generated = create_controller_if_exists(file_name_base + "specification.txt")
            realizables.append(controller_generated)

        except SynthesisException as e:
            if e.os_not_supported:
                print("Os not supported for synthesis. Only linux can run strix")
            elif e.trivial:
                print("The assumptions are not satisfiable. The controller is trivial.")
                raise Exception("Assumptions unsatisfiable in a CGT is impossible.")

    return realizables


if __name__ == "__main__":

    """Print List of Goals"""
    for g in list_of_goals:
        print(g)

    """Generate controller from goals as is, where the assumptions are in AND"""
    controller_generated_and, trivial_and = create_general_specification(and_assumptions=True)

    """Generate controller from goals as is, where the assumptions are in OR"""
    controller_generated_or, trivial_or = create_general_specification(and_assumptions=False)

    """Create cgt with the goals, it will automatically compose/conjoin them based on the context"""
    context_goals = create_contextual_clusters(list_of_goals, "MUTEX", context_rules)

    """Create the CGT composing the goals with the context"""
    try:
        cgt = create_cgt(context_goals, compose_with_context=True)
    except CGTFailException as e:
        print(pretty_cgt_exception(e))
        sys.exit()
    save_to_file(str(cgt), file_path + "/CGT_clustered.txt")

    """Generate a controller for each branch of the CGT"""
    realizables_clustered = generate_controller_from_cgt(cgt, "clustered")

    """Create the CGT composing the goals without the context"""
    try:
        cgt = create_cgt(context_goals, compose_with_context=False)
    except CGTFailException as e:
        print(pretty_cgt_exception(e))
        sys.exit()

    save_to_file(str(cgt), file_path + "/CGT_original.txt")

    realizables_original = generate_controller_from_cgt(cgt, "original")

    save_to_file(pretty_print_summary_clustering(list_of_goals,
                                                 controller_generated_and,
                                                 trivial_and,
                                                 controller_generated_or,
                                                 trivial_or,
                                                 context_goals,
                                                 realizables_clustered,
                                                 realizables_original),
                 file_path + "/SUMMARY.txt")

    print("\nClustering process finished. Results generated.")
