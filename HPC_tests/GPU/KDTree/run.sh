#echo nn:;
#gcc -c compare_nn.c base/util.c;
#nvcc -std=c++11 -c nn.cu;
#gcc compare_nn.o nn.o -o nn -I/usr/local/cuda/include -L/usr/local/cuda/lib64 -lcudart -lstdc++ -lm

#./nn;


#echo eballsearch:;
#nvcc -std=c++11 -c eball_search.cu;
#gcc compare_nn.o util.o eball_search.o -o eball_search -I/usr/local/cuda/include -L/usr/local/cuda/lib64 -lcudart -lstdc++ -lm
#./eball_search;


echo Flann GPU implementation:;
gcc -c FLANN_BCPD/flann_example_c.c -o FLANN_BCPD/flann_example_c.o;
gcc FLANN_BCPD/flann_example_c.o -o FLANN_BCPD/flann_example_c -I/usr/local/cuda/include -l:liblz4.a -L/usr/local/cuda/lib64 -lcudart -lstdc++ -lm
~/Repos/HPC_tests/GPU/KDTree/FLANN_BCPD/flann_example_c;