import cv2
import numpy as np
from PIL import Image


def edge_detection(img,threshold1=90, threshold2=180):
    grayscale_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    edges = cv2.Canny(grayscale_image, threshold1, threshold2)

    processed_image = Image.fromarray(edges)
    return processed_image

def color_manipulation(img):
        inverted_image = cv2.bitwise_not(img)
        processed_image = Image.fromarray(inverted_image)
        return processed_image


def detect_corners(image):
    image_array = np.array(image)
    if len(image_array.shape) == 3 and image_array.shape[2] == 3:
        gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
    else:
        gray = image_array.copy()  
    dst = cv2.cornerHarris(gray, blockSize=2, ksize=3, k=0.04)
    dst = cv2.dilate(dst, None)
    ret, thresh = cv2.threshold(dst, 0.1*dst.max(), 255, cv2.THRESH_BINARY)
    corners = np.argwhere(thresh == 255)
    image_with_corners = image_array.copy()  
    for corner in corners:
        x, y = corner[0], corner[1]
        cv2.circle(image_with_corners, (x, y), 5, (0, 0, 255), -1)
    processed_image = Image.fromarray(image_with_corners)
    return processed_image

def sift_feature_detection(image):

    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    sift = cv2.SIFT_create()

    keypoints, descriptors = sift.detectAndCompute(gray, None)

    sift_image = cv2.drawKeypoints(image, keypoints, None, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    processed_image = Image.fromarray(sift_image)
    return processed_image


def denoise_image(image, h=10, templateWindowSize=7, searchWindowSize=21):

    denoised_image = cv2.fastNlMeansDenoisingColored(image, None, h, h, templateWindowSize, searchWindowSize)

    processed_image = Image.fromarray(denoised_image)
    return processed_image



def erosion(image, kernel_size=(5, 5), iterations=1):

    kernel = np.ones(kernel_size, np.uint8)

    eroded_image = cv2.erode(image, kernel, iterations=iterations)
    processed_image = Image.fromarray(eroded_image)
    return processed_image

def dilation(image, kernel_size=(5, 5), iterations=1):

    kernel = np.ones(kernel_size, np.uint8)

    dilated_image = cv2.dilate(image, kernel, iterations=iterations)

    processed_image = Image.fromarray(dilated_image)
    return processed_image
def histogram_equalization(image):

    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    equalized_image = cv2.equalizeHist(gray)

    processed_image = Image.fromarray(equalized_image)
    return processed_image

if __name__ == '__main__':
    img = cv2.imread('images/img.png')

    img_edge = np.array(edge_detection(img))
    success = cv2.imwrite('images/edge.png', img_edge)

    img_color = np.array(color_manipulation(img))
    success = cv2.imwrite('images/color.png', img_color)

    img_corner = np.array(detect_corners(img))
    success = cv2.imwrite('images/corner.png', img_corner)

    img_sift = np.array(sift_feature_detection(img))
    success = cv2.imwrite('images/sift.png', img_sift)

    img_denoise = np.array(denoise_image(img))
    success = cv2.imwrite('images/denoise.png', img_denoise)

    img_erosion = np.array(erosion(img))
    success = cv2.imwrite('images/erosion.png', img_erosion)

    img_dilation = np.array(dilation(img))
    success = cv2.imwrite('images/dilation.png', img_dilation)

    img_histogram = np.array(histogram_equalization(img))
    success = cv2.imwrite('images/histogram.png', img_histogram)
