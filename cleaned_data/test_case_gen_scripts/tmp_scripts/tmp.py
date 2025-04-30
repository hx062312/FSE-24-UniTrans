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

def addOne ( x ) :
    m = 1
    while ( x & m ) :
        x = x ^ m
        m <<= 1
    x = x ^ m
    return x

if __name__ == '__main__':
    try:
        print(repr(addOne(15)))

    except Exception as e:
        print("exception")
