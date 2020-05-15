import os
import shutil
import sys

from controller.synthesis import create_controller_if_exists
from goals.helpers import generate_controller_inputs_from, generate_controller_input_text
from goals.operations import create_contextual_clusters, create_cgt, CGTFailException, pretty_cgt_exception, \
    pretty_print_summary_clustering
from helper.tools import save_to_file

try:
    from clustering_mission_custom import get_inputs
except:
    from clustering_mission_default import get_inputs

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

    ctx, dom, gs, unc, cont = generate_controller_inputs_from(list_of_goals, list(sns.keys()), context_rules,
                                                              domain_rules)

    file_name_base = file_path + "/general_"

    controller_file_name = file_name_base + "specification.txt"

    save_to_file(generate_controller_input_text(ctx, dom, gs, unc, cont), controller_file_name)

    controller_general = create_controller_if_exists(controller_file_name)

    """Create cgt with the goals, it will automatically compose/conjoin them based on the context"""
    context_goals = create_contextual_clusters(list_of_goals, "MUTEX", context_rules)
    realizables = []

    for i, (ctx, ctx_goals) in enumerate(context_goals.items()):
        from helper.buchi import generate_buchi

        file_name_base = file_path + "/cluster_" + str(i) + "_"

        generate_buchi(ctx, file_name_base + "context")

        ctx, dom, gs, unc, cont = generate_controller_inputs_from(ctx_goals, list(sns.keys()), context_rules,
                                                                  domain_rules, ctx)
        save_to_file(generate_controller_input_text(ctx, dom, gs, unc, cont), file_name_base + "specification.txt")

        controller_generated = create_controller_if_exists(file_name_base + "specification.txt")
        realizables.append(controller_generated)

    save_to_file(pretty_print_summary_clustering(list_of_goals, controller_general, context_goals, realizables), file_path + "/SUMMARY.txt")

    try:
        cgt = create_cgt(context_goals)
    except CGTFailException as e:
        print(pretty_cgt_exception(e))
        sys.exit()

    save_to_file(str(cgt), file_path + "/CGT.txt")

    print("\nClustering process finished. Results generated.")
