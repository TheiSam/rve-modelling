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

# Set desired height and width of image to be cropped to
req_height = 541
req_width = 541

# Path to folder where all images are stored
# image_folder_path = "C:/Users/TheiSam/Dropbox/UNI_WORK/ANSTO_Thesis/Image_Processing/Images_used"
image_folder_path = "C:/Users/TheiSam/Dropbox/UNI_WORK/ANSTO_Thesis/Image_Processing/void_images"

# 2D array to store stats of all the processed composite SEM images
all_stats = []

for image_name in os.listdir(image_folder_path):
    image_path = os.path.join(image_folder_path, image_name)
    # Ensure that it is a file
    if (os.path.isfile(image_path)):
        # image = cv.imread(image_path, cv.IMREAD_COLOR)
        crc_photo, image = circle_finding(image_path, req_height, req_width)

        voids, void_ratio = void_detection.find_voids(image_path, req_height, req_width)

        # ANALYSIS: Find the volume fraction of the processed image.
        num_crc = analysis.count_circles(crc_photo)
        fibre_radius = analysis.avg_radius(crc_photo)
        img_area = analysis.find_area(image)
        volume_fraction = analysis.find_vf(num_crc, fibre_radius, img_area)

        # ANALYSIS: Find the void ratio of the processed image.
        # total_void_area = analysis.total_circle_area(voids)
        # void_ratio = total_void_area / img_area

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

avg_vol_frac = sum_vol_fraction / num_images
avg_std_dist = sum_std_dist / num_images
avg_void_ratio = sum_void_ratio / num_images

print(F"THE VOID RATIO IS {avg_void_ratio} ")




RVE_bounds = (35, 35)
RVE_fib_radius = 3.5

void_radius = 2

# scaling_factor = 7
# RVE_bounds = np.round(np.divide(RVE_bounds, scaling_factor))
# RVE_bounds = RVE_bounds.astype(int)
# RVE_fib_radius = RVE_fib_radius / scaling_factor

print(RVE_bounds)
print(RVE_fib_radius)

################# STATS ################
print(F"{avg_vol_frac} and {avg_std_dist}")


generated_circles = generate.generate_RVE(RVE_bounds[0], RVE_bounds[1], RVE_fib_radius, avg_vol_frac, avg_std_dist, void_radius, avg_void_ratio)

fibre_list = generated_circles[0]
void_list = generated_circles[1]
generate.draw_circles(RVE_bounds[0], RVE_bounds[1], fibre_list, void_list)

np.savetxt("C:/Users/TheiSam/Dropbox/UNI_WORK/ANSTO_Thesis/Image_Processing/RVE_fibres.csv", fibre_list, delimiter = ",")
np.savetxt("C:/Users/TheiSam/Dropbox/UNI_WORK/ANSTO_Thesis/Image_Processing/RVE_voids.csv",  void_list, delimiter = ",")
