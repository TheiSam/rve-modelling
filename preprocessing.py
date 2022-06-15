from ast import For
from os import remove
from re import I
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
import math

# Function for drawing circles
def draw(image,circles,title):
    fig = plt.figure(figsize=(5, 5)) # fig, ax = plt.subplots()
    plt.suptitle(title, fontsize=35)
    plt.imshow(image, cmap='gray', vmin=0, vmax=255);
    for row in circles[0, :]:
     # draw the outer circle
     fig = plt.gcf();
     ax = fig.gca()
     circle = plt.Circle((row[0], row[1]), row[2], color='r', linewidth = 2, fill=False, clip_on = True)
     ax.add_artist(circle)
     plt.axis('off');
     plt.axis('equal'); plt.show(block=False);


# Replace the radius of every row in the list of circles. Give the function the
#crc_photo and the radius you want to replace it with.
def replace_radius(crc_photo, radius):
    for row in crc_photo[0]:
        row[2] = radius


