#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include"./base/util.h"
/***
 * Task 1:
 * Compare eballsearchnext on cpu with stubbed input file (approx 6-7 sec for one call for 50000 points)
 * with nearest neighbour on gpu with same input file (approx 8 msec for one call for 50000 points)
 * Task 2:
 * convert openmp cpu parallelization on eballsearch to paralleization on gpu
*/
//double gauss    (const double *x, const double *y, int D, double h){return exp(-dist2(x,y,D)/(2*SQ(h)));}
void kernel_wrapper(double* points_c, double* queries_c);
int* ball_tree_search_wrapper(double* points_c,int* T);
void save_variable(const char *prefix, const char *suffix,const int *var, int D, int J, char *fmt, int trans){
  int d,j; char fn[256]; double **buf;
  strcpy(fn,prefix); strcat(fn,suffix);
  if(trans==1){
    buf=calloc2d(J,D);
    for(j=0;j<J;j++)for(d=0;d<D;d++) buf[j][d]=var[d+D*j];
    write2d(fn,(const double **)buf,J,D,fmt,"NA"); free2d(buf,J);
  }
  else {
    buf=calloc2d(D,J);
    for(j=0;j<J;j++)for(d=0;d<D;d++) buf[d][j]=var[d+D*j];
    write2d(fn,(const double **)buf,D,J,fmt,"NA"); free2d(buf,D);
  }

  return;
}
int main(){
    // read input downsampled file
    FILE *fp = fopen("XX_after.txt", "r");
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
    double val;
    double point_arr[n][3];
    int i =0;
    
    while(fgets(line,120,fp)){
        int j=0;
        token  = strtok(line, "\t");
        while(token!=NULL){
            val = strtod(token,&end);
            point_arr[i][j]=val;
            //printf("%lf \t",val);
            token = strtok(NULL, "\t");
            j++;
        }
        i++;
      //   printf("\n");
    }
    for(int i=0;i<n;i++)fprintf(stderr,"%lf, %lf, %lf\n",point_arr[i][0],point_arr[i][1],point_arr[i][2]);
 //  double (*points)= point_arr;
 //  double (*queries)= point_arr;
  
  /* for(int i=0;i<50000;i++){
    for(int j=0;j<3;j++){
        printf("%lf\t",*(points+j));
    }
    points = points+3;
     printf("\n");
   }

   for(int i=0;i<50000;i++){
    for(int j=0;j<3;j++){
        printf("%lf\t",*(queries+j));
    }
    queries = queries+3;
     printf("\n");
   }
   */
  /* double arr[150000];
    for(int i=0;i<50000;i++){
        for(int j=0;j<3;j++){
            arr[j+3*i]= point_arr[i][j];
        }
    }
    int *T,*wi; double *wd;int N =50000;

    T =(int *)calloc(3*N+1,sizeof(int));
    T = ball_tree_search_wrapper(arr,T);
    printf("%s","Tree\n");
    for(int i=0;i<10;i++){
        printf("%d, %d, %d\n",T[0],T[1],T[2]);
         T = T+3;
    }
    save_variable("KD","Tree.txt",T, 3,n,"%lf",1);
    */ 
    fclose(fp);
    return 0;
    // run a loop over 50000 points calling the cpu and gpu function
    // record time
    

}

/**void call_cpu(X,Y){
    A=X; B=Y;
    kdtree(T,bi,bd,B,D,J);
  #pragma omp parallel for private (j) private (d) private (val)
  for(int i=0;i<I;i++){
    a[i]=u[i]=0;
    do{ 
      
      eballsearch_next(a+i,S+mtd*i,u+i,A+D*i,rad,B,T,D,J); 
        j=a[i];
     
      if(j>=0){ val=q[j]*gauss(A+D*i,B+D*j,D,h)*(fx?gauss(F+Df*i,G+Df*j,Df,hf):1);
        w[i]+=val; if(tr) continue;
        for(d=0;d<D; d++) U[i+I*d]+=val*B[d+D *j];
        for(d=0;d<Df;d++) V[i+I*d]+=val*G[d+Df*j];
      }
    } while(u[i]);
  } ;
} **/