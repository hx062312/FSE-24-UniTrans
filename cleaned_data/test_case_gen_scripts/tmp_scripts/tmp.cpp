#include <iostream>
#include <cstdlib>
#include <string>
#include <vector>
#include <fstream>
#include <iomanip>
// #include <bits/stdc++.h>
#include <algorithm>
using namespace std;

string noAdjacentDup ( string s ) {
  int n = s . length ( );
  for ( int i = 1;
  i < n;
  i ++ ) {
    if ( s [ i ] == s [ i - 1 ] ) {
      s [ i ] = 'a';
      while ( s [ i ] == s [ i - 1 ] || ( i + 1 < n && s [ i ] == s [ i + 1 ] ) ) s [ i ] ++;
      i ++;
    }
  }
  return s;
}


int main() {

try {
string s = "abcde";
cout <<noAdjacentDup(s);
}catch(...){cout <<"exception";}




    return 0;
}
