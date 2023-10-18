from matplotlib.colors import ListedColormap, LinearSegmentedColormap

LOAD_DATA = True
READ_PCD = True
REGISTER = True
WRITE_REGISTERED_PCD = True
READ_REGISTERED_PCD = True
SAVING_DISTANCE_OBJECT = False
CREATE_BOUNDING_BOXES = True
BOUNDING_BOX_AREA_MAX_THRESHOLD = 1250000
BOUNDING_BOX_AREA_MIN_THRESHOLD = 4000
DISTANCE_THRESHOLD =30
#-J300 -K70 -p -d5 -e0.3 -f0.3 -g3 -D'B,2000,0.08' -w0.1,        |
                                                               
# BCPD++ algorithm parameters
BINARY_FILE_PATH = "../bcpd/bcpd"
#BINARY_FILE_PATH = "../bcpd/bcpd"
#bcpd/bcpd_cpu/bcpd
VOXEL_SIZE = "-DB,50000,0.08"
COMPONENTS="-N 2"
K ="-K70"
J= "-p -J300"
D = "-d15"
ENABLE_KDTREE_SEARCH = "-b50 -G geodesic,0.2,40,0.15  " #-Ggeo,0.2,8,0.10 -G geodesic,0.5,40,0.15  
RADIUS = "-e0.15"
F = "-f0.2"
NORM_X = "-uy"
NORM_Y = "-k1000"
LAMBDA = "-l10"
Print = "-sve" #xyY
MSE ="-c 1e-5"
GAMMA="-g1"
outlier_removal = True
distance_calculate = True
# File path
REGISTERED_REFERENCE_FILENAME = "../bcpd-pp-nuvoscan/output_y.interpolated.txt"

DATA_FILE = "../../data/input.txt"
OUTPUT_PATH="/mnt/Data1/data/outputs/"

def get_cmap(distance_image):
    cmap = LinearSegmentedColormap.from_list(distance_image, 
                                             [(0,"black"), 
                                              (0.1,"green"), 
                                              (0.2, "yellow"),  
                                              (0.3,"orangered"),
                                              (0.4, "pink"), 
                                              (0.5, "orange"), 
                                              (0.6, "red"), 
                                              (1, "red")])
    return cmap
