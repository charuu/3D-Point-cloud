  /*const int threadIdx = omp_get_thread_num();
   int blockDim = omp_get_num_threads();
  const int blockIdx = omp_get_team_num();
   int gridDim=omp_get_num_teams();
   **/
#include <stdio.h>
#include <omp.h>
#include <stdlib.h>
#include <getopt.h>
#include <time.h>

#define GET_RAND (float)rand()/1000000000
#include <sys/time.h>


  int main ( int argc, char *argv[] ){
    const char* str = argv[1];
    int size=atoi(str);
    printf("Size :%d \n",size);
    
    int *d_a;
    kernel_wrapper(d_a);
    #pragma omp target data use_device_ptr(d_a)
    for(int i=0;i<256;i++){
        d_a[i]=2;
    }
    return 0;
}