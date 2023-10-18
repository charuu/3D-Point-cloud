#include "include/add.h"
#include<cuda.h>
#include <stdio.h>
#include <cuda_runtime.h>
void sum(float a, float b){
float f_a,f_b;
float sum;
f_a=9.0;
f_b=10.0;
double duration;
int N = 10000000;
/**
 * simple add
 * */
for(int i=0;i<N;i++){
sum = f_a + f_b;
}
printf("%f \n",sum);
}

extern "C" void call_cuda(){
    sum(4.0,5.0);
    printf("%s\n","cuda call");
}