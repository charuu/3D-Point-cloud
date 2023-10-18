/* solving the matrix equation A*x=b using LAPACK */

#include <stdio.h>
# include <cuda.h>
#include <../cuda/include/cublas_v2.h>     // if you need CUBLAS v2, include before magma.h

# include <../magma/include/magma_v2.h>
#define size 3 /* dimension of matrix */

void dpotrf_( 	char*  , int* 	 , float*  	,int*  	,	int* );
void zfill_matrix(
    magma_int_t m, magma_int_t n, magmaDoubleComplex *A, magma_int_t lda )
{
    #define A(i_, j_) A[ (i_) + (j_)*lda ]
    
    magma_int_t i, j;
    for (j=0; j < n; ++j) {
        for (i=0; i < m; ++i) {
            A(i,j) = MAGMA_Z_MAKE( rand() / ((double) RAND_MAX),    // real part
                                   rand() / ((double) RAND_MAX) );  // imag part
        }
    }
    
    #undef A
}
void zfill_matrix_gpu(
    magma_int_t m, magma_int_t n, magmaDoubleComplex *dA, magma_int_t ldda,
    magma_queue_t queue )
{
    magmaDoubleComplex *A;
    magma_int_t lda = ldda;
    magma_zmalloc_cpu( &A, m*lda );
    if (A == NULL) {
        fprintf( stderr, "malloc failed\n" );
        return;
    }
    zfill_matrix(m, n, A, lda);
    magma_zsetmatrix(m, n, A, lda, dA, ldda, queue);
    magma_free_cpu( A );
}
int main() {
  int i, j, c1, c2, pivot[size], ok,info;
  magma_int_t K;
  float A[size][size], b[size], AT[size * size]; /* single precision!!! */
double *dA=NULL;
  A[0][0] = 3.1;
  A[0][1] = 1.3;
  A[0][2] = -5.7; /* matrix A */
  A[1][0] = 1.0;
  A[1][1] = -6.9;
  A[1][2] = 2.8;
  A[2][0] = 3.4;
  A[2][1] = 7.2;
  A[2][2] = -8.8;

  b[0] = -1.3; /* if you define b as a matrix then you */
  b[1] = -0.1; /* can solve multiple equations with */
  b[2] = 1.8;  /* the same A but different b */

  for (i = 0; i < size; i++) /* to call a Fortran routine from C we */
  {                          /* have to transform the matrix */
    for (j = 0; j < size; j++)
      AT[j + size * i] = A[j][i];
  }

  c1 = size; /* and put all numbers we want to pass */
  c2 = 1;    /* to the routine in variables */
  K=2;
  /* find solution using LAPACK routine SGESV, all the arguments have to */
  /* be pointers and you have to add an underscore to the routine name */
  //char uplo='U';
  magma_init();
  magma_int_t ldda = magma_roundup( 1000, 32 );
  int n=1000;
  
 // magma_zmalloc( &dA, ldda*n );
      magma_malloc((void**)&A,   ldda*n);
  magma_int_t *ipiv=NULL;
  magma_queue_t queue=NULL;
  magma_uplo_t uplo=MagmaUpper;
    // magma_*malloc routines for GPU memory are type-safe,
    // but you can use cudaMalloc if you prefer.
  //zfill_matrix_gpu( n, n, dA, ldda, queue );
    
  magma_int_t dev = 0; 
  magma_queue_create(dev, &queue);
  // magma_dpotrf_batched(uplo,K,AT,&K,&info);
  magma_dpotrf_batched(MagmaUpper,K,&AT,K,&info,1,queue);

  magma_queue_destroy( queue );
    magma_free( dA );
  magma_finalize();
  /*
   parameters in the order as they appear in the function call
      order of matrix A, number of right hand sides (b), matrix A,
      leading dimension of A, array that records pivoting,
      result vector b on entry, x on exit, leading dimension of b
      return value */

  for (j = 0; j < size; j++)
    printf("%e\n", b[j]); /* print vector x */
  return 0;
}