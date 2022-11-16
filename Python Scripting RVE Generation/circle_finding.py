
import numpy
import cv2
import preprocessing
import matplotlib.pyplot as plt
import analysis
import void_detection


######## THIS FILE CONTAINS THE FUNCTION TO FIND CIRCLES FROM AN SEM IMAGE ######

##### THIS FUNCTION CAN BE RUN SEPARATELY ON ONE IMAGE TO VISUALISE THE RESULTS. SIMPLY #####
###### CHANGE THE PATH IN THE MAIN FUNCTION BELOW TO THE DESIRED IMAGE PATH #######

# This function finds the circles from an SEM image.
def circle_finding(img_path, req_height, req_width):

    # Read in the image
    input_image = cv2.imread(img_path)

    # Crop the image
    image = input_image[0:req_height, 0:req_width, : ]

    # Process the image - convert to grayscale, equalize histogram and Gaussian blurring.
    output = image.copy()
    gray = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)
    hist = cv2.equalizeHist(gray)
    blur = cv2.GaussianBlur(hist, (31,31), cv2.BORDER_DEFAULT)

    processed_img = blur
    height, width = processed_img.shape[:2]

    # Set the parameters for the HoughCircles function.
    minR = round(width/38)
    maxR = round(width/28)
    minDis = round(width/18)

    # Circle detection using HoughCircles
    circles = cv2.HoughCircles(processed_img, cv2.HOUGH_GRADIENT, 1, minDis, param1=10, param2=8, minRadius=minR, maxRadius=maxR)

    # Find voids
    voids = void_detection.find_voids(img_path, req_height, req_width)[0]

    # Remove any circles that are actually voids from the fibre list.
    circles = analysis.remove_voids(circles, voids)

    # Convert circles to a numpy array. 
    circles = numpy.array([circles])

    # Both the circle list and the original image are returned.
    return [circles, output]


# This is simply to visualise the results of this function. Change the path below to your desired image.
# Running this file will run this function.
if __name__ == '__main__':

    # Path of image.
    path = 'C:/' # INSERT DESIRED PATH HERE

    # Desired height and width of the image to be cropped to.
    req_height = 541
    req_width = 541

    # Show the original image.
    image = cv2.imread(path)
    plt.figure();
    plt.suptitle('Collected Image', fontsize=20)
    plt.imshow(image, cmap='gray', vmin=0, vmax=255);
    plt.axis('off'); plt.axis('equal');
    plt.show();

    # Find circles and show found circles on image.
    circles, image = circle_finding(path, req_height, req_width)
    preprocessing.draw(image, circles, "Found Circles")
    plt.show()