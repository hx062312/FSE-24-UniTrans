#include <iostream>
#include <cstdlib>
#include <string>
#include <vector>
#include <fstream>
#include <iomanip>
// #include <bits/stdc++.h>
#include <algorithm>
using namespace std;

int addOne(int x){
    return -(~x);
}


int main()
{
    try
    {

        int exp_out = -2;

        int x=-3;

        int act_out = addOne(x);

        if(act_out == exp_out) cout << "OK";

        else {
cout << "Expected Output:-2\nActual Output:";
cout << act_out;
cout << "\nExpected output and actual output are not equal!";}
    }
    catch (std::exception const &e)
    {
        std::cout << "Runtime Error:\n"
                  << e.what() << std::endl;
    }
    return 0;
}
