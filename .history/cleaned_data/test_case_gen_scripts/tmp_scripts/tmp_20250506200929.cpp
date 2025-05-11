#include <iostream>
#include <cstdlib>
#include <string>
#include <vector>
#include <fstream>
#include <iomanip>
// #include <bits/stdc++.h>
#include <algorithm>
using namespace std;

static void sortInWave(int arr[], int n) {
  for (int i = 0; i < n; i += 2) {
    if (i > 0 && arr[i - 1] > arr[i])
      swap(arr, i - 1, i);
    if (i < n - 1 && arr[i] < arr[i + 1])
      swap(arr, i, i + 1);
  }
}


int main() {

try {
int arr[] = {1};
int n = 1;
cout <<sortInWave(arr,n);
}catch(...){cout <<"exception";}




    return 0;
}
