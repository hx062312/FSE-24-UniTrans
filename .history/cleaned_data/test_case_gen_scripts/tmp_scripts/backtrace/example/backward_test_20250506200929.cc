#include "../backtrace_service.h"
#include <iostream>
#include <thread>
#include <vector>
#include <memory>
#include <sys/types.h>
#include <unistd.h>
#include <dirent.h>
#include <iostream>
#include <cstdlib>
#include <string>
#include <vector>
#include <fstream>
#include <iomanip>
// #include <bits/stdc++.h>
#include <algorithm>
using namespace std;
namespace
{
int addOne(int x) {
    int m = 1;
    while (x & m) {
        x = x ^ m;
        m <<= 1;
    }
    x = x ^ m;
    return x;
}

};

int main(void)
{
        int x=0;

        int act_out = addOne(x);

	int exp_out = 1;

	if(act_out == exp_out) cout << "OK";

	else {
cout << "Expected Output:1\nActual Output:";
cout << act_out;
cout << "\nExpected output and actual output are not equal!";}

    return 0;
}
