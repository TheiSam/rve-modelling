
import cv2
import numpy as np
import preprocessing
import matplotlib.pyplot as plt



####### THIS FILE CONTAINS THE FUNCTION TO DETECT AND QUANTIFY VOIDS IN AN IMAGE ######

##### THIS FUNCTION CAN BE RUN SEPARATELY ON ONE IMAGE TO VISUALISE THE RESULTS. SIMPLY #####
###### CHANGE THE PATH IN THE MAIN FUNCTION BELOW TO THE DESIRED IMAGE PATH #######


def find_voids(img_path, req_height, req_width):

    # Read in and crop the image as required.
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    img = img[0:req_height, 0:req_width]

    # Binary threshold the image.
    ret,thresh2 = cv2.threshold(img,50,255,cv2.THRESH_BINARY)

    # Thresholded image.
    im = thresh2

    # Setup SimpleBlobDetector parameters.
    params = cv2.SimpleBlobDetector_Params()
    params.filterByArea = True
    params.minArea = 200
    params.filterByConvexity = True
    params.minConvexity = 0
    params.maxConvexity = 1


    # Detect black blobs
    detector = cv2.SimpleBlobDetector_create(params)
    keypoints = detector.detect(im)
    im_with_keypoints = cv2.drawKeypoints(im, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)


    # 2D array to store void locations and size
    voids = []

    # Add found voids to voids array
    for keypoint in keypoints:
        x = keypoint.pt[0]
        y = keypoint.pt[1]
        r = keypoint.size / 2
        void = [x, y, r]
        voids.append(void)

    #Calculate the total number of black pixels.
    total_pixels = thresh2.shape[0] * thresh2.shape[1]
    total_white_pixels = thresh2.sum() / 255
    total_black_pixels = total_pixels - total_white_pixels
    void_ratio = total_black_pixels / total_pixels

    voids = np.array(voids)

    # Return a list of circles approximately representing void location and size, and the void ratio. 
    return [voids, void_ratio]

# This is simply to visualise the results of this function. Change the path below to your desired image.
# Running this file will run this function.
if __name__ == '__main__':
    path = "C:/Users/TheiSam/Dropbox/UNI_WORK/ANSTO_Thesis/Image_Processing/Images_new/cc1_33.tif"
    image = cv2.imread(path)

    voids, ratio = find_voids(path, 10000, 10000)
    preprocessing.draw(image, np.array([voids]), "Approximate void locations and size")
    plt.show()