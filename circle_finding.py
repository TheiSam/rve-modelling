

import re
import numpy
import cv2
import preprocessing
import matplotlib.pyplot as plt
import analysis
import void_detection



def circle_finding(img_path, req_height, req_width):

  

    input_image = cv2.imread(img_path)

    image = input_image[0:req_height, 0:req_width, : ]

    output = image.copy()

    gray = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)

    hist = cv2.equalizeHist(gray)

    blur = cv2.GaussianBlur(hist, (31,31), cv2.BORDER_DEFAULT)

    processed_img = blur
    height, width = processed_img.shape[:2]

    minR = round(width/38)
    maxR = round(width/28)
    minDis = round(width/18)
    # minR = 50
    # maxR = 60
    # minDis = 70



    circles = cv2.HoughCircles(processed_img, cv2.HOUGH_GRADIENT, 1, minDis, param1=10, param2=8, minRadius=minR, maxRadius=maxR)
    # circles = cv2.HoughCircles(processed_img, cv2.HOUGH_GRADIENT, 1, minDis, param1=20, param2=15, minRadius=minR, maxRadius=maxR)

    # Draw found circles on the image.
    # if circles is not None:
    #     circles = numpy.round(circles[0, :]).astype("int")
    #     circles = numpy.round(circles).astype("int")
    #     for (x, y, r) in circles:
    #         cv2.circle(output, (x, y), r, (0, 255, 0), 2)
    #         #cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
    # cv2.imshow("result", numpy.hstack([image, output]))
    # cv2.waitKey()

    print(f' ORIGINAL CIRCLE SHAPE {circles.shape}')

    # Find voids
    voids = void_detection.find_voids(img_path, req_height, req_width)[0]

    # Remove any circles that are actually voids from the fibre list.
    circles = analysis.remove_voids(circles, voids)

    circles = numpy.array([circles])
    # print(f' AFTER CIRCLE SHAPE {numpy.array([circles]).shape}')

    return [circles, output]

if __name__ == '__main__':
    path = 'C:/Users/TheiSam/Dropbox/UNI_WORK/ANSTO_Thesis/Image_Processing/Images_new/cc1_33.tif'
    # path = 'D:/TheiSam/Thesis_Images/TIF16-bit/Electron_Image_368.tif'
    # path = 'C:/Users/TheiSam/Dropbox/UNI_WORK/ANSTO_Thesis/Image_Processing/Images_misc/new_image.jpg'
    image = cv2.imread(path)
    print(image.shape)


    plt.figure();
    plt.suptitle('Collected Image', fontsize=20)
    plt.imshow(image, cmap='gray', vmin=0, vmax=255);
    plt.axis('off'); plt.axis('equal');
    plt.show();


    circles, image = circle_finding(path, 541, 541)
    preprocessing.draw(image, circles, "Found Circles")

    plt.show()

    num_crc = analysis.count_circles(circles)
    print(num_crc)
    fibre_radius = analysis.avg_radius(circles)
    img_area = analysis.find_area(image)
    volume_fraction = analysis.find_vf(num_crc, fibre_radius, img_area)
    print(volume_fraction)

    img_dim = image.shape

    # Find the standard distance (spatial distribution measure) of the processed image
    standard_distance = analysis.standard_distance(circles[0])
    scaled_SD = analysis.scaled_SD(standard_distance, img_dim[0], img_dim[1])
    print(scaled_SD)








    # input_image = cv2.imread('C:/Users/TheiSam/Dropbox/UNI_WORK/ANSTO_Thesis/Image_Processing/Images_misc/cc1_30.jpg')
    # input_image = cv2.imread('C:/Users/TheiSam/Dropbox/UNI_WORK/ANSTO_Thesis/Image_Processing/Images_new/cc1_30.tif')

    # minR = round(width/38)
    # maxR = round(width/28)

    # Draw found circles on the image.
    # if circles is not None:
    #     circles = numpy.round(circles[0, :]).astype("int")
    #     circles = numpy.round(circles).astype("int")
    #     for (x, y, r) in circles:
    #         cv2.circle(output, (x, y), r, (0, 255, 0), 2)
    #         #cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
    # cv2.imshow("result", numpy.hstack([image, output]))
    # cv2.waitKey()


    # circles = cv2.HoughCircles(blur, cv2.HOUGH_GRADIENT, 1, minDis, param1=10, param2=7, minRadius=minR, maxRadius=maxR)
    


    # with open("circles.txt", "w") as output:
    #     print(circles, file = output)



''' RELEVANT PARAMETERS
For the cc1 photos of 600 magnification:
    req_height = 541
    req_width = 541

    minR = round(width/38)
    maxR = round(width/28)
    minDis = round(width/18)

    circles = cv2.HoughCircles(processed_img, cv2.HOUGH_GRADIENT, 1, minDis, param1=20, param2=15, minRadius=minR, maxRadius=maxR)



For the TIF16_bit images

    req_height = 1536
    req_width = 2048

    minR = 50
    maxR = 60
    minDis = 70

    circles = cv2.HoughCircles(processed_img, cv2.HOUGH_GRADIENT, 1, minDis, param1=20, param2=15, minRadius=minR, maxRadius=maxR)






'''