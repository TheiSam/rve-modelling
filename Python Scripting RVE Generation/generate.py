import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import analysis
import math

######## THIS FILE CONTAINS THE FUNCTION TO GENERATE AND DRAW THE RVE. ########
####### SOME HELPER FUNCTIONS FOR THE GENERATION OF THE RVE ARE ALSO IN THIS FILE ######

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

    # Append a new circle that represents the circle being mirrored to the other side,
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

    # Circles cannot be on the corners for easier processing in ABAQUS.
    if x + r > width and y + r > height:
        return False 
    if x + r > width and y - r < 0:
        return False 
    if x - r < 0 and y + r > height:
        return False 
    if x - r < 0 and y - r < 0:
        return False 

    # At least 25% of the circle must be within the bounds. This is also for easier 
    # processing in ABAQUS.
    if x + r > width and (x + r - width < 0.25 * r or x + r - width > 0.75 * r):
        return False
    if x - r < 0 and (abs(x - r) < 0.25 * r or abs(x - r) > 0.75 * r):
        return False
    if y + r > height and (y + r - height < 0.25 * r or y + r - height > 0.75 * r):
        return False
    if y - r < 0 and (abs(y - r) < 0.25 * r or abs(y - r) > 0.75 * r):
        return False

    # Return the new circle list with both the original and the mirrored circle.
    return circles

# This function generates the RVE.
def generate_RVE(height, width, fib_radius, vol_fraction, standard_distance, void_dimensions, void_ratio, void_shape, min_fib_dist):

    similar_distribution = False
    filled_area = 0;

    # Ensure that spatial distribution of the final RVE is similar enough as desired. Otherwise,
    # rerun the function.
    while(not similar_distribution):
        circle_area = math.pi * fib_radius * fib_radius
        required_area = vol_fraction * height * width
        fibres = []
        filled_area = 0
        counter = 0

        required_void_area = void_ratio * height * width

        if void_shape == "circle":
            void_radius = void_dimensions[0]
            void_area = math.pi * void_radius * void_radius

        if void_shape == "ellipse":
            horizontal_radius = void_dimensions[0]
            vertical_radius = void_dimensions[1]
            ellipse_area = math.pi * horizontal_radius * vertical_radius

        voids = []
        filled_void_area = 0

        # While volume fraction is not reached:
        while filled_area < 0.95 * required_area:
            valid_circle = True
            # Generate a random circle within the height and width. Mirror it if necessary.
            x_centre = random.randint(0, width)
            y_centre = random.randint(0, height)
            circle = [x_centre, y_centre, fib_radius]

            # If counter reaches this high number, it means the algorithm  most likely
            # cannot find space to insert a new circle. In that case, simply restart
            # the process.
            counter += 1
            if counter == 200000:
                break

            # Circle is invalid.
            if mirror_boundary_circle(circle, height, width) == False:
                continue

            # Mirror circle if it is out of bounds
            mirrored_circles = mirror_boundary_circle(circle, height, width)
            
            # If circle overlaps, set the valid_circle flag to false.
            for circle in mirrored_circles: 
                x_centre = circle[0]
                y_centre = circle[1]
                curr_radius = circle[2]
                if analysis.is_any_intersecting(x_centre, y_centre, curr_radius, fibres, min_fib_dist):
                    valid_circle = False
                    
            if valid_circle:
                # Add the circle/s if it does not intersect
                for circle in mirrored_circles:
                    fibres.append(circle)
                # Need to update filled _area
                filled_area += circle_area

        if counter >= 200000:
            continue
            
        # Check that the generated RVE has a similar standard distance
        SD_RVE = analysis.standard_distance(fibres)
        scaled_SD = analysis.scaled_SD(SD_RVE, height, width)
        if (scaled_SD < 1.1 * standard_distance and scaled_SD > 0.9 * standard_distance):
            similar_distribution = True
        
        # Generate voids
        while filled_void_area < 0.95 * required_void_area:

            if void_shape == "circle":
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

            elif void_shape == "ellipse":
                # Generate a random ellipse within the height and width.
                # Note: An ellipse will be represented by x_centre, y_centre, horizontal_radius and vertical_radius.
                x_centre = random.randint(0, width)
                y_centre = random.randint(0, height)
                void = [x_centre, y_centre, horizontal_radius, vertical_radius]

                # Check that the void does not go out of bounds
                if (x_centre + horizontal_radius >= width or x_centre - horizontal_radius <= 0 or y_centre + vertical_radius >= height or y_centre - vertical_radius <= 0):
                    continue

                # If the void overlaps with a fibre or a void, remove the void.
                if analysis.is_any_ellipse_circle_intersecting(void, fibres) or analysis.is_any_ellipse_ellipse_intersecting(void, voids):
                    continue

                # Otherwise add the void
                voids.append(void)
                filled_void_area += ellipse_area


    # The RVE is represented by a list of fibre and void positions.
    return [fibres, voids]

# Draw the RVE
def draw_RVE(height, width, fibre_list, void_list, void_shape):
    plt.axis([-0.5 * width, 1.5 * width, -0.5 * height , 1.5 * height])
    plt.axis("equal")
    plt.suptitle("Generated RVE", fontsize=25)
    rect = patches.Rectangle((0, 0), width, height, linewidth=1, edgecolor='r', facecolor='none')
    plt.gca().add_artist(rect)

    # Draw fibres
    for fibre in fibre_list:
        c = plt.Circle((fibre[0], fibre[1]), radius = fibre[2], color='blue')
        plt.gca().add_artist(c)

    if void_shape == "circle":
        # Draw circular voids
        for void in void_list:
            c = plt.Circle((void[0], void[1]), radius = void[2], color='black')
            plt.gca().add_artist(c)

    if void_shape == "ellipse":
    # Draw elliptical voids
        for void in void_list:
            ellipse = patches.Ellipse(xy=(void[0], void[1]), width=void[2] * 2, height=void[3] * 2, color='black')
            plt.gca().add_artist(ellipse)

    plt.show()
