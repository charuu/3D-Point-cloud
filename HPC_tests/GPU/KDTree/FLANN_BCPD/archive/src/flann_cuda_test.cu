#define FLANN_USE_CUDA
#include <flann/flann.h>
#include <flann/io/hdf5.h>
#include <flann/nn/ground_truth.h>
void setup(){
 printf("Reading test data...");
        fflush(stdout);
        Matrix<float> data;
        load_from_file(data, "../datasets/cloud.h5","dataset");
}