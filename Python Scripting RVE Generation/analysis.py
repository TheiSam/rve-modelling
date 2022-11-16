import numpy as np
import math


###### THIS FILE CONTAINS HELPER FUNCTIONS TO ASSIST WITH STATISTICAL ANALYSIS AND RVE GENERATION ##########

# Find the area of an image
def find_area(image):
    return image.shape[0] * image.shape[1]

# Counts the number of circles in the list
def count_circles(crc_photo):
    return (crc_photo[0].shape)[0];

# Find average radius
def avg_radius(crc_photo):
    total_radius = 0
    for crc in crc_photo[0]:
        total_radius += crc[2]

    return (total_radius / count_circles(crc_photo))

# Calculate the fibre volume fraction based on average radius
def find_vf(num_crc, radius, img_area):
    crc_area = math.pi * radius * radius * num_crc
    return crc_area/img_area

# Finds the mean x or y coordinate of the circle list
def find_mean(circle_list, coordinate):
    num_points = len(circle_list)
    total_x = 0
    total_y = 0

    for circle in circle_list:
        total_x += circle[0]
        total_y += circle[1]

    mean_x = total_x / num_points
    mean_y = total_y / num_points

    if coordinate == 'x':
        return mean_x
    if coordinate == 'y':
        return mean_y
    
# Make function to quanitfy the spatial distribution. Calculate the standard distance
def standard_distance(circle_list):

    mean_x = find_mean(circle_list, 'x')
    mean_y = find_mean(circle_list, 'y')

    sum_var_x = 0
    sum_var_y = 0

    for circle in circle_list:
        sum_var_x += (circle[0] - mean_x) ** 2
        sum_var_y += (circle[1] - mean_y) ** 2
    
    SD = math.sqrt((sum_var_x + sum_var_y) / len(circle_list))
    return SD

# Find the scaled standard_distance
def scaled_SD(standard_distance, height, width):
    scaling_factor = math.sqrt(height * width)
    return standard_distance / scaling_factor

# Check if two circles are intersecting. The buffer represents the minimum space between circles.
# Set buffer = 0 if circles are allowed to touch
def is_intersecting(x_1, y_1, r_1, x_2, y_2, r_2, buffer):
    dist = math.sqrt((x_1 - x_2) * (x_1 - x_2) + (y_1 - y_2) * (y_1 - y_2))
    radius_sum = (r_1 + r_2)
    # Return whether circles intersecting
    return radius_sum >= dist - buffer
  

# Check if circle is intersecting with any other circle in a list of circles
def is_any_intersecting(x, y, r, circle_list, buffer):
    for circle in circle_list:
        if is_intersecting(x, y, r, circle[0], circle[1], circle[2], buffer):
            return True
    return False

# Checks a list of fibres to see if any of them are voids. Removes voids from fibre list.
# Returns the new fibre list without voids.
def remove_voids(fibre_list, void_list):
    cleaned_fibre_list = []
    for fibre in fibre_list[0]:
        x_fibre = fibre[0]
        y_fibre = fibre[1]
        r_fibre = fibre[2]

        if not np.any( [is_intersecting(x_fibre, y_fibre, r_fibre, x, y, r, 0) for x, y, r in void_list] ):
            cleaned_fibre_list.append(fibre)
            
    return np.asarray(cleaned_fibre_list)

# Calculate the total circle area of a circle list.
def total_circle_area(circles):
    total_area = 0
    for circle in circles:
        total_area += math.pi * (circle[2] ** 2)

    return total_area

# Check if an ellipse and a cricle are intersecting. 
def is_ellipse_circle_intersecting(ellipse, circle):
    # a and b represent the two radii of the ellipse
    a = ellipse[2]
    b = ellipse[3]
    major_radius = a if a > b else b

    # Find distance between centres
    x_1 = ellipse[0]
    y_1 = ellipse[1]
    x_2 = circle[0]
    y_2 = circle[1]
    dist = math.sqrt((x_1 - x_2) * (x_1 - x_2) + (y_1 - y_2) * (y_1 - y_2))

    circle_radius = circle[2]

    return dist < major_radius + circle_radius
    
# Check if ellipse is intersecting with any circle in a list of circles
def is_any_ellipse_circle_intersecting(ellipse, circle_list):
    for circle in circle_list:
        if is_ellipse_circle_intersecting(ellipse, circle):
            return True
    return False

# Check if an ellipse and a cricle are intersecting. 
def is_ellipse_ellipse_intersecting(ellipse_1, ellipse_2):
    # a and b represent the two radii of the ellipse
    a = ellipse_1[2]
    b = ellipse_1[3]
    major_radius_1 = a if a > b else b

    # a and b represent the two radii of the ellipse
    a = ellipse_2[2]
    b = ellipse_2[3]
    major_radius_2 = a if a > b else b

    # Find distance between centres
    x_1 = ellipse_1[0]
    y_1 = ellipse_1[1]
    x_2 = ellipse_2[0]
    y_2 = ellipse_2[1]

    dist = math.sqrt((x_1 - x_2) * (x_1 - x_2) + (y_1 - y_2) * (y_1 - y_2))

    return dist < major_radius_1 + major_radius_2
    
# Check if ellipse is intersecting with any circle in a list of circles
def is_any_ellipse_ellipse_intersecting(ellipse_1, ellipse_list):
    for ellipse_2 in ellipse_list:
        if is_ellipse_ellipse_intersecting(ellipse_1, ellipse_2):
            return True
    return False