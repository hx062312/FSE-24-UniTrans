#include <iostream>
#include <cstdlib>
#include <string>
#include <vector>
#include <fstream>
#include <iomanip>
// #include <bits/stdc++.h>
#include <algorithm>
using namespace std;

bool isPower ( int x, int y ) {
  if ( x == 1 ) return ( y == 1 );
  long int pow = 1;
  while ( pow < y ) pow *= x;
  return ( pow == y );
}


int main() {

try {
int x = 2;
int y = 1;
cout <<isPower(x,y);
}catch(...){cout <<"exception";}




    return 0;
}
