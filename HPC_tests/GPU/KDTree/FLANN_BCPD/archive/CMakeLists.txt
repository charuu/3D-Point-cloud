# min. version of cmake required for this project
cmake_minimum_required( VERSION 3.10)

# name of the project
project(flann_bcpd)
find_package(CUDA REQUIRED)
find_library(FLANN PUBLIC)
set(CMAKE_CXX_STANDARD 11)
#target_include_directories(kdtree_flann_cuda PUBLIC /usr/include/c++/11)
add_executable(kdtree_flann_cuda src/kdtree_flann_cuda.c)
target_link_libraries(kdtree_flann_cuda flann)
find_package(PkgConfig REQUIRED)
pkg_check_modules(LZ4 REQUIRED liblz4)
target_link_libraries(kdtree_flann_cuda liblz4.a)
set_target_properties(kdtree_flann_cuda PROPERTIES COMPILE_FLAGS -fPIC)

include_directories(${HDF5_INCLUDE_DIR})
