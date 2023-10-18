#ifndef __B_H_

#define __B_H_

#include <stdio.h>

#include <stdlib.h>

#include <string.h>

#include <cuda.h>

#include <cuda_runtime.h>

#endif

extern void kernel_wrapper(int *a);

int main(int argc, char *argv[])

{

    int *a = (int *)malloc(sizeof(int) * 2);

    a[0] = 2;

    a[1] = 3;

    

    printf( "a[0]: %d, a[1]: %d\n", a[0], a[1] );
    
    kernel_wrapper(a);

    printf( "a[0]: %d, a[1]: %d\n", a[0], a[1] );

   free(a);

    return 0;

}