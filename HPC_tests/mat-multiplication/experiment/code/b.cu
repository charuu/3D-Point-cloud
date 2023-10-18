#ifndef __B_H_

#define __B_H_

#include <stdio.h>

#include <stdlib.h>

#include <string.h>

#include <cuda.h>

#include <cuda_runtime.h>

#endif

extern "C" void kernel_wrapper(int *a);

__global__ void kernel(int *a)

{

    int tx = threadIdx.x;

    

    switch( tx )

    {

	case 0:

     a[tx] = a[tx] + 2;

     break;

	case 1:

     a[tx] = a[tx] + 3;

     break;

    }

}

void kernel_wrapper(int *a)

{
 
    int *d_a;

    dim3 threads( 2, 1 );

    dim3 blocks( 1, 1 );

   cudaMalloc( (void **)&d_a, sizeof(int) * 2 );

   cudaMemcpy( d_a, a, sizeof(int) * 2, cudaMemcpyHostToDevice );

   kernel<<< blocks, threads >>>( d_a );

   cudaMemcpy( a, d_a, sizeof(int) * 2, cudaMemcpyDeviceToHost );

   printf( "Finish kernel wrapper\n" );

    cudaFree(d_a);

}