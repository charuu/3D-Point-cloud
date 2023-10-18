import numpy as np
import cv2
import time
import matplotlib.pyplot as plt
import open3d as o3d
import glob as glob
import seaborn as sns
import pandas as pd
import copy

def load_image_mask(rpath,trans_id=None):
    image_list=[]
    pcd_list=[]
    mask_list=[]
    
    path = rpath 
    
    imgs=glob.glob(path+"*.jpg")
    
    if trans_id==None:
        arr=(imgs[i].split('/'))
        name = arr[len(arr)-1].split('_')[0]
    else:
        name = trans_id

    
    low_res = False
    
    msks=glob.glob(path+name+".m.jpg")
    pcds=glob.glob(path+name+ ".depth.txt")
    img = path+name+str(".jpg") 
    print(img)
    if low_res == True:
        img_left_color_img = cv2.resize(cv2.imread(img,1),(1600,1000), interpolation = cv2.INTER_NEAREST)
    else:
        img_left_color_img =  cv2.imread(img,1) 
  
    # img_left_color_img = cv2.cvtColor(img_left_color_img, cv2.COLOR_BGR2RGB).astype(np.uint8)
    print(img_left_color_img.shape)
    
    if low_res == True:
        print(msks)
        mask= cv2.resize(cv2.imread(msks[0],0),(1600,1000), interpolation = cv2.INTER_NEAREST)
    else:
        mask= cv2.imread(msks[0],0)  
    
    print(mask.shape)

    point_cloud=o3d.io.read_point_cloud(pcds[0],'xyz')
    points = np.asarray(point_cloud.points)
    print(points.shape)
    mask_reshape = mask.reshape(-1, )
    points[mask_reshape==0] = 0

    img_left_color= img_left_color_img.reshape(-1,3)

    mask_list.append(mask_reshape.reshape(mask.shape))
    image_list.append(img_left_color.reshape(img_left_color_img.shape))
    pcd_list.append(point_cloud)
        
    return image_list,pcd_list,mask_list

def write_ply(fn, verts, colors):
    ply_header = '''ply
    format ascii 1.0
    element vertex %(vert_num)d
    property float x
    property float y
    property float z
    property uchar red
    property uchar green
    property uchar blue
    end_header
    '''
   # out_colors = colors.copy()
    verts = verts.reshape(-1, 3)
    colors = colors.reshape(-1, 3)
    verts = np.hstack([verts, colors])
    with open(fn, 'wb') as f:
        f.write((ply_header % dict(vert_num=len(verts))).encode('utf-8'))
        np.savetxt(f, verts, fmt='%f %f %f %d %d %d ')
    return
 
def draw_registration_result(source, target, transformation):
    source_temp = copy.deepcopy(source)
    target_temp = copy.deepcopy(target)
    source_temp.transform(transformation)
    o3d.visualization.draw_geometries([source_temp, target_temp])
    
    
def find_l2_distance(pcd,pcd2,corr):
    dist=0
    for c in corr:
        if (c[1] < len(np.array(pcd.points)) and c[0] < len(np.array(pcd2.points))):
            a=np.array(pcd.points)[c[1]]
            b=np.array(pcd2.points)[c[0]]
            dist += np.linalg.norm(a-b)
    dist = dist/len(corr)
    return dist

def remove_outliers_from_pcd(p,img,mask,filepath):
    arr = np.array(p.points)
    print(arr.shape)
    mask_reshape = mask.reshape(-1, )
    arr[mask_reshape==0] = 0
    
    arr[:,2][np.round(arr[:,2]) > 800] = 0
    
    arr_nan= [po for po in range(len(arr)) if (arr[po][2] != 0).all() ]
    p_no_nan = np.array(arr)[arr_nan]
    img_t_arr = img.reshape(-1,3)[arr_nan]
    
   # print(arr_nan.shape, img_t_arr.shape, p_no_nan.shape)
    
    orig_no_outliers = o3d.geometry.PointCloud() 
    orig_no_outliers.points = o3d.utility.Vector3dVector(np.array(p_no_nan))
    orig_no_outliers.colors = o3d.utility.Vector3dVector(np.array(img_t_arr)/255)
    
    write_xyz(filepath+'_bcpd.txt',p_no_nan,'bcpd')
    write_xyz(filepath+'_open3d.txt',p_no_nan,'open3d')
    write_xyz(filepath+'.xyz',p_no_nan,'open3d')
    
    return orig_no_outliers
       
    
def create_pointcloud(p,img,mask,path):
    return remove_outliers_from_pcd(p,img,mask,path)

def write_xyz(filepath,pcd,file_type):
    
    if file_type =='bcpd':
        with open(filepath, 'w') as f:
            r = [f.write(str((line).tolist())[1:-1]+'\n') for line in np.array(pcd)]
    else:
        with open(filepath, 'w') as f:
            r = [f.write(str((line).tolist())[1:-1].replace(',',' ')+'\n') for line in np.array(pcd)]
    
    return 1

def read_xyz(filepath):
    pcd = o3d.io.read_point_cloud(filepath,'xyz')
    return pcd