#include<stdio.h>
#include <omp.h>
#include <math.h>
#include <stdlib.h>
int main(){
    printf("Testing max reduciton using openmp threading\n");
    int D=3;
    int sd=sizeof(double);
    double* max=calloc(D,sd); 
    //double* max0=(double*)omp_target_alloc(D*sd,0);
    //omp_target_associate_ptr(max, max0, D*sizeof(double), sizeof(double), 0);
    double max_val=0;
    int MAX_THREADS=1024;
    double* cache=calloc(MAX_THREADS,sd);
   double* cache0=(double*)omp_target_alloc(MAX_THREADS*sd,0);
  omp_target_associate_ptr(cache, cache0, MAX_THREADS*sizeof(double), sizeof(double), 0);
    //#pragma omp target data map(alloc:cache0)
    #pragma omp target teams num_teams(60) thread_limit(1024) is_device_ptr(cache0)
    {
        double arr[]={1,2,3,4,5,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,220,200003,24,25,26,27,28,2900,30,31,32,100,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,1700,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32};
        int gridDim = omp_get_num_teams();
        int blockIdx= omp_get_team_num();
        double cache[1024];
        
        int N= 64;
        printf(" Grid dimensions %d \n" , gridDim);
        #pragma omp parallel shared(cache) shared(arr) num_threads(1024)
        {
            int blockDim= omp_get_num_threads();
            int threadIdx= omp_get_thread_num();
            int stride = blockDim*gridDim ;
            int unique_id =    blockDim*blockIdx + threadIdx;
            int offset=0;
            double temp = -1.0;
            while(unique_id + offset < N){
                    temp = fmax(temp, arr[unique_id + offset]);
                    offset += stride;
            }

            cache[threadIdx] = temp;
            
            #pragma omp barrier


            // reduction
            unsigned int i = blockDim/2;
            while(i != 0){
            if(threadIdx < i){
                cache[threadIdx] = fmax(cache[threadIdx], cache[threadIdx + i]);
            }
            printf("%d: %lf \n",i,cache[threadIdx]  );
            #pragma omp barrier
            i /= 2;
            }
 
            if(threadIdx == 0){
           #pragma omp critical
            cache0[0] = fmax(cache0[0], cache[0]);
            
            }
        }
    }

    
     omp_target_memcpy(cache, cache0, MAX_THREADS*sizeof(double), 0,0, 1, 0);
    for(int i =0;i<56;i++)fprintf(stderr,"%lf\n",cache[i]);

   // omp_target_free(cache0,0);
   // omp_target_free(X0,0);
}