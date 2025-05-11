import java.util. *;
import java.util.stream.*;
import java.lang.*;
public class BASIC_AND_EXTENDED_EUCLIDEAN_ALGORITHMS{


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


public static void main(String args[]) {
    try {
int[] A = {10, 20, 30, 40, 50};
int K = 2;
System.out.println(largestSumOfAverages(A,K));
}catch(Exception e){System.out.println("exception");}


}
}
