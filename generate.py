from ast import For
from os import remove
import random
from re import I
from turtle import color
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import analysis
import math

# Given boundary dimensions and number of fibres, calculate required fibre radius
def calculate_fib_radius(height, width, vol_fraction, num_fibres):
    total_fib_area = vol_fraction * height * width
    fib_area = total_fib_area / num_fibres
    fib_radius = math.sqrt(fib_area / math.pi)
    return fib_radius

# Given boundary dimensions and fibre radius, calculate required number of fibres.
def calculate_num_fibres(height, width, vol_fraction, fib_radius):
    total_fib_area = vol_fraction * height * width
    fib_area = math.pi * fib_radius * fib_radius
    num_fibres = round(total_fib_area / fib_area)
    return num_fibres 



# Mirror circles that cross the bounds of the RVE to the other side of the boundary.
def mirror_boundary_circle(circle, height, width):
    circles = [circle]

    x = circle[0]
    y = circle[1]
    r = circle[2]

    if x + r > width:
        x_new = x - width
        circles.append([x_new, y, r])
    if x - r < 0:
        x_new = x + width
        circles.append([x_new, y, r])
    if y + r > height:
        y_new = y - height
        circles.append([x, y_new, r])
    if y - r < 0:
        y_new = y + height
        circles.append([x, y_new, r])
    if x + r > width and y + r > height:
        return False 
        # x_new = x - width
        # y_new = y - height
        # circles.append([x_new, y_new, r])
    if x + r > width and y - r < 0:
        return False 
        # x_new = x - width
        # y_new = y + height
        # circles.append([x_new, y_new, r])
    if x - r < 0 and y + r > height:
        return False 
        # x_new = x + width
        # y_new = y - height
        # circles.append([x_new, y_new, r])
    if x - r < 0 and y - r < 0:
        return False 
        # x_new = x + width
        # y_new = y + height
        # circles.append([x_new, y_new, r])
    if x + r > width and (x + r - width < 0.25 * r or x + r - width > 0.75 * r):
        return False
    if x - r < 0 and (abs(x - r) < 0.25 * r or abs(x - r) > 0.75 * r):
        return False
    if y + r > height and (y + r - height < 0.25 * r or y + r - height > 0.75 * r):
        return False
    if y - r < 0 and (abs(y - r) < 0.25 * r or abs(y - r) > 0.75 * r):
        return False

    

    return circles

# Random sequential absorption algorithm
def generate_RVE(height, width, fib_radius, vol_fraction, standard_distance, void_radius, void_ratio):

    similar_distribution = False
    filled_area = 0;

    while(not similar_distribution):
        circle_area = math.pi * fib_radius * fib_radius
        required_area = vol_fraction * height * width
        fibres = []
        filled_area = 0
        counter = 0

        void_area = math.pi * void_radius * void_radius
        required_void_area = void_ratio * height * width
        voids = []
        filled_void_area = 0

        # While volume fraction is not reached:
        while filled_area < 0.95 * required_area:
            valid_circle = True
            # Generate a random circle within the height and width. Mirror it if necessary.
            x_centre = random.randint(0, width)
            y_centre = random.randint(0, height)
            circle = [x_centre, y_centre, fib_radius]
            counter += 1
            if counter == 200000:
                break

            if mirror_boundary_circle(circle, height, width) == False:
                continue

            # Mirror circle if it is out of bounds
            mirrored_circles = mirror_boundary_circle(circle, height, width)
            
            # If circle overlaps with another circle, remove the circle.
            for circle in mirrored_circles: 
                x_centre = circle[0]
                y_centre = circle[1]
                curr_radius = circle[2]
                if analysis.is_any_intersecting(x_centre, y_centre, curr_radius, fibres, 0.2):
                    valid_circle = False
                    
            if valid_circle:
                # Add the circle/s if it does not intersect
                for circle in mirrored_circles:
                    fibres.append(circle)
                # Need to update filled _area
                filled_area += circle_area

        # print(F"The filled area is {filled_area}")

        if counter >= 200000:
            continue
            
        # Check that the generated RVE has a similar standard distance
        SD_RVE = analysis.standard_distance(fibres)
        scaled_SD = analysis.scaled_SD(SD_RVE, height, width)
        if (scaled_SD < 1.1 * standard_distance and scaled_SD > 0.9 * standard_distance):
            similar_distribution = True
        
        # Generate voids
        while filled_void_area < 0.95 * required_void_area:
            # Generate a random circle within the height and width.
            x_centre = random.randint(0, width)
            y_centre = random.randint(0, height)
            void = [x_centre, y_centre, void_radius]

            # Check that the void does not go out of bounds
            if (x_centre + void_radius >= width or x_centre - void_radius <= 0 or y_centre + void_radius >= height or y_centre - void_radius <= 0):
                continue

            # If void overlaps with another circle, remove the circle.
            if analysis.is_any_intersecting(x_centre, y_centre, void_radius, fibres, 0) or analysis.is_any_intersecting(x_centre, y_centre, void_radius, voids, 0):
                continue

            # Otherwise add the void
            voids.append(void)
            filled_void_area += void_area
        
    print(F"The scaled SD area is {scaled_SD} and the fibre volume ratio is {filled_area / (height * width)}")

    return [fibres, voids]


def draw_circles(height, width, fibre_list, void_list):
    plt.axis([-0.5 * width, 1.5 * width, -0.5 * height , 1.5 * height])
    plt.axis("equal")
    plt.suptitle("Generated RVE", fontsize=25)
    rect = patches.Rectangle((0, 0), width, height, linewidth=1, edgecolor='r', facecolor='none')
    plt.gca().add_artist(rect)

    for fibre in fibre_list:
        c = plt.Circle((fibre[0], fibre[1]), radius = fibre[2], color='blue')
        plt.gca().add_artist(c)

    for void in void_list:
        c = plt.Circle((void[0], void[1]), radius = void[2], color='black')
        plt.gca().add_artist(c)

    plt.show()

''''
        # Check that the covariance matrix of the generated RVE has a similar trace
        circles_cov_matrix = analysis.cov(circles)
        scaled_cov = analysis.scaled_cov(circles_cov_matrix, height, width)

        # trace_RVE = analysis.trace(scaled_cov)
        # if (trace_RVE < 1.2 * trace and trace_RVE > 0.8 * trace):
        #     similar_trace = True
        max_eig_RVE = analysis.max_eig(scaled_cov)
        if (max_eig_RVE < 1.2 * max_eig and max_eig_RVE > 0.8 * max_eig):
            similar_max_eig = True

        # similar_distribution = True
        # similar_trace = True
        similar_max_eig = True

'''
    
    # with open("spatial_stats.txt", "a") as output_file:
    #     print("SSSSSSSSSSSSSSSSSSSSSS", file = output_file)
    #     print("SSSSSSSSSSSSSSSSSSSSSS", file = output_file)
    #     print("SSSSSSSSSSSSSSSSSSSSSS", file = output_file)
    #     print("SSSSSSSSSSSSSSSSSSSSSS", file = output_file)
    #     print("STANDARD DISTANCE BELOW", file = output_file)
    #     print(SD_RVE, file = output_file)
    #     print("SCALED STANDARD DISTANCE BELOW", file = output_file)
    #     print(scaled_SD, file = output_file)
    #     print("SCALED COVARIANCE MATRIX BELOW", file = output_file)
    #     print(scaled_cov, file = output_file)
    #     print("RVE TRACE BELOW", file = output_file)
    #     print(trace_RVE, file = output_file)
    #     print("volume_fraction BELOW", file = output_file)
    #     print(filled_area / (height * width), file = output_file)
    #     print("max EIG", file = output_file)
    #     print(max_eig_RVE, file = output_file)
    #     output_file.close
        # print(F"{scaled_SD} and {scaled_SD}")

'''             
# Random sequential absorption algorithm
def generate_RVE(height, width, radius, vol_fraction, standard_distance):

    similar_distribution = False
    filled_area = 0;

    while(not similar_distribution):
        circle_area = math.pi * radius * radius
        required_area = vol_fraction * height * width

        print(F"The required area is {required_area}")

        circles = []
        filled_area = 0

        counter = 0

        # While volume fraction is not reached:
        while filled_area < 0.9 * required_area:
            # Generate a random circle within the height and width. Mirror it if necessary.
            x_centre = random.randint(0, width)
            y_centre = random.randint(0, height)
            circle = [x_centre, y_centre, radius]
            counter += 1
            if counter == 200000:
                break
            # Check that the circle does not go out of bounds
            if (x_centre + radius >= width or x_centre - radius <= 0 or y_centre + radius >= height or y_centre - radius <= 0):
                # Mirror circles
                # Check whether they overlap
                continue
            
            # If circle overlaps with another circle, remove the circle.
            if is_any_intersecting(x_centre, y_centre, radius, circles):
                continue
            
            # Otherwise add the circle
            circles.append(circle)
            # Append mirrored circle if exists
            filled_area += circle_area


        print(F"The filled area is {filled_area}")


        if counter >= 200000:
            continue
            


        # Check that the generated RVE has a similar standard distance
        SD_RVE = analysis.standard_distance(circles)
        scaled_SD = analysis.scaled_SD(SD_RVE, height, width)
        if (scaled_SD < 1.25 * standard_distance and scaled_SD > 0.75 * standard_distance):
            similar_distribution = True
        
        print(F"The scaled SD area is {scaled_SD} and the fibre volume ratio is {filled_area / (height * width)}")

        # similar_distribution = True
    return circles

'''