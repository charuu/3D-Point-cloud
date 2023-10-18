
#include <stdio.h>


void __global__ print()
{
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    printf("I am in GPU");
}

extern "C" void f()
{
    print<<<1, 10>>>();
    cudaDeviceSynchronize();
     return;
}
