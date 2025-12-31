#!/usr/bin/env python3
"""Debug circuit image processing"""

import cv2
import numpy as np
from PIL import Image

# Load image
img = Image.open('../test_data/test_images/test5_circuit.png')
img_gray = img.convert('L')
img_array = np.array(img_gray)

# Threshold
_, binary = cv2.threshold(img_array, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

# Dilate
kernel = np.ones((2, 2), np.uint8)
dilated = cv2.dilate(binary, kernel, iterations=1)

# Skeletonize
skeleton = cv2.ximgproc.thinning(dilated)

# Find contours
contours, _ = cv2.findContours(skeleton, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

print(f"Total contours found: {len(contours)}")
print("\nContour details:")
for i, contour in enumerate(contours):
    perimeter = cv2.arcLength(contour, False)
    area = cv2.contourArea(contour)
    print(f"  Contour {i+1}: {len(contour)} points, perimeter={perimeter:.1f}px, area={area:.1f}px²")

# Save debug images
cv2.imwrite('../test_data/test_output/debug_binary.png', binary)
cv2.imwrite('../test_data/test_output/debug_dilated.png', dilated)
cv2.imwrite('../test_data/test_output/debug_skeleton.png', skeleton)

# Draw contours on image for visualization
debug_img = cv2.cvtColor(img_array, cv2.COLOR_GRAY2BGR)
cv2.drawContours(debug_img, contours, -1, (0, 255, 0), 1)
cv2.imwrite('../test_data/test_output/debug_contours.png', debug_img)

print("\nDebug images saved to test_output/")
print("  debug_binary.png - thresholded image")
print("  debug_dilated.png - after dilation")
print("  debug_skeleton.png - skeletonized")
print("  debug_contours.png - detected contours highlighted")
