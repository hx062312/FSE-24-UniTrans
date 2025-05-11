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

def largestSumOfAverages(A, K):
    n = len(A)
    pre_sum = [0.0] * (n + 1)
    for i in range(n):
        pre_sum[i + 1] = pre_sum[i] + A[i]
    dp = [[0.0] * n for _ in range(K)]
    for i in range(n):
        dp[0][i] = (pre_sum[n] - pre_sum[i]) / (n - i)
    for k in range(1, K):
        for i in range(n):
            for j in range(i + 1, n):
                dp[k][i] = max(dp[k][i], (pre_sum[j] - pre_sum[i]) / (j - i) + dp[k - 1][j])
    return dp[K - 1][0]


if __name__ == '__main__':
    try:
        exp_out = 20.0

        A = {9, 1, 2, 3, 9}

        K = 3

        act_out = largestSumOfAverages(A = {9, 1, 2, 3, 9},K = 3)

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
