import itertools
import os
import shutil
import sys

from goals.operations import create_contextual_clusters, create_cgt, CGTFailException, pretty_cgt_exception, \
    pretty_print_summary_clustering, conjunction
from helper.tools import save_to_file

from mission_specification import get_inputs
from run_clustering import run

results_path = os.path.dirname(os.path.abspath(__file__)) + "/output/results"
try:
    shutil.rmtree(results_path)
except:
    pass

sys.path.append(os.path.join(os.getcwd(), os.path.pardir))

ap, rules, goals = get_inputs()

if __name__ == "__main__":

    """Print List of Goals"""
    for g in goals:
        print(g)

    print("Generating all combinations of goals")

    summary_file_name = results_path + "/SUMMARY_COMBINATIONS.txt"
    dirname = os.path.dirname(summary_file_name)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    with open(summary_file_name, 'w') as f:
        f.write("SUMMARY OF COMBINATIONS \n\n")

    f.close()

    if len(goals) > 1:
        for i in range(1, len(goals)):
            for j, subset in enumerate(itertools.combinations(goals, i)):
                rnc, rcc, rco, t1, t2, t3 = run(list(subset),
                                                results_path + "/comb_" + str(i) + "_" + str(j),
                                                no_clusters=True,
                                                clusters_origianl=True,
                                                clusters_mutex=True)
                f = open(summary_file_name, "a+")
                f.write("COMBINATION " + str(i) + "-" + str(j) + "\n")
                f.write("GOALS             :\t" + str([g.name for g in subset]) + "\n")
                if rnc:
                    f.write("RLSB_NO_CLUSTERS      :\tYES" + "\t\t" + format(t1, '.3f') + "sec\n")
                else:
                    f.write("RLSB_NO_CLUSTERS      :\tNO" + "\t\t" + format(t1, '.3f') + "sec\n")
                f.write("RLSB_CLUSTERS_1   :\t" + str(sum(rcc)) + " / " + str(len(rcc)) + "\t\t" + format(sum(t2),
                                                                                                          '.3f') + "sec\n")
                f.write("RLSB_CLUSTERS_2   :\t" + str(sum(rco)) + " / " + str(len(rco)) + "\t\t" + format(sum(t3),
                                                                                                          '.3f') + "sec\n")
                f.write("\n\n")
                f.close()
    else:
        rnc, rcc, rco, t1, t2, t3 = run(goals,
                                        "comb_1",
                                        no_clusters=True,
                                        clusters_origianl=True,
                                        clusters_mutex=True)
        f = open(summary_file_name, "a+")
        f.write("GOAL              :\t" + str([g.name for g in goals]) + "\n")
        if rnc:
            f.write("RLSB_GENERAL      :\tYES" + "\t\t" + format(t1, '.3f') + "sec\n")
        else:
            f.write("RLSB_GENERAL      :\tNO" + "\t\t" + format(t1, '.3f') + "sec\n")
        f.write(
            "RLSB_CLUSTERS_1   :\t" + str(sum(rcc)) + " / " + str(len(rcc)) + "\t\t" + format(sum(t2), '.3f') + "sec\n")
        f.write(
            "RLSB_CLUSTERS_2   :\t" + str(sum(rco)) + " / " + str(len(rco)) + "\t\t" + format(sum(t3), '.3f') + "sec\n")
        f.write("\n\n")
        f.close()
