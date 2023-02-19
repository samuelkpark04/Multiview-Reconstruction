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

# Data for generating mesh.
vertices = []
edges = []
faces = []
vert_count = 0

# Fixed constants.
degrees_offset = 6
blend_const = 0.0651084055


# Directory to cross-sections.
dirname = os.path.dirname(__file__)
file_path = os.path.join(dirname, '../data/cross-sections')




def identify_verticies(f_directory, pool_check, pool_resolution):

    # Keep track of the number of vertices per cross-section

    # Traverse through all images in the f_directory.
    for img_name in os.listdir(f_directory):

        f = os.path.join(f_directory, img_name)

        # Read in image as a grayscale.
        img = imread(f, as_gray, img_name)

        # Normalize into edge map using 0.5 as a threshold.
        img[img < 0.5] = 0
        img[img >= 0.5] = 1

        # Optional pooling for performance.
        if pool_check:
            img = skimage.measure.block_reduce(img, (pool_resolution, pool_resolution), np.max)
        
        # Gather image metrics
        width = img[0].size - 3
        height = (img.size / width) - (3 + 50)
        u_origin = ((width + 1) // 2, (height + 1) // 2)
        img_num = int(img_name[len(img_name) - 5])

        # Keep track of current cross-section as well as average previous differences in z value
        curr_cross_section = 0
        
        # Traverse through individual pixels of image, not including border pixels.
        for u in width:
            for v in height:
                # Check if pixel is an edge
                if img[u-1][v] != img[u+1][v] and (curr_cross_section <= vert_count or vert_count == 0):
                    add_verticies(u, v, u_origin, img_num)
                    curr_cross_section += 1 

        if vert_count == 0:
            vert_count = curr_cross_section


def add_verticies(u_real, v_real, origin, img_num):
    
    # Get the radius of the cylindrical coordinate and degree offset
    r = origin[0] - abs(u_real)
    deg = degrees_offset * img_num

    # Calculate relative x, y, z coordinates
    x = r * cos(math.radians(deg)) * 0.0065 / 185.324
    y = r * sin(math.radians(deg)) * 0.0065 / 185.324
    z = (v_real - origin) * 0.0065 / 185.324

    # Append vertice
    vertices.append((x, y, z))

def gen_edges():

    vert_length = len(vertices)

    # Create edges between geometrically adjacent verticies
    for index in range(0, vert_length, vert_count):
        if index >= (len(vertices) - vert_count):
            edges.append((vertices[index], vertices[index - (vert_length - vert_count)]))
        else:
            edges.append((vertices[index], vertices[index + vert_count]))

def gen_model():

    # Create Mesh
    new_mesh = bpy.data.meshes.new("new_mesh")
    new_mesh.from_pydata(vertices, edges, faces)
    new_mesh.update()

    # Render mesh
    new_object = bpy.data.objects.new("new_object", new_mesh)
    view_layer = bpy.context.view_layer
    view_layer.active_layer_collection.collection.objects.link(new_object)


# main code

identify_verticies(file_path, 0, None)
gen_edges()
gen_model()













