from PIL import Image
import cv2


def edge_detection(img,threshold1=90, threshold2=180):
        grayscale_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        edges = cv2.Canny(grayscale_image, threshold1, threshold2)

        processed_image = Image.fromarray(edges)
        return processed_image

def color_manipulation(img):
        inverted_image = cv2.bitwise_not(img)
        processed_image = Image.fromarray(inverted_image)
        return processed_image