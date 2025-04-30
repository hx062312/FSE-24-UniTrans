import java.util.*;
import java.util.stream.*;
import java.lang.*;
public class BASIC_AND_EXTENDED_EUCLIDEAN_ALGORITHMS{


static int addOne(int x) {
    int m = 1;
    while ((x & m) != 0) {
        x = x ^ m;
        m <<= 1;
    }
    x = x ^ m;
    return x;
}


public static void main(String args[]) {
    try{

        int exp_out = 6;

        int x=5;

        int act_out = addOne(x);

        if(act_out == exp_out) System.out.println("OK");

        else {
System.out.print("Expected Output:6\nActual Output:");
System.out.print(act_out);
System.out.print("\nExpected output and actual output are not equal!");}

    }catch(Exception e){
        System.out.print("Runtime Error:");
        e.printStackTrace();
    }
}
}
