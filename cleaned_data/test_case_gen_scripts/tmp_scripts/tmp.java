import java.util.*;
import java.util.stream.*;
import java.lang.*;

public class BASIC_AND_EXTENDED_EUCLIDEAN_ALGORITHMS {

static int gcd(int a, int b) {
    if (a == 0) {
        return b;
    }
    return gcd(b % a, a);
}


    public static void main(String args[]) {
        try {

            int exp_out = 1;

            int a = 17;

            int b = 13;

            int act_out = gcd(a,b);

            if(act_out == exp_out) System.out.println("OK");

            else {
System.out.print("Expected Output:1\nActual Output:");
System.out.print(act_out);
System.out.print("\nExpected output and actual output are not equal!");}

        } catch (Exception e) {
            System.out.print("Runtime Error:");
            e.printStackTrace();
        }
    }
}
