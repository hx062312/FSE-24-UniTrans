static double largestSumOfAverages(int[] A, int K) {
    int n = A.length;
    double[] pre_sum = new double[n + 1];
    pre_sum[0] = 0;
    for (int i = 0; i < n; i++)
        pre_sum[i + 1] = pre_sum[i] + A[i];
    
    double[] dp = new double[n];
    for (int i = 0; i < n; i++)
        dp[i] = (pre_sum[n] - pre_sum[i]) / (n - i);
    
    for (int k = 0; k < K - 1; k++)
        for (int i = 0; i < n; i++)
            for (int j = i + 1; j < n; j++)
                dp[i] = Math.max(dp[i], (pre_sum[j] - pre_sum[i]) / (j - i) + dp[j]);
    
    return dp[0];
}

def largestSumOfAverages(A, K):
    n = len(A)
    pre_sum = [0.0] * (n + 1)
    for i in range(n):
        pre_sum[i + 1] = pre_sum[i] + A[i] #<Buggy Line>
    dp = [0.0] * n
    for i in range(n):
        dp[i] = (pre_sum[n] - pre_sum[i]) / (n - i)
    for k in range(K - 1):
        for i in range(n):
            for j in range(i + 1, n):
                dp[i] = max(dp[i], (pre_sum[j] - pre_sum[i]) / (j - i) + dp[j])
    return dp[0]

def largestSumOfAverages(A, K):
    n = len(A)
    A = list(A)
    pre_sum = [0.0] * (n + 1)
    for i in range(n):
        pre_sum[i + 1] = pre_sum[i] + A[i]
    dp = [0.0] * n
    for i in range(n):
        dp[i] = (pre_sum[n] - pre_sum[i]) / (n - i)
    for k in range(K - 1):
        for i in range(n):
            for j in range(i + 1, n):
                dp[i] = max(dp[i], (pre_sum[j] - pre_sum[i]) / (j - i) + dp[j])
    return dp[0]