#include <stdio.h>
#include <omp.h>
#include <stdlib.h>
#include <getopt.h>
#include <time.h>
#define GET_RAND (float)rand()/1000000000
#include <sys/time.h>

double create_matrix_from_random( double (&x)[], double (&y)[],int size){
   double global_sum;
   int total_no_of_tiles;
  #pragma omp target teams has_device_addr(x,y) map(tofrom:global_sum)\
  num_teams(60) thread_limit(1024) shared(x,y,size,global_sum) 
  {
  int BS=16;
  int i,j,k,l,m;
  int tile_no;
  double sum;
  int tile_per_row=size/BS;
  int total_no_of_tiles = tile_per_row *tile_per_row;
  double tile_l[BS*BS],tile_r[BS*BS];


  #pragma omp distribute \
  private(tile_no) 
  for( tile_no=0; tile_no < total_no_of_tiles; tile_no++){
     
    int row = (tile_no)/tile_per_row;
    int col= (tile_no%tile_per_row);

     // filling up tile from global memory
     #pragma omp parallel for \
     private(l,m)
     for(l=0;l<BS;l++){
        #pragma omp simd 
        for(m=0;m<BS;m++){
          tile_l[BS*l + m]  =x[row*BS*size+ BS*col + size*l + m];
          tile_r[BS*l + m]  =y[col*BS*size+ BS*row + size*m + l];
       //   printf("%d,%d\n",row*BS*size+ BS*col + size*l + m,col*BS*size+ BS*row + size*m + l);        
        } 
     }

      #pragma omp parallel for\
      private(sum,i,j,k)shared(tile_l,tile_r)
      for (i = 0; i < BS; i++) { 
        double sum=0;
      #pragma omp simd
        for ( j=0; j < BS; j++) {
           #pragma omp atomic
              sum+= tile_l[BS*i + j] * tile_r[BS*j + i];
            
          }
          #pragma omp atomic
            global_sum+=sum;
      }
      }
  }
  
  return global_sum;
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