import bpy
import sys
import os
import math
from math import sin,cos,radians
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import skimage
from skimage.io import imread, imshow
from skimage import measure
import re

#define stuff
vertices = []
edges = []
faces = []
degrees = 6
count = 0
blendconst = 0.0651084055
origin = [(),()]
avg = []

directory = r"C:\Users\Josh\Documents\PCG\data\dataphotos\debug"


#program to run and extract point cloud database from sample objects

for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    image = imread(f, as_gray = True)
    #obtain edge map
    image[image != 0] = 1
    #pooling operation is optional for performance
    image = skimage.measure.block_reduce(image, (16, 16), np.max)
    
    #convert non edge pixels to 0.5 or gray
    for r in range(int(image.size / image[0].size) - 1):
        for c in range(image[0].size - 1):
            if(r == image.size / image[0].size or r == 0 or c == 0 or c == image[0].size):
                continue
            elif(image[r + 1][c] == 0 or image[r][c - 1] == 0 or image[r][c + 1] == 0 or image[r - 1][c] == 0):
                continue
            else:
                image[r][c] = 0.5
    
    #gray pixels to black
    image[image == 0.5] = 0
    
    #plot vertices
    if("start" in f):
        #case for the first image that doesn't rotate
        for r in range(int(image.size/image[0].size) - 1):
            for c in range(image[0].size - 1):
                if(image[r][c] == 1):
                    count += 1
                    xm=(c *  0.0065) / 185.324
                    xtrue = xm / blendconst
                    ym = ((image.size / image[0].size - r) * 0.0065) / 185.324
                    ytrue = ym / blendconst
                    vertices.append((xtrue, 0, ytrue))
                     
    else:
        #all other images need to be rotated by their angular offset
        filenum = int("".join(re.findall(r'\d+', f)))
        theta = filenum * degrees
        for r in range(int(image.size / image[0].size) - 1):
            for c in range(image[0].size - 1):
                if(image[r][c] == 1):
                    count+=1                    
                    origin=[(image[0].size+1) / 2, (image.size / image[0].size + 1) / 2] 
                    xt = (c-origin[0]) * cos(math.radians(theta)) + origin[0]
                    yt = (c-origin[0]) * sin(math.radians(theta))
                    
                    xm = (xt *  0.0065) / 185.324
                    xtrue = xm / blendconst
                    ym = (yt * 0.0065) / 185.324
                    ytrue = ym/blendconst
                    zm = ((image.size / image[0].size - r) * 0.0065) / 185.324
                    ztrue = zm / blendconst
                    vertices.append((xtrue, ytrue, ztrue))
    avg.append(count)
#get average number of vertices per image
sum = 0
for x in avg:
    sum += x
print(sum / len(avg))

#create mesh
new_mesh=bpy.data.meshes.new("new_mesh")
new_mesh.from_pydata(vertices, edges, faces)
new_mesh.update()

#make object from the mesh
new_object = bpy.data.objects.new("new_object", new_mesh)

view_layer = bpy.context.view_layer
view_layer.active_layer_collection.collection.objects.link(new_object)
        
print(len(vertices))
