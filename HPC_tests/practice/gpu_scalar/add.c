#include<stdio.h>
#include<omp.h>
#include <time.h>
#ifdef __cplusplus
     
 extern "C" void call_cuda();
#endif


int main(){
call_cuda();
float f_a,f_b;
float sum;
f_a=9.0;
f_b=10.0;
double duration;
int N = 1000000;
double clock_start,clock_stop;
/**
 * simple add
 * */
clock_start = clock();
for(int i=0;i<N;i++){
sum = f_a + f_b;
}
clock_stop = clock();

duration = ( clock_stop - clock_start ) / CLOCKS_PER_SEC;
printf("No simd duration: %lf\n", duration);
printf("%f \n",sum);

/**
 *  add with openmp
 * */
clock_start = clock();
#pragma omp parallel for simd
for(int i=0;i<N;i++){
sum = f_a + f_b;
}
clock_stop = clock();

duration = ( clock_stop - clock_start ) / CLOCKS_PER_SEC;
printf("With simd duration: %lf\n", duration);
printf("%f \n",sum);

/**
 *  add with openmp target offloading
 * */
f_a=90.0;
f_b=10.0;
clock_start = clock();
#pragma omp target data map(tofrom:f_a,f_b,sum)
#pragma omp target teams distribute parallel for map(to:f_a,f_b) map(from:sum)
for(int i=0;i<N;i++){
sum = f_a + f_b;
}
clock_stop = clock();

duration = ( clock_stop - clock_start ) / CLOCKS_PER_SEC;
printf("With simd duration: %lf\n", duration);
printf("%f \n",sum);

/**
 * add with openmp threading
 * */
#pragma target
{
  int teams = omp_get_team_num();
  int threadx= omp_get_num_threads();
  
}



/**
 *  add with cuda
 * */
call_cuda();
}

