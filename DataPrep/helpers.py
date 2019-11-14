
"""
File: Helpers.py
Authors Jared Galloway, Nick Wagner, Annie Wang
Date: 11/20/2019

This file contains all helpful python
functions for scripts included in synapse detection.
"""

##############################################################################

import os
import sys

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from skimage.draw import circle
import cv2

##############################################################################

# UNDER CONSTRUCTION
def dot_click_annoation_file_to_pixelmap(anno_file,
                                                width,
                                                height,
                                                dot_radius):
    """
    This function takes in an csv image anno which has the
    row format: filepath, top x, top y, bottom x, bottom y. no header.
    
    

    width, and height represent the total size of the annotated image.
    dot_radius is the size the of the circle centered around a clicked 
    synapse. 
 
    EX INPUT

    L1-D01-g.bmp,583,247,591,255,synapse
    L1-D01-g.bmp,589,256,597,264,synapse
    L1-D01-g.bmp,559,269,567,277,synapse
    L1-D01-g.bmp,592,267,600,275,synapse
    L1-D01-g.bmp,635,264,643,272,synapse
    L1-D01-g.bmp,607,281,615,289,synapse
    L1-D01-g.bmp,595,284,603,292,synapse

    the function will return a 2-dimentional binary numpy ndarray object 
    with the shape (width,height). 1's represent annotated images 
    
    """

    # initialize a pixelmap
    pixelmap = np.zeros([width,height], dtype=np.uint8)

    # draw ones using skimage circle()
    # https://scikit-image.org/docs/dev/api/skimage.draw.html
    # skimage.draw.circle
    for line in open(anno_file,"r"):

        # [filepath, top x, top y, bottom x, bottom y]
        anno = line.strip().split(',')
       
        # these should be the original x, and y's when given a bbox. 
        mid_x = (int(anno[1]) + int(anno[3])) // 2
        mid_y = (int(anno[2]) + int(anno[4])) // 2

        assert(0 <= mid_x <= width)
        assert(0 <= mid_y <= height)

        # yay skimage!
        rr,cc = circle(mid_x, mid_y, dot_radius)

        # cut out extreneous indices.
        count = 0
        for i in range(len(rr)):
            if (rr[i-count] >= 1024 or rr[i-count] < 0):
                rr = np.delete(rr, i-count)
                cc = np.delete(cc, i-count)
                count += 1
            if (cc[i-count] >= 1024 or cc[i-count] < 0):
                rr = np.delete(rr, i-count)
                cc = np.delete(cc, i-count)
                count += 1
         
        # set pixel values.
        pixelmap[rr, cc] = 1

    return pixelmap

##############################################################################

def symquant_to_pixelmap_stub(anno_format,
                                                width,
                                                height,
                                                dot_radius):
    """
    TODO: Impliment and remove stub :)
    
    This function should take in the output from SynQuant
    https://www.biorxiv.org/content/10.1101/538769v1
    and convert it to a pixelmap 

        
    """

    
    pass

##############################################################################

def colocaliztion(pixelmap_list):
    """
    This function takes in a list of pixelmaps and performs bitwise operations 
    to find the spots that have pixels in common (colocalization)


    This function is dependent on the length of the pixelmap_list. If the length is
    just two then it will compute the bitwise-AND, and find the spots of colocalization
    for those two images. If the length is three then it will find all three sets of 
    image colocalization and bitwise-OR those together.


    This function will return a 2-dimentional binary numpy ndarray object 
    with the shape (1024,1024). 1's represent any point of colocalization between the
    images.
    """
    pixelmap_list = np.array(pixelmap_list)

    SHAPE = pixelmap_list[0].shape
    COLOCALIZED = np.zeros((SHAPE[0],SHAPE[1]), dtype=np.uint8)

    # if(len(pixelmap_list) == 1):   # The user did not provide enough information to calculate the colocalization
    #     return "Please provide a list of at least two pixelmaps."
    assert(len(pixelmap_list) >= 2)
    
    
    # Case where two pixelmaps are provided
    if(len(pixelmap_list) == 2):
        if(pixelmap_list[0].shape != pixelmap_list[1].shape):
            return "Please provide pixelmaps with the same dimensions"
        
        # performs a bitwise-AND to keep only the pixels that share a spot of colocalizaiton
        COLOCALIZED = np.bitwise_and(pixelmap_list[0], pixelmap_list[1])
    

    # Case where three pixelmaps are provided
    if(len(pixelmap_list) == 3):
        if(pixelmap_list[0].shape != pixelmap_list[1].shape or pixelmap_list[0].shape != pixelmap_list[2].shape):
            return "Please provide pixelmaps with the same dimensions"

        # performs three bitwise-ANDs to keep only the pixels that share a spot of colocalizaiton
        coloalized1 = np.bitwise_and(pixelmap_list[0], pixelmap_list[1])
        coloalized2 = np.bitwise_and(pixelmap_list[0], pixelmap_list[2])
        coloalized3 = np.bitwise_and(pixelmap_list[1], pixelmap_list[2])

        # performs two bitwise-ORs to combine all three sets of colocalization
        COLOCALIZED = np.bitwise_or(coloalized1, coloalized2)
        COLOCALIZED = np.bitwise_or(COLOCALIZED, coloalized3)

    
    return COLOCALIZED

##############################################################################

def sub_patch_pixelmap(image_pixelmap, size=32, height=(256,1024), width=(256,768)):
    """
    This function allows the user to break up the given pixelmap into sub-patches. The 
    user can specify the area they would like to sub-patch as well as the size of
    the patch they would like to grab.

    image_pixelmap: numpy 2d array corresponding to the pixelmap to be sub-patched
    size: the SIZExSIZE chunk to be grabbed
    height: tuple specifying the y start and stop positions (start, stop)  
            DEFAULT: (256,1024)
    width: tuple specifying the x start and stop positions (start, stop)  
            DEFAULT: (256,768)
    
    This function will return a numpy ndarray of SIZExSIZE 2-dimentional binary numpy ndarrays
    """

    SUB_IMAGES = []    # initialize an array for holding the sub images

    for i in range(height[0],height[1],size):  # this for loop isolates only the region of the image specified in the parameters
        for j in range(width[0],width[1],size):
            temp_array = image_pixelmap[i:i+size,j:j+size] # grabbing SIZExSIZE chunks and storing them in an array
            SUB_IMAGES.append(temp_array)
    
    SUB_IMAGES = np.array(SUB_IMAGES)

    return SUB_IMAGES

##############################################################################

def empirical_prep(list_of_paths, size=32, height=(256,1024), width=(256,768)):
    """
    This function allows the user to break up the empirical images into sub images for 
    training or testing. The user can give as many paths to images as they would like in
    the list_of_paths parameter. The user can specify the area they would like to sub-image 
    as well as the size of the chunk they would like to grab.

    list_of_paths: list of strings corresponding to the paths of the images wanting to be
                sub-imaged
    size: the SIZExSIZE chunk to be grabbed
    height: tuple specifying the y start and stop positions (start, stop)  
            DEFAULT: (256,1024)
    width: tuple specifying the x start and stop positions (start, stop)  
            DEFAULT: (256,768)

    This function will return a list of numpy ndarrays, of which contain all of the sub-images
    for that given empirical image. There will be one item in the list for each empirical 
    image given
    """

    SUB_EMPIRICAL = []
    for num in range(len(list_of_paths)):
        pillow_opened_image = Image.open(list_of_paths[num])
        temp_sub_images = []
        for i in range(height[0],height[1],size):  # this for loop isolates only the region of the image specified in the parameters
            for j in range(width[0],width[1],size):
                temp_pic = pillow_opened_image.crop((i,j,i+size,j+size)) # grabbing SIZExSIZE chunks and storing them in an array
                temp_sub_images.append(temp_pic)
        SUB_EMPIRICAL.append(temp_sub_images)

    return SUB_EMPIRICAL

##############################################################################

# TODO impliment and remove stub :)
def f1_stub(pixelmap1, pixelmap2):
    """
    this function will take two pixelmaps (2d-ndarray)
    and return the f1 score defined as:
    
    f1 = 2 / ((1 / precision) + (1/ recall)).
    """

    pass








