
# Nuvoscan - Bayesian Coherent Point Drift plus plus

This repository implements a non-rigid point matching algorithm, Bayesian coherent point drift plus plus(BCPD++) on the nuvoscan depth scan images.

## Table of Contents
1. [Experiments](#experiments)
    + [Folder setup](#folder-setup)
    + [Execution](#execution)
2. [Compilation](#compilation)
    + [Windows](#windows)
    + [MacOS and Linux](#macos-and-linux)
3. [Usage](#usage)
    + [Terms and symbols](#terms-and-symbols)
    + [Input data](#input-data)
    + [Tuning parameters](#tuning-parameters)
    + [Kernel functions](#kernel-functions)
4. [Acceleration](#acceleration)
    + [Nystrom method](#nystrom-method)
    + [KD tree search](#kd-tree-search)
    + [Downsampling](#downsampling)
    + [Interpolation](#interpolation)
5. [Options](#options)
    + [Convergence](#convergence)
    + [Normalization](#normalization)
    + [File output](#file-output)
    + [Terminal output](#terminal-output)

## Experiments

### Folder setup
1. Data 
 + Reference
     - Image
     - Mask
     - Point cloud data in .xyz format
     
 + Target
     - Image
     - Mask
     - Point cloud data in .xyz format
     
 + Outputs
     - File containing distance values from the target point cloud data to the registered reference in mm. Format `Trans_id_reference-Trans_id_target-DIST.txt`
     - Image displaying heatmap where colors correspond to the distances between the reference and the target. Format `Trans_id_target-BB.png`
     - Image displaying the bounding boxes in regions with difference in the distances greater than 20mm. Format `Trans_id_target-DIST.png`
     
### Execution
1. To pre-process data for registeration we perform removal of NULL values and outliers using script `Outlier_removal_batch.py`
It writes the point cloud data file in two types of input format, one accepted by the bcpd algorithm and the other by open3d function. 
`python Outlier_removal_batch.py car_type_folder_name Trans_id_reference Trans_id_target`
2. Regiseration using bcpd++ can be performed using script `bcpd_plusplus.py`. The configuration of which can be updated by updating parameters in `config.py`
`python bcpd_plusplus.py car_type_folder_name Trans_id_reference Trans_id_target`

## Compilation

### Windows

Ready to go. The compilation is not required. Use the binary file `bcpd.exe` in the `win` directory.
The binary file was created by GCC included in the 32-bit version of the MinGW system.
Therefore, it might be quite slower than the one compiled in a Mac/Linux system.

### MacOS and Linux

1. Install OpenMP and the LAPACK library if not installed. If your machine is a Mac, install Xcode, Xcode command-line tools,
   and MacPorts (or Homebrew).
2. Download and decompress the zip file that includes source codes.
3. Move into the top directory of the uncompressed folder using the terminal window.
4. Type `make OPT=-DUSE_OPENMP ENV=<your-environment>`; replace `<your-environment>` with `LINUX`,
   `HOMEBREW`, or `MACPORTS`. Type `make OPT=-DNUSE_OPENMP` when disabling OpenMP.

The default installation path for Homebrew seems to be changed. If the compilation under Homebrew fails,
please replace the path `/usr/local/` with `/opt/homebrew/` in `makefile`.

## Usage

Type the following command in the terminal window for Mac/Linux:

` ./bcpd -x <target: X> -y <source: Y> (+options) `

For Windows, type the following command in the DOS prompt:

` bcpd -x <target: X> -y <source: Y> (+options) `

Brief instructions are printed by typing `./bcpd -v` (or `bcpd -v` for windows) in the terminal window.
The binary file can also be executed using the `system` function in MATLAB.
See MATLAB scripts in the `demo` folder regarding the usage of the binary file.

### Terms and symbols

- X: Target point set. The point set corresponding to the reference shape.
- Y: Source point set. The point set to be deformed. The mth point in Y is denoted by ym.
- N: The number of points in the target point set.
- M: The number of points in the source point set.
- D: Dimension of the space in which the source and target point sets are embedded.

### Input data

- `-x [file]`: The target shape represented as a matrix of size N x D.
- `-y [file]`: The source shape represented as a matrix of size M x D.

Tab- and comma-separated files are accepted, and the extensions of input files
MUST be `.txt`. If your file is space-delimited, convert it to a tab- or comma-separated file using Excel,
MATLAB, or R, for example. Do not insert any tab (or comma) symbol after the last column.
If the file names of target and source point sets are `X.txt` and `Y.txt`, these arguments can be omitted.

### Tuning parameters

- `-w [real]`: Omega. Outlier probability in (0,1).
- `-l [real]`: Lambda. Positive. It controls the expected length of deformation vectors. Smaller is longer.
- `-b [real]`: Beta. Positive. It controls the range where deformation vectors are smoothed.
- `-g [real]`: Gamma. Positive. It defines the randomness of the point matching at the beginning of the optimization.
- `-k [real]`: Kappa. Positive. It controls the randomness of mixing coefficients.

The expected length of deformation vectors is sqrt(D/lambda). Set gamma around 2 to 10 if your target point set
is largely rotated. If input shapes are roughly registered, use `-g0.1` with an option `-ux`.
The default kappa is infinity, which means that all mixing coefficients are equivalent.
Do not specify `-k infinity` or extremely large kappa to impose the equivalence of mixing coefficients,
which sometimes causes an error. If lambda (-l) is sufficiently large, e.g., 1e9, BCPD solves rigid registration problems.
If you would like to solve rigid registration for large point sets, accelerate the algorithm carefully;
see [Rigid registration](#rigid-registration).

### Kernel functions

- `-G [1-4]`: Switch kernel functions.
  - `-G1` Inverse multiquadric: `(||ym-ym'||^2+beta^2)^(-1/2)`
  - `-G2` Rational quadratic: `1-||ym-ym'||^2/(||ym-ym'||^2+beta^2)`
  - `-G3` Laplace: `exp(-|ym-ym'|/beta)`
  - `-G4` Neural network: see [Williams, Neural computation, 1998] for the definition of the kernel.
- `-b [real(s)]`: The parameter(s) of a kernel function.
  - `-b [real]`: Beta. The parameter of a kernel function except the neural network kernel.
  - `-b [real,real]`: The parameters of the neural network kernel. Do not insert whitespaces before and after comma.

The Gaussian kernel `exp(-||ym-ym'||^2/2*beta^2)` is used unless specified.
Here, `ym` represents the mth point in Y. Except the neural network kernel, the tuning parameter of
the kernel functions is denoted by beta, which controls the range where deformation vectors are smoothed.
For the neural network kernel, the first and second arguments of the option `-b` specify the standard deviations
of the intercept and linear coefficients, respectively.

## Acceleration
![alt text](https://github.com/ohirose/bcpd/blob/master/img/lucy.png?raw=true)

BCPD can be accelerated inside and outside variational Bayes inference (VBI), separately. The Nystrom method and
KD-tree search accelerate VBI. The former works before approaching convergence, whereas the latter works near
convergence. The following option accelerates VBI with default parameters:

- `-A`: VBI acceleration with parameters, i.e., `-K70 -J300 -p -d7 -e0.15 -f0.2`.

Downsampling and deformation vector interpolation, called BCPD++, accelerate non-rigid registration
outside VBI. For example, the following options activate BCPD++:

- `-DB,5000,0.08 -L100`: BCPD++ acceleration outside VBI.

If N and M are larger than several thousand, activate either the internal or external acceleration.
If N and M are more than several hundreds of thousands, activate both accelerations.
Also, the acceleration methods reduce memory consumption. Either internal or external acceleration method
**MUST** be activated to avoid a memory allocation error for such a large dataset.
Otherwise, BCPD sometimes fails without any error notice.

### Nystrom method

- `-K [int]`: #Nystrom samples for computing G.
- `-J [int]`: #Nystrom samples for computing P.
- `-r [int]`: Random number seed for the Nystrom method. Reproducibility is guaranteed if the same number is specified.

Specify `-J300 -K70`, for example. The acceleration based only on the Nystrom method probably fails to converge;
do not forget activating the KD-tree search.

### KD tree search

- `-p`: KD-tree search is turned on if specified. The following options fine-tune the KD tree search.
  - `-d [real]`: Scale factor of sigma that defines areas to search for neighbors.
  - `-e [real]`: Maximum radius to search for neighbors.
  - `-f [real]`: The value of sigma at which the KD tree search is turned on.

The default parameters are `-d7 -e0.15 -f0.2`.
Retry the execution with `-p -f0.3` unless the Nystrom method is replaced by the KD-tree search during optimization.

### Downsampling

- `-D [char,int,real]`: Changes the number of points. E.g., `-D'B,10000,0.08'`.
  - 1st argument: One of the symbols: [X,Y,B,x,y,b]; x: target; y: source; b: both, upper: voxel, lower: ball.
  - 2nd argument: The number of points to be extracted by the downsampling.
  - 3rd argument: The voxel size or ball radius required for downsampling.

Input point sets can be downsampled by the following algorithms:
1. voxel-grid resampling with voxel width r,
2. ball resampling with the radius r, and
3. random resampling with equivalent sampling probabilities.

The parameter r can be specified as the 3rd argument of `-D`. If r is specified as 0,
sampling scheme (3) is selected. The numbers of points in downsampled target and source point sets
can be different; specify the `-D` option twice, e.g., `-D'X,6000,0.08' -D'Y,5000,0.05'`.
For more information, see [paper](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=9290402) and
[appendix](https://ieeexplore.ieee.org/ielx7/34/4359286/9290402/supp1-3043769.pdf?tp=&arnumber=9290402).

### Interpolation

- `-L [int]`: #Nystrom samples for accelerating interpolation. E.g., `-L100`.

Downsampling automatically activates the deformation vector interpolation. However, if the `-L` option is
unspecified, the method runs without low-rank approximations; the execution will be quite slow or might fail.
The resulting registered shape with interpolation is output to the file with the suffix `y.interpolated.txt`.

## Options

Default values will be used unless specified.

### Convergence

- `-c [real]`: Convergence tolerance.
- `-n [int ]`: The maximum number of VB loops.
- `-N [int ]`: The minimum number of VB loops.

The default minimum VB iteration is `30`, which sometimes causes an error for small data.
If the bcpd execution stopped within 30 loops with an error notice, execute it again after
setting `-N1`, which removes the constraint on the minimum VB iteration.
The default value of the convergence tolerance is `1e-4`. If your point sets are smooth
surfaces with moderate numbers of points, specify `-c 1e-5` or `-c 1e-6`.

### Normalization

- `-u [char]`: Chooses a normalization option by specifying the argument of the option, e.g., `-ux`.
  - `e`: Each of X and Y is normalized separately (default).
  - `x`: X and Y are normalized using the location and the scale of X.
  - `y`: X and Y are normalized using the location and the scale of Y.
  - `n` : Normalization is skipped (not recommended).

Using `-ux` or `-uy` is recommended with `-g0.1` if input point sets are roughly registered.
The option `-un` is not recommended because choosing beta and lambda becomes non-intuitive.

### Terminal output

- `-v`: Print the version and the simple instruction of this software.
- `-q`: Quiet mode. Print nothing.
- `-W`: Disable warnings.
- `-h`: History mode. Alternative terminal output regarding optimization.

### File output

- `-o [string]`: Prefix of output file names.
- `-s [string]`: Save variables by specifying them as the argument of the option, e.g., `-sYP`.
  - `y`: Resulting deformed shape (=y).
  - `x`: Target shape with alignment (=x).
  - `u`: Deformed shape without similarity transformation (=u).
  - `v`: Displacement vector (=v).
  - `c`: non-outlier labels (=c).
  - `e`: matched points (=e).
  - `a`: Mixing coefficients (=alpha).
  - `P`: Nonzero matching probabilities (=P).
  - `T`: Similarity transformation (=s,R,t).
  - `Y`: Optimization trajectory.
  - `t`: Computing time (real/cpu) and sigma for each loop.
  - `A`: All of the above.

The resulting deformed shape y will be output without the `-s` option. All output variables
except for `output_[y/x].txt` and `output_y.interpolated.txt` are normalized.
In other words, only these variables are denormalized.
Therefore, the transformation `(v, s, R, t)` can only be applied to the normalized source shape,
named as `output_normY.txt`. If at least one of `u`,`v`, and `T` is specified as an argument
of `-s`, BCPD will output normalized input point sets, i.e., `output_norm[X/Y].txt`.

If `Y` is specified as an argument of `-s`, the optimization trajectory
will be saved to the binary file `.optpath.bin`.
The trajectory can be viewed using scripts: `optpath.m` for 2D data and
`optpath3.m` for 3D data. Saving a trajectory is memory-inefficient. Disable it if both N and M
are more than several hundreds of thousands. If `P` is specified as an argument of `-s`,
nonzero elements of matching probability P will be output. If the optimization is not converged,
the output of P might become time-consuming.
