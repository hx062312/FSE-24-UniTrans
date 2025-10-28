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

def gcd ( a , b ) :
    if a == 0 :
        return b
    return gcd ( b % a , a )

if __name__ == '__main__':
    try:
        a = 17

        b = 13

        print(repr(gcd(a = 17,b = 13)))

    except Exception as e:
        print("exception")
