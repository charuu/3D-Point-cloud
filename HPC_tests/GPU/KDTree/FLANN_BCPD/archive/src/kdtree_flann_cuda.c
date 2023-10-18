#define FLANN_USE_CUDA
#include <flann/flann.h>
#include <stdio.h>
#include <stdlib.h>

int main(){
    float* dataset;
	float* testset;
	int nn;
	int* result;
	float* dists;
	struct FLANNParameters p;
	float speedup;
	flann_index_t index_id;

    p = DEFAULT_FLANN_PARAMETERS;
    p.algorithm = FLANN_INDEX_KDTREE_CUDA;
    p.leaf_max_size = 8;
    p.iterations = 3;
    
    printf("Computing index.\n");

}