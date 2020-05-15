import os
import shutil
import sys

from controller.synthesis import create_controller_if_exists
from goals.helpers import generate_general_controller_from_goals, generate_controller_input_text
from goals.operations import create_contextual_clusters, create_cgt, CGTFailException, pretty_cgt_exception, \
    pretty_print_summary_clustering
from helper.tools import save_to_file

from input_clustering import get_inputs
from typescogomo.formula import OrLTL

file_path = os.path.dirname(os.path.abspath(__file__)) + "/output/results"
try:
    shutil.rmtree(file_path)
except:
    pass

sys.path.append(os.path.join(os.getcwd(), os.path.pardir))

if __name__ == "__main__":

    sns, loc, act, context_rules, domain_rules, list_of_goals = get_inputs()

    for g in list_of_goals:
        print(g)

    assum, guaran, ins, outs = generate_general_controller_from_goals(list_of_goals,
                                                                      list(sns.keys()),
                                                                      context_rules,
                                                                      domain_rules,
                                                                      include_context=True)

    file_name_base = file_path + "/general_"

    controller_file_name = file_name_base + "specification.txt"

    save_to_file(generate_controller_input_text(assum, guaran, ins, outs), controller_file_name)

    controller_general = create_controller_if_exists(controller_file_name)

    """Create cgt with the goals, it will automatically compose/conjoin them based on the context"""
    context_goals = create_contextual_clusters(list_of_goals, "MUTEX", context_rules)
    realizables = []

    """Create the CGT"""
    try:
        cgt = create_cgt(context_goals)
    except CGTFailException as e:
        print(pretty_cgt_exception(e))
        sys.exit()

    save_to_file(str(cgt), file_path + "/CGT.txt")

    """Synthetize the controller for the branches of the CGT"""
    for i, goal in enumerate(cgt.refined_by):
        from helper.buchi import generate_buchi

        file_name_base = file_path + "/cluster_" + str(i) + "_"

        generate_buchi(OrLTL(goal.context), file_name_base + "context")

        assum, guaran, ins, outs = generate_general_controller_from_goals(goal,
                                                                          list(sns.keys()),
                                                                          context_rules,
                                                                          domain_rules,
                                                                          include_context=False)

        save_to_file(generate_controller_input_text(assum, guaran, ins, outs), file_name_base + "specification.txt")

        controller_generated = create_controller_if_exists(file_name_base + "specification.txt")
        realizables.append(controller_generated)

    save_to_file(pretty_print_summary_clustering(list_of_goals, controller_general, context_goals, realizables),
                 file_path + "/SUMMARY.txt")

    print("\nClustering process finished. Results generated.")
