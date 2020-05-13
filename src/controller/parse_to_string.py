import sys, os
import subprocess

from checks.tools import Implies
from parser import parse


if sys.argv[1] is None:
    raise Exception("No input file specified")


filepath = os.getcwd()

files_folder = os.path.dirname(os.path.abspath(__file__)) + "/files/"

file = files_folder + sys.argv[1]

assumptions, guarantees, ins, outs = parse(file)

params = ' -f "' + Implies(assumptions, guarantees) + '" --ins="' + ins + '" --outs="' + outs + '"'

print(params)