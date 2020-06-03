from src.typescogomo.formula import LTL
from src.typescogomo.variables import *


if __name__ == '__main__':
    a = LTL("G(g -> F e)")
    b = LTL("G(e)")
    a &= b
    c = a & b
    print(a)
    print(c)