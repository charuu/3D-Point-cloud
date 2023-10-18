from multiprocessing import pool
import open3d as o3d
import teaserpp_python
import numpy as np 
import copy
import cv2
import time
import matplotlib.pyplot as plt
import glob as glob
import seaborn as sns
from load_inputs import *
from config import *
from random import seed
from random import sample
import sys
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import matplotlib.pyplot as plt
import matplotlib as mpl
import shlex, subprocess
import os
from PIL import Image 

class Outlier_removal_batch:
    
    def __init__(self,img, pts, msk):
        self.img = img
        self.pts = pts
        self.msk= msk

    
    
def main():
    print("\nArguments passed (Reference, Target):\n", end = "")

   
    try:     
        trans_file_input = sys.argv[1]
    except:
        print('Please provide reference transaction id!')
        sys.exit(1)  # abort because of error
        
    
    with open(trans_file_input, 'r') as f:
        trans_arr = f.read().split("\n")
    
    ctr=0
    for t in trans_arr:
        arr = t.split(" ")
        
        TARGET_PATH = arr[0]
        trans_id_target = arr[1]
        REF_PATH = arr[2]
        trans_id_ref = arr[3]
        
        full_ref_path = REF_PATH  + trans_id_ref
        full_target_path = TARGET_PATH + trans_id_target
        
        raw_folderpath = sys.argv[1]
        pcds=glob.glob(raw_folderpath + "*.depth.txt")

        ref_img, ref_pts, ref_msk = load_image_mask(raw_folderpath,r)
        or1 = Outlier_removal_batch(ref_img[0], ref_pts[0], ref_msk[0])
        rm_pcd =  or1.remove_outlier(raw_folderpath+r)

   

if __name__ == '__main__':
    main()