import unittest
import cv2
import numpy as np
from PIL import Image
from numpy import testing

from Image_Preprocessing import *


def load_test_image(image_path="images/img.png"):
    """Loads an image for testing using OpenCV."""
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Failed to load test image: {image_path}")
    return image

def convert_to_pil_image(cv2_image):
    """Converts a OpenCV image to PIL format for compatibility."""
    return Image.fromarray(cv2_image)


class TestImageProcessing(unittest.TestCase):

    def setUp(self):
        self.test_image = load_test_image("images/img.png")  # Replace with your image path

    # Test edge_detection function
    def test_edge_detection(self):
        edges = edge_detection(self.test_image)
        self.assertIsInstance(edges, Image.Image)  # Check if output is a PIL Image

        # Additional tests for edge quality or specific threshold effects (optional)
    def test_edge_detection_res(self):
        expected = cv2.imread("images/edge.png", cv2.IMREAD_GRAYSCALE)
        edges = edge_detection(self.test_image)
        edges = np.array(edges)
        testing.assert_array_equal(edges, expected)

    # Test color_manipulation function
    def test_color_manipulation(self):
        inverted_image = color_manipulation(self.test_image)
        self.assertIsInstance(inverted_image, Image.Image)

        # Additional tests to verify color inversion (optional)

    def test_color_manipulation_res(self):
        expected = cv2.imread("images/color.png")
        inverted_image = color_manipulation(self.test_image)
        inverted_image = np.array(inverted_image)
        testing.assert_array_equal(inverted_image, expected)

    # Test detect_corners function (using both grayscale and color images)
    def test_detect_corners_grayscale(self):
        grayscale_image = cv2.cvtColor(self.test_image, cv2.COLOR_BGR2GRAY)
        corners_image = detect_corners(convert_to_pil_image(grayscale_image))
        self.assertIsInstance(corners_image, Image.Image)

    def test_detect_corners_grayscale_res(self):
        expected = cv2.imread("images/corner.png")
        corners_image = detect_corners(self.test_image)
        corners_image = np.array(corners_image)
        testing.assert_array_equal(corners_image, expected)

    def test_detect_corners_color(self):
        corners_image = detect_corners(convert_to_pil_image(self.test_image))
        self.assertIsInstance(corners_image, Image.Image)

    def test_detect_corners_color_res(self):
        expected = cv2.imread("images/corner.png")
        corners_image = detect_corners(self.test_image)
        corners_image = np.array(corners_image)
        testing.assert_array_equal(corners_image, expected)

    # Test sift_feature_detection function
    def test_sift_feature_detection(self):
        sift_image = sift_feature_detection(self.test_image)
        self.assertIsInstance(sift_image, Image.Image)

    # Test denoise_image function
    def test_denoise_image(self):
        denoised_image = denoise_image(self.test_image)
        self.assertIsInstance(denoised_image, Image.Image)

    def test_denoise_image_res(self):
        expected = cv2.imread("images/denoise.png")
        denoised_image = denoise_image(self.test_image)
        denoised_image = np.array(denoised_image)
        testing.assert_array_equal(denoised_image, expected)

    # Test erosion function
    def test_erosion(self):
        eroded_image = erosion(self.test_image)
        self.assertIsInstance(eroded_image, Image.Image)

    def test_erosion_res(self):
        expected = cv2.imread("images/erosion.png")
        eroded_image = erosion(self.test_image)
        eroded_image = np.array(eroded_image)
        testing.assert_array_equal(eroded_image, expected)

    # Test dilation function
    def test_dilation(self):
        dilated_image = dilation(self.test_image)
        self.assertIsInstance(dilated_image, Image.Image)

    def test_dilation_res(self):
        expected = cv2.imread("images/dilation.png")
        dilated_image = dilation(self.test_image)
        dilated_image = np.array(dilated_image)
        testing.assert_array_equal(dilated_image, expected)

    # Test histogram_equalization function
    def test_histogram_equalization(self):
        equalized_image = histogram_equalization(self.test_image)
        self.assertIsInstance(equalized_image, Image.Image)

    def test_histogram_equalization_res(self):
        expected = cv2.imread("images/histogram.png", cv2.IMREAD_GRAYSCALE)
        equalized_image = histogram_equalization(self.test_image)
        equalized_image = np.array(equalized_image)
        testing.assert_array_equal(equalized_image, expected)
