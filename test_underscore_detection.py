#!/usr/bin/env python3
"""Test underscore detection with the sample image"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2

# Create the test image that matches the user's attachment
# Numbers 1-5 with underscores of increasing length
img = Image.new('L', (400, 300), color=255)  # White background
draw = ImageDraw.Draw(img)

try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
except:
    font = ImageFont.load_default()

y_start = 30
y_spacing = 50

# Draw numbers and underscores
for i in range(1, 6):
    # Draw number
    draw.text((20, y_start + (i-1) * y_spacing), str(i), fill=0, font=font)
    
    # Draw underscore of increasing length
    underscore_start = 60
    underscore_length = 20 + i * 20
    underscore_y = y_start + (i-1) * y_spacing + 25
    underscore_thickness = 3
    
    draw.rectangle(
        [underscore_start, underscore_y, 
         underscore_start + underscore_length, underscore_y + underscore_thickness],
        fill=0
    )

# Save the image
img.save('test_underscores.png')
print("✓ Created test_underscores.png")

# Now analyze what would be detected
img_array = np.array(img)
_, binary = cv2.threshold(img_array, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

contours, hierarchy = cv2.findContours(binary, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)

print(f"\nFound {len(contours)} contours")
print("\nAnalyzing underscores:")

if hierarchy is not None:
    hierarchy = hierarchy[0]
    
    for i, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        x, y, w, h = cv2.boundingRect(contour)
        bbox_area = w * h
        
        # Check if this looks like an underscore (wide and thin)
        if w > h and w > 15 and h < 10:
            perimeter = cv2.arcLength(contour, True)
            thickness = min(w, h) if area == 0 else (area / perimeter if perimeter > 0 else 0)
            
            hull = cv2.convexHull(contour)
            hull_area = cv2.contourArea(hull)
            calc_area = area if area > 0 else bbox_area
            
            if hull_area > 0:
                solidity = calc_area / hull_area
            elif calc_area > 0:
                solidity = 1.0
            else:
                solidity = 0.0
            
            has_children = hierarchy[i][2] != -1
            is_child = hierarchy[i][3] != -1
            
            print(f"\nContour {i}: UNDERSCORE candidate")
            print(f"  Bounding box: ({x}, {y}) size {w}x{h}")
            print(f"  Area: {area} (bbox: {bbox_area})")
            print(f"  Solidity: {solidity:.3f}")
            print(f"  Thickness: {thickness:.3f}")
            print(f"  Has children: {has_children}, Is child: {is_child}")

print("\n" + "="*60)
print("Now running blueprint2gcode.py with --fill-solid-areas...")
print("="*60)
