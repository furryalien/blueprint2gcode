#!/usr/bin/env python3
"""Debug floor plan processing"""

import cv2
import numpy as np
from PIL import Image

# Load image
img = Image.open('../test_data/test_images/test2_floor_plan.png')
img_gray = img.convert('L')
img_array = np.array(img_gray)

# Threshold
_, binary = cv2.threshold(img_array, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

# Skeletonize
skeleton = cv2.ximgproc.thinning(binary)

# Find contours
contours, _ = cv2.findContours(skeleton, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

print(f"Total contours found: {len(contours)}")
print("\nContour details:")
for i, contour in enumerate(contours):
    perimeter = cv2.arcLength(contour, False)
    # Get bounding box
    x, y, w, h = cv2.boundingRect(contour)
    print(f"  Contour {i+1}: {len(contour)} pts, perim={perimeter:.1f}px, bbox=({x},{y},{w}x{h})")

# Check stairs region specifically
stairs_region = skeleton[450:700, 100:200]
print(f"\nStairs region (y450-700, x100-200) non-zero pixels: {np.count_nonzero(stairs_region)}")

# Save debug images
cv2.imwrite('../test_data/test_output/debug_floor_binary.png', binary)
cv2.imwrite('../test_data/test_output/debug_floor_skeleton.png', skeleton)

# Highlight stairs area
debug_img = cv2.cvtColor(skeleton, cv2.COLOR_GRAY2BGR)
cv2.rectangle(debug_img, (100, 450), (200, 700), (0, 255, 0), 2)
cv2.imwrite('../test_data/test_output/debug_floor_stairs_area.png', debug_img)

print("\nDebug images saved to test_output/")
