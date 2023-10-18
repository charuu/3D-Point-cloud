#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include<math.h>
#include"../base/util.h"
#include"flann/flann.h"
void write_results(const char* filename, int *data, int rows, int cols)
{
	FILE* fout;
	int* p;
	int i,j;

    fout = fopen(filename,"w");
    if (!fout) {
        printf("Cannot open output file.\n");
        exit(1);
    }
    
    p = data;
    for (i=0;i<rows;++i) {
        for (j=0;j<cols;++j) {
            fprintf(fout,"%d ",*p);
            p++;
        }
        fprintf(fout,"\n");
    }
    fclose(fout);
}



int main(){
    // read input downsampled file
    FILE *fp = fopen("../data/XX_after.txt", "r");
    int RANGE_MAX = 100;
 
    if (fp == NULL)
    {
        puts("Couldn't open file");
        exit(0);
    }
    int n =50000;
    int dim=3;
    char line[120];
    char* end;
    char* token;
    float val;
    float point_arr[n][3];
    int i =0;
    
    while(fgets(line,120,fp)){
        int j=0;
        token  = strtok(line, "\t");
        while(token!=NULL){
            val = strtod(token,&end);
            point_arr[i][j]=val;
            token = strtok(NULL, "\t");
            j++;
        }
        i++;
      //   printf("\n");
    }
    //for(int i=0;i<n;i++)fprintf(stderr,"%lf, %lf, %lf\n",point_arr[i][0],point_arr[i][1],point_arr[i][2]);
    struct FLANNParameters p;
   
    int* result;
	float* dists;
    float speedup;
    int nn = 3;
     int tcount = 50000;
     flann_index_t index_id;
     
    result = (int*) malloc(tcount*nn*sizeof(int));
    dists = (float*) malloc(tcount*nn*sizeof(float));

    p.algorithm = 1;
    p.trees = 8;
    p.log_level = FLANN_LOG_INFO;
    p.checks = 64;
    printf("Computing index.\n");
    index_id = flann_build_index(point_arr, tcount, 3, &speedup, &p);
    flann_find_nearest_neighbors_index(index_id, point_arr, tcount, result, dists, nn, &p);
    
    write_results("results.dat",result, tcount, nn);
    
    flann_free_index(index_id, &p);
    free(result);
    free(dists);
    
}