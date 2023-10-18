import numpy as np
import sys
from glob import glob
import matplotlib.pyplot as plt

if(len(sys.argv)!=2):
    print("ERROR: Please enter raw filepath!")
    exit()

raw_folderpath = sys.argv[1]
pcds=glob(raw_folderpath + "*.depth.raw")

for p in pcds:
	raw_filepath = p
	f = open(raw_filepath, "rb")

	meta = np.fromfile(f, dtype=np.int32, count=4, sep=" ")

	rows=meta[0]
	cols=meta[1]
	image_data = np.fromfile(f, dtype=np.uint16, count=rows*cols)

	l = [f"{x} {y} {image_data[x*cols+y]}\n" for x in range(rows) for y in range(cols)]
	spl = raw_filepath.split('/')
	txt_filepath = '.'.join(spl[len(spl)-1].split('.')[:-1]) + ".txt"
	
	with open(raw_folderpath + txt_filepath, 'w') as txt_file:
	    txt_file.writelines(l)

	print(f" -- {txt_filepath}")
