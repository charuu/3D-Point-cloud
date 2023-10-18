import multiprocessing as mp
import open3d as o3d

import numpy as np 
import copy
import cv2
from datetime import datetime
from timebudget import timebudget
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
import json
from shutil import copyfile
from clear_cache import clear as clear_cache
import pandas as pd

def run_complex_operations(distance):  
    distance_array = distance
    d = int(float(distance_array))
    if (d in range(0,5)):
        return ((0,0,0))
    elif (d in range(5,10)):
        return ((0, 255, 0))
    elif (d in range(10,20)):
        return ((153, 255, 255))
    elif (d in range(20,30)):
        return ((0, 255, 255))
    elif (d in range(30,40)):
        return ((204, 153, 255))
    elif (d in range(40,800)):
        return ((0,0,255))

class distanceCalculator:
    
    def __init__(self,img, pts, msk):
        self.img = img
        self.pts = pts
        self.msk= msk
    
    def remove_outlier(self, path):
        """
        Summary.
        Remove NULL values and points with depth greater than 800mm from the raw point cloud data file.
        Parameters:
        path (String): Relative path to folder containing image, raw point cloud data and image mask.
        Returns:
        pcd_no_outliers: Point cloud data after removing outliers
        """
        pcd_no_outliers = create_pointcloud(self.pts, self.img, path)
            
        return pcd_no_outliers
    
    def register(self,source_path,target_path):
        """
        Summary.
        Registration of deformable reference point cloud data to the fixed target point cloud file.
        Parameters:
        source_path (String): Relative path of reference point cloud data 
        target_path (String): Relative path of target point cloud data 
        Returns:
        None
        """
        print(BINARY_FILE_PATH, target_path  ,"-y",  source_path, VOXEL_SIZE, 
                                 K,J,COMPONENTS,ENABLE_KDTREE_SEARCH,F,D,RADIUS, NORM_X,NORM_Y,LAMBDA,MSE,GAMMA,Print )
    
        subprocess.run([BINARY_FILE_PATH,"-x",  target_path ,"-y",  source_path, VOXEL_SIZE,COMPONENTS, 
        K,J,ENABLE_KDTREE_SEARCH,F,D,RADIUS, NORM_X,NORM_Y,LAMBDA,MSE,GAMMA,Print],stdout=subprocess.PIPE)
        
        Dict = {}
        Dict["Parameters"]=VOXEL_SIZE+","+K+","+J+","+COMPONENTS+","+ENABLE_KDTREE_SEARCH+","+F+","+D+","+RADIUS+","+NORM_X+","+NORM_Y+","+LAMBDA+","+MSE+","+GAMMA+","+Print
        with open('output_comptime.txt', 'r') as f:
            for t in f.readlines():
                arr = t.split(":")
                Dict[arr[0].strip()]= arr[1].strip()
            
        time = Dict
        Dict = {}
        with open('output_info.txt', 'r') as f:
            for i in f.readlines():
                arr = i.split("\t")
                Dict[arr[0].strip()]= arr[1].strip()
        info = Dict
        
        
        return time, info
        
    def calculate(self, target):
        """
        Summary.
        Calculate closed point distance between the reference and target point cloud data.
        Parameters:
        target (point cloud): Target point cloud data after removal of outliers
        Returns:
        distance_array: Distance object storing pointwise values from the target 
        to the reference point cloud using closest point distance function in open3d
        """
        ref_registered_pcd = None
        distance_array_wrt_tgt = None
        
        ref_registered_pcd = o3d.io.read_point_cloud(REGISTERED_REFERENCE_FILENAME,'xyz')
        distance_array_wrt_tgt = target.compute_point_cloud_distance(ref_registered_pcd)
        
        return distance_array_wrt_tgt
    
  
    def save_distances(self, distance_array,target_pcd, target_shape):
        """
        Summary.
        Creation of heatmap for the distances calculated to 
        the closest points in the deformed reference point cloud data with respect 
        to the target point cloud.
        Parameters:
        distance_array (array): Distance object storing pointwise values from the target 
        to the reference point cloud using closest point distance function in open3d
        target_pcd (point cloud): Target point cloud data after removal of outliers
        target_shape (tuple): Shape of target image
        Returns:
        distance_image_normalised: Description of return value
        cmap: cmap 
        """
        
        distance_image = None
        target_points = None
        
        distance_image = np.zeros((target_shape[0],target_shape[1],3), np.uint8)
        #foreign_object_mask = np.zeros((target_shape[0],target_shape[1],3),  np.uint8)
        
        tgtpcd = np.array(target_pcd.points)
        length = len(distance_array)
        
        x_list = (tgtpcd[:,0]).astype(int)
        y_list = (tgtpcd[:,1]).astype(int)
        
        result = [(run_complex_operations(distance_array[i])) for i in range(length)]
        
        distance_image[x_list,y_list] = np.array(result)
        
        
        return distance_image
                  
    
    def show_bb(self,foreign_object_mask,image):
        """
        Summary line.
        Draw bounding boxes on connected components in the binary image containing foreign objects.
        Parameters:
        target_pcd (point cloud): Target point cloud data after removal of outliers
        image (Image): Description of arg1
        distance_array (Array): Distance object storing pointwise values from the target
        target_shape (tuple): Shape of target image
        Returns:
        gt: Image array
        """
        count = 0
        gt = None
        print(foreign_object_mask.shape)    
       # Create binary image of the detected regions 
        kernel = np.zeros((1,1),np.uint8)
        
        closing =  cv2.morphologyEx(foreign_object_mask, cv2.MORPH_CLOSE, kernel, iterations=40)
        opening =  cv2.morphologyEx(closing, cv2.MORPH_OPEN, kernel, iterations=2)
        
        th, binaryImage = cv2.threshold(opening, 0, 255, cv2.THRESH_BINARY)
        bi = binaryImage.copy()
        # Find connected components in the binary image
        gt= image.copy()
        contours, hierarchy = cv2.findContours(np.uint8(bi), cv2.RETR_EXTERNAL,  cv2.CHAIN_APPROX_SIMPLE)
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            area= cv2.contourArea(c)
            
            if (area) >= BOUNDING_BOX_AREA_MIN_THRESHOLD and (area) <= BOUNDING_BOX_AREA_MAX_THRESHOLD :
                count = count + 1
                cv2.rectangle(gt,(x,y), (x+w,y+h), (255,0,0), 10)
        print("Number of bounding boxes with the detected objects : ",count)
        return gt,count
    
    def remove_outlier(self,path):
        pcd_no_outliers = create_pointcloud(self.pts,self.img,self.msk,path)

        return pcd_no_outliers
    
def visualization(directory,reference, target, reference_warpped,ctr):
    vis = o3d.visualization.Visualizer()
    vis.create_window(visible=False)

    reference.paint_uniform_color([1.0, 0, 0])
    target.paint_uniform_color([0.0, 0, 1])
    vis.add_geometry(reference)
    vis.add_geometry(target)
    vis.add_geometry(reference_warpped)
    vis.update_geometry(reference)
    vis.poll_events()
    vis.update_renderer()
    vis.capture_screen_image(OUTPUT_PATH +directory+'/3D'+str(ctr)+ 'ScreenCapture.png')
    vis.destroy_window()

def main():
    ctr=0
    print("\nArguments passed (Reference, Target):\n", end = "")
    SuperDict=[]
    Dict = {}
    runs=[]
    data=[]
    try:     
        trans_file_input = sys.argv[1]
    except:
        print('Please provide reference transaction id!')
        sys.exit(1)  # abort because of error
        
    
    with open(trans_file_input, 'r') as f:
        trans_arr = f.read().split("\n")
    
    if os.path.exists("data.json"):
        jsonFile = open("data.json",'r')
        data = json.load(jsonFile)
        ctr=len(data)
        jsonFile.close()
    else:
        ctr=0
    
    for t in trans_arr:
        after = None
        before = None
        count = None
        dist_im_tgt = None
        object_mask = None
        Dict ={}
        arr = t.split(" ")
        dist_tgt = None
        start_tic =  datetime.now()
        
        TARGET_PATH = arr[0]
        trans_id_target = arr[1]
        REF_PATH = arr[2]
        trans_id_ref = arr[3]
        full_ref_path = REF_PATH  + trans_id_ref
        full_target_path = TARGET_PATH + trans_id_target
        
        Dict["id"] = str(ctr) +'-'+trans_id_ref+ '-'+trans_id_target
        Dict["Reference"]=full_ref_path+'.jpg'
        Dict["Target"]=full_target_path+'.jpg'
        
        r = trans_id_ref
        t = trans_id_target
        directory = r + '-' + t
        
        try:
            os.makedirs(OUTPUT_PATH + r + '-' + t, exist_ok = True)
            print("Directory '%s' created successfully" % directory)
        except OSError as error:
            print("Directory '%s' can not be created" % directory)


        # Step 0: Loading data
        ref_img, ref_pts, ref_msk = load_image_mask(REF_PATH, trans_id_ref)
        target_img, target_pts, target_msk = load_image_mask(TARGET_PATH, trans_id_target)

        ref_shape = np.array(ref_img[0][:,:,0].shape)
        target_shape = np.array(target_img[0][:,:,0].shape)

        print(target_shape)

        # Initialising class objects
        dc1 = distanceCalculator(ref_img[0], ref_pts[0], ref_msk[0])
        dc2 = distanceCalculator(target_img[0], target_pts[0], target_msk[0])

        #Outlier removal 
        if outlier_removal == True:
            if os.path.exists(full_ref_path + '_open3d.txt')==False:
                ref_pointcloud = dc1.remove_outlier(full_ref_path)
                o3d.io.write_point_cloud(full_ref_path + '_open3d.ply', ref_pointcloud)
            
        if outlier_removal == True:
            if os.path.exists(full_target_path + '_open3d.txt')==False:
                target_pointcloud = dc2.remove_outlier(full_target_path)
                o3d.io.write_point_cloud(full_target_path + '_open3d.ply', target_pointcloud)
            
        # Step 1: Reading pre-processed data after removing outliers
        print("\nStep 1: Reading pre-processed data.")
        print(full_ref_path + '_open3d.txt')
        
        rm_pcd = read_xyz(full_ref_path + '_open3d.txt')
        tgt_pcd = read_xyz(full_target_path + '_open3d.txt')
        
        if distance_calculate==True:
            dist_tgt = 0#dc1.calculate(tgt_pcd)
            before = 0
          #  before = np.sum(dist_tgt)/len(tgt_pcd.points)
            Dict["MSE Before"]= format(before, '.2f') 
            print("Before avg distance wrt tgt : ", before)
        else:
            dist_ref,dist_tgt = 0, 0
            before = 0 
            Dict["MSE Before"]= format(before, '.2f') 
            
        # Step 2: Register
        print("\nStep 2: Registering the reference to the target point cloud.")               
        time, info = dc1.register(full_ref_path+'_bcpd.txt', full_target_path+'_bcpd.txt')
        warpped_pcd = read_xyz('output_y.interpolated.txt')
        visualization(directory, rm_pcd, tgt_pcd, warpped_pcd,ctr)
        Dict["3D screen capture"] = OUTPUT_PATH +directory+'/3D'+str(ctr)+ 'ScreenCapture.png'
        copyfile('output_y.interpolated.txt', OUTPUT_PATH +directory+'/'+ r +'_reference_warpped.txt')   
        
        # Step 3: calculate distance 
        print("\nStep 3: Calculating distance between the reference and target point cloud.")
        tic =  datetime.now()
        dist_tgt = None
        dist_tgt = dc1.calculate(tgt_pcd)
        
        if SAVING_DISTANCE_OBJECT==True:
            with open( OUTPUT_PATH + directory+'/'+ r + '-' + t + '-tgt-DIST.txt', 'wb') as f:
                np.savetxt(f, dist_tgt, fmt='%f')

            with open(OUTPUT_PATH + directory+'/'+ r +'-'+ t + '-tgt-DIST.txt', 'r') as f:
                dist_tgt = f.readlines()
       
        toc =  datetime.now()
        print("Time taken in calculate distance : ", toc-tic)
        after=0
        if distance_calculate==True:
            after = np.sum(dist_tgt)/len(tgt_pcd.points)
            print("After avg distance wrt tgt : ", after)
            Dict["MSE After"]= format(after, '.2f') 
        else:
            after = 0
            Dict["MSE After"]= format(after, '.2f') 
            
        # Step 4: Creation and saving of target image with its heatmap     
        print("\nStep 4: Creation of heatmap from the distance object.")
        tic =  datetime.now()
        dist_im_tgt = dc1.save_distances(np.array(dist_tgt), tgt_pcd, target_shape)
        x_list = (np.array(tgt_pcd.points)[:,0]).astype(int)
        y_list = (np.array(tgt_pcd.points)[:,1]).astype(int)
        
        foreign_object_mask = np.zeros((target_shape[0],target_shape[1],3),  np.uint8)
        foreign_object_mask[x_list,y_list] = [(0,0,0) if(d <  DISTANCE_THRESHOLD) else (0,0,255) for d in np.array(dist_tgt).astype(float)] 
        
        cv2.imwrite( OUTPUT_PATH + directory+'/'+ r + '-' + t +'-'+str(ctr)+ '-tgt-DIST.png', dist_im_tgt)
        cv2.imwrite( OUTPUT_PATH + directory+'/'+ r + '-' + t +'-'+str(ctr)+ '-tgt-object_mask.png', foreign_object_mask)
        Dict["HeatMap_image"]=OUTPUT_PATH + directory+'/'+ r + '-' + t +'-'+str(ctr)+'-tgt-DIST.png'
        toc =  datetime.now()
        print("Time taken in creation of heat map : ", toc-tic)
        
        # Step 5: Creation and saving of image with bounding boxes
        print("\nStep 5: Creation of image from the target image with the detected bounding boxes.")
        tic =  datetime.now()
        o_mask = cv2.imread( OUTPUT_PATH + directory+'/'+ r + '-' + t +'-'+str(ctr)+ '-tgt-object_mask.png',0).astype(float)
        bb_tgt, count = dc1.show_bb(o_mask,target_img[0])
        Dict["Bounding boxes"] = count
        cv2.imwrite( OUTPUT_PATH + directory + '/' + r + '-' + t +'-'+str(ctr)+'-tgt-BB.png', bb_tgt)
        Dict["BB_image"] = OUTPUT_PATH +directory+'/'+ r + '-' + t +'-'+str(ctr)+'-tgt-BB.png'
        toc =  datetime.now()
        print("Time taken in creating bounding boxes : ", toc-tic)
        
        cv2.imwrite( OUTPUT_PATH + directory + '/' + r +'.png', ref_img[0])
        cv2.imwrite( OUTPUT_PATH + directory + '/' + t +'.png', target_img[0])
        
        Dict["Time"] = time
        Dict["Output Info"] = info
        
        stop_toc =  datetime.now()
        print("Time taken in transaction : ",ctr," ", stop_toc-start_tic)
        
        ctr=ctr+1
        
        data.append(Dict)
        
  #  data.append(SuperDict)
    jsonFile = open("data.json", "w+")
    json.dump(data, jsonFile)
    jsonFile.close()
        
    
if __name__ == '__main__':
    main()


