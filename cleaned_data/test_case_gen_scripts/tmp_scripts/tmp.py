import math
import collections
import heapq
import sys
import random
import itertools
from math import sqrt, radians, sin, cos, asin, floor
from collections import defaultdict
import numpy as np
import array
import traceback

def isPower(x, y):
    if x == 1:
        return y == 1
    pow = 1
    while pow < y:
        pow *= x
    return pow == y


if __name__ == '__main__':
    try:
        exp_out = 1

        x = 5

        y = 125

        act_out = isPower(x = 5,y = 125)

        if isinstance(exp_out, float) or isinstance(act_out, float):
            if abs(exp_out - act_out) < 1e-3:
                print("\nOK\n")
            else:
                print(f"Expected Output:{exp_out}\nActual Output:{act_out}\nExpected output and actual output are not equal!")
        else:
            if exp_out == act_out:
                print("\nOK\n")
            else:
                print(f"Expected Output:{exp_out}\nActual Output:{act_out}\nExpected output and actual output are not equal!")
    except Exception as e:
        print(f"Runtime Error:\n{traceback.format_exc()}")
