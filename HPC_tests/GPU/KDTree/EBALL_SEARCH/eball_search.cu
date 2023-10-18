#include <iostream>
#include <chrono>
#include <time.h>
#include <algorithm>
#include <math.h>


#define SQ(x) ((x)*(x))
extern "C" int* ball_tree_search_wrapper(double* points_c,int* T);
__host__ void eballsearch_next(
       int           *m,  /*  O  |   1   | next index within radius e */
       int           *S,  /*  W  | 2logN | stack                      */
       int           *q,  /*  W  |   1   | top index of stack 'S'     */
       const double  *y,  /*  I  |   D   | the point of interest      */
       double         e,  /*  I  | const.| ball radius                */
       const double  *X,  /*  I  |   DN  | points                     */
       const int     *T,  /*  I  |  3N+1 | kdtree                     */
       int            D,  /*  I  | const.| dimension                  */
       int            N   /*  I  | const.| #points                    */
     );
__host__ static double dist(const double *x, const double *y, double D);
__host__ void kdtree(
       int           *T,  /* O | 3N+1 | depth(N),left(N),right(N),root(1)    */
       int           *a,  /* W |  6N  | index(N),size(N),buffer(3N),stack(N) */
       double        *v,  /* W |  2N  | buffer1(N), buffer2(N)               */
       const double  *X,  /* I |  DN  | points                               */
       int            D,  /* I |      | dimension                            */
       int            N   /* I |      | #points                              */
    );
__host__ int *kdtree_build(const double *X, int D, int N);


extern "C" int* ball_tree_search_wrapper(double* points_c,int* T) {
  //  int *a,*u,*S;
    double* A=points_c;
    double* B=points_c;
    int D=3;
    int N=50000;
   // int *wi;
    //srand(16);
    //int * T ;//=(int *)calloc(3*50000+1,sizeof(int));
   // wi=(int*)calloc(6*50000,  sizeof(int));
    T = kdtree_build(A,3,50000);
    
   // for(int i=0;i<10;i++){
      //  printf("%d, %d, %d\n",T[0],T[1],T[2]);
      //   T = T+3;
   // }
   // int mtd=10;int j;int si=0;
  //  wi+=6*50000; a=wi+si;si+=50000; S=wi+si;si+=mtd*50000;
  //  u=wi+si;si+=50000;
  
 // for(int i=0;i<50000;i++){
  //  a[i]=u[i]=0;
  //  do{ 
      
     // eballsearch_next(a+i,S+mtd*i,u+i,A+D*i,0.001,B,T,D,50000); 
   //   j=a[i];
   //   printf("query:%lf,found:%lf\n",A[D*i],B[D*j]);
     
   // } while(u[i]);
 // } ;
//free(A);free(B);
//free(T);
return T;
}
__host__ void eballsearch_next(
       int           *m,  /*  O  |   1   | next index within radius e */
       int           *S,  /*  W  | 2logN | stack                      */
       int           *q,  /*  W  |   1   | top index of stack 'S'     */
       const double  *y,  /*  I  |   D   | the point of interest      */
       double         e,  /*  I  | const.| ball radius                */
       const double  *X,  /*  I  |   DN  | points                     */
       const int     *T,  /*  I  |  3N+1 | kdtree                     */
       int            D,  /*  I  | const.| dimension                  */
       int            N   /*  I  | const.| #points                    */
     ){

  int d,p,nl,nr,n=T[3*N],state=1; double u,v;

  if(*q==0) S[(*q)++]=n;
  while((*q)&&state){ n=S[--(*q)];
     nl=T[n+N*1]; p=T[n];
     nr=T[n+N*2]; d=p%D;

     if(dist(y,X+D*n,D)<=e){*m=n;state=0;}

     v=y[d]-X[d+D*n]; u=fabs(v);
     if   (v>0){if(nr>=0)S[(*q)++]=nr; if(nl>=0&&u<=e)S[(*q)++]=nl;}
     else      {if(nl>=0)S[(*q)++]=nl; if(nr>=0&&u<=e)S[(*q)++]=nr;}

  }  if( state) *m=-1;
}
__host__ static double dist(const double *x, const double *y, double D){
  int d; double val=0;
  for(d=0;d<D;d++) val+=SQ(x[d]-y[d]);
  return sqrt(val);
}
__host__ static void swap(double *a, double *b){double tmp; tmp=*a; *a=*b; *b=tmp;}

__host__ double median(double *a, double *w, const int N){
  const int c = N/2;
  int     i,j,k,l,u,e,ofs=0,size=N;
  double  *tmp, p;/*pivot*/

  while(1){i=j=k=0;p=a[0];e=1;
    for(i=1;i<size;i++){
      if      (a[i]< p)  a[j++]=a[i];
      else if (a[i]> p)  w[k++]=a[i];
      else   /*a[i]==p*/ e++;
    } l=ofs+j;u=l+e-1;

    if      (c<l) {size=j;}
    else if (c>u) {tmp=a;a=w;w=tmp;ofs=u+1;size=k;}
    else break;
  }

  return p;
}

__host__ static inline void divide(
   int          *  b,    /*  I/O | 5N | array to be divided         */
   double       *  v,    /*   W  | 2N | working memory              */
   int             K,    /*   I  |    | size of array to be divided */
   const double *  X,    /*   I  | DN | points                      */
   int             D,    /*   I  |    | dimension                   */
   int             N,    /*   I  |    | #points                     */
   int             p     /*   I  |    | current depth               */
  ){
  int k,i=0,j=0,e=0,c=K/2,d=p%D; double med,val; double *w=v+N;
  int *sz=b+N,*bl=b+2*N,*bc=b+3*N,*br=b+4*N;

  *sz=K; /* store original array size */
  for(k=0;k<K;k++){v[k]=X[d+D*b[k]];} swap(v,v+K/2);

  if (K==1) bl[0]=b[c];
  else { med=median(v,w,K);
    for(k=0;k<K;k++){ val=X[d+D*b[k]];
      if      (val<med) bl[i++]=b[k];
      else if (val>med) br[j++]=b[k];
      else              bc[e++]=b[k];
    }
    for(k=0;k<i;k++) b[k    ]=bl[k];
    for(k=0;k<e;k++) b[k+i  ]=bc[k];
    for(k=0;k<j;k++) b[k+i+e]=br[k];
  }
}
__host__ int *kdtree_build(const double *X, int D, int N){
   int *T,*wi; double *wd;

  T =(int *)calloc(3*N+1,sizeof(int));
  wi=(int *)calloc(6*N,  sizeof(int));
  wd=(double *)calloc(2*N,  sizeof(double));
  kdtree(T,wi,wd,X,D,N);
  free(wi); free(wd);

  return T;
}
__host__ void kdtree(
       int           *T,  /* O | 3N+1 | depth(N),left(N),right(N),root(1)    */
       int           *a,  /* W |  6N  | index(N),size(N),buffer(3N),stack(N) */
       double        *v,  /* W |  2N  | buffer1(N), buffer2(N)               */
       const double  *X,  /* I |  DN  | points                               */
       int            D,  /* I |      | dimension                            */
       int            N   /* I |      | #points                              */
    ){
  int *bl=NULL,*br=NULL,*b=a,*S=a+5*N; int n,nl,nr,q=0,c,cl,cr,s,sl,sr; int p=0;

  /* init */
  for(n=0;n<3*N;n++) T[n]=-1;
  for(n=0;n<  N;n++) b[n]= n;
  /* basis */
  divide(b,v,N,X,D,N,p); S[q++]=0;c=N/2;T[b[c]]=p; T[3*N]=b[c]; /*root*/
  
  /* step */
  while(q){ b=a+S[--q];s=*(b+N); /*pop*/
    /* compute locations and sizes of divided arrays */
    c=s/2; n=b[c]; bl=b; br=bl+c+1; sl=c; sr=c-(s%2?0:1); p=T[n];
    /* division of coordinate space */
    if(sl){divide(bl,v,sl,X,D,N,p+1);S[q++]=bl-a;cl=sl/2;nl=bl[cl];T[nl]=p+1;T[n+N*1]=nl;}
    if(sr){divide(br,v,sr,X,D,N,p+1);S[q++]=br-a;cr=sr/2;nr=br[cr];T[nr]=p+1;T[n+N*2]=nr;}
  }
}
