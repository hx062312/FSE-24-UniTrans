#include <iostream>
#include <cstdlib>
#include <string>
#include <vector>
#include <fstream>
#include <iomanip>
using namespace std;

int addOne ( int x ) {
  int m = 1;
  while ( x & m ) {
    x = x ^ m;
    m <<= 1;
  }
  x = x ^ m;
  return x;
}


int main() {

try {
int x = -5;
cout <<addOne(x);
}catch(...){cout <<"exception";}




    return 0;
}
