#include <stdio.h>
#include <omp.h>
#include <stdlib.h>
#include <getopt.h>
#include <time.h>
#define GET_RAND (float)rand()/1000000000
#include <sys/time.h>

double create_matrix_from_random( double (&x)[], double (&y)[],int size){
  double sum;

  int t=0;

  #pragma omp target teams has_device_addr(x,y) map(tofrom:sum,a,gridDim,blockDim)\
  shared(x,y,size,sum) thread_limit(2048)
  {
  int i,j,k;
  //gridDim = omp_get_num_teams();
  //a[omp_get_team_num()]=1;
   #pragma omp loop\
   private(i,j,k)
   for (i = 0; i < size; i++) {
    
      #pragma omp simd
        for (j = 0; j < size; ++j) {
          
            #pragma omp atomic
            sum +=  x[i * size + j] * y[j * size + i];
        }  
      } 
     
  }
  //for (int i = 0; i < 60; ++i)  printf("team :%d, %d, %d\t",a[i],gridDim,blockDim);
  return sum;
}



int main ( int argc, char *argv[] ){
    const char* str = argv[1];
    int size=atoi(str);
    printf("Size :%d \n",size);
   
    double *l = (double*)omp_target_alloc (size*size*sizeof(double), 0);
    double *u = (double*)omp_target_alloc (size*size*sizeof(double), 0);
  

    #pragma omp target is_device_ptr(l,u)
    {
      int i,j,k;
     // int size=32;
        for (i = 0; i < size*size; i++) {
                l[i] = 2;
        }

        for (i = 0; i < size*size; i++) {
                u[i] = 2;
              
        }
    } 
    
    double (&x)[size*size] = *static_cast<double(*)[size*size]>(static_cast<void*>(l));
    double (&y)[size*size] = *static_cast<double(*)[size*size]>(static_cast<void*>(u));

    double sum=0;
    sum=create_matrix_from_random(x,y,size);
    printf("SUM:%lf\n",sum);
    omp_target_free(l, 0);
    omp_target_free(u, 0);

    return 0;
}