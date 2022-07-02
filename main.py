from ast import For
from audioop import avg
from os import remove
from re import I
import re
from turtle import circle
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
import math
import preprocessing
import analysis
import generate
import sys
import os
import void_detection
from circle_finding import circle_finding


### MAIN FILE THAT PUTS EVERYTHING TOGETHER. WILL GENERATE AN RVE FROM A GIVEN FOLDER OF IMAGES ###

######################### PARAMETERS TO BE CHANGED AS DESIRED ################################

# Set desired height and width of image to be cropped to
req_height = 541
req_width = 541

# Set the desired bounds, fibre radius and void dimensions of the RVE to be generated.
RVE_bounds = (35, 35)
RVE_fib_radius = 3.5

void_dimensions = [3, 2]  # For circle, void_dimensions = [radius]. For ellipse, void_dimensions = [horizontal_radius, vertical_radius]
void_shape = "ellipse"    # Either "circle" or "ellipse"

# Set this to True and the manual RVE parameters will be used for RVE generation.
# Set this to False and the RVE parameters will be derived from the image_folder_path.
set_parameters_manually = True

# Set RVE parameters manually. These parameters will be taken if set_parameters_manually = True
fibre_volume_ratio = 0      # Fibre volume ratio
std_dist = 0.4              # Standard distance (simialr to standard deviation) referring to spatial distribution of fibres.
void_ratio = 0              # Void ratio

# File and folder paths
# Specify path to a folder where the images to be read in are stored.
image_folder_path = "C:/Users/TheiSam/Dropbox/UNI_WORK/ANSTO_Thesis/Image_Processing/void_images"

# Specify path for fibre and void lists from the generated RVE to be saved to.
saved_fibre_list = "C:/Users/TheiSam/Dropbox/UNI_WORK/ANSTO_Thesis/Image_Processing/RVE_fibres.csv"
saved_void_list = "C:/Users/TheiSam/Dropbox/UNI_WORK/ANSTO_Thesis/Image_Processing/RVE_voids.csv"

############################## END PARAMETERS TO BE CHANGED AS DESIRED #########################

if (not set_parameters_manually):
    # 2D array to store stats of all the processed composite SEM images
    all_stats = []

    # Go through the folder of images.
    for image_name in os.listdir(image_folder_path):
        image_path = os.path.join(image_folder_path, image_name)
        # Ensure that it is a file.
        if (os.path.isfile(image_path)):

            # Find fibres
            crc_photo, image = circle_finding(image_path, req_height, req_width)

            # Find voids
            voids, void_ratio = void_detection.find_voids(image_path, req_height, req_width)

            # ANALYSIS: Find the volume fraction of the processed image.
            num_crc = analysis.count_circles(crc_photo)
            fibre_radius = analysis.avg_radius(crc_photo)
            img_area = analysis.find_area(image)
            volume_fraction = analysis.find_vf(num_crc, fibre_radius, img_area)

            img_dim = image.shape

            # Find the standard distance (spatial distribution measure) of the processed image
            standard_distance = analysis.standard_distance(crc_photo[0])
            scaled_SD = analysis.scaled_SD(standard_distance, img_dim[0], img_dim[1])

            # 1D array to store stats of the current processed image
            image_stats = [volume_fraction, scaled_SD, void_ratio]
            all_stats.append(image_stats)

    # Calculate average stats for final generated RVE
    sum_vol_fraction = 0
    sum_std_dist = 0
    sum_void_ratio = 0
    for stat in all_stats:
        sum_vol_fraction += stat[0]
        sum_std_dist += stat[1]
        sum_void_ratio += stat[2]

    num_images = len(all_stats)

    fibre_volume_ratio = sum_vol_fraction / num_images
    std_dist = sum_std_dist / num_images
    void_ratio = sum_void_ratio / num_images


# Generate the RVE
generated_circles = generate.generate_RVE(RVE_bounds[0], RVE_bounds[1], RVE_fib_radius, fibre_volume_ratio, std_dist, void_dimensions, void_ratio, void_shape)

# Show the generated RVE
fibre_list = generated_circles[0]
void_list = generated_circles[1]
generate.draw_RVE(RVE_bounds[0], RVE_bounds[1], fibre_list, void_list, void_shape)

# Save the fibre and void lists to the specified path.
np.savetxt(saved_fibre_list, fibre_list, delimiter = ",")

np.savetxt(saved_void_list, void_list, delimiter = ",")    

