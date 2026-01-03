#!/usr/bin/env python3
"""Debug underscore detection in detail"""

import numpy as np
from PIL import Image
import cv2

img = Image.open('test_underscores.png').convert('L')
img_array = np.array(img)
_, binary = cv2.threshold(img_array, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

contours, hierarchy = cv2.findContours(binary, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)

print(f"Found {len(contours)} contours")
print("\n" + "="*80)

min_solid_area = 0  # Use 0 to see all contours
min_thickness = 0.15

if hierarchy is not None:
    hierarchy = hierarchy[0]
    
    underscore_contours = []
    
    for i, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        x, y, w, h = cv2.boundingRect(contour)
        bbox_area = w * h
        
        # Focus on underscore candidates (wide and thin)
        if w > h and w > 15:
            effective_area = area if area > 0 else bbox_area
            
            hull = cv2.convexHull(contour)
            hull_area = cv2.contourArea(hull)
            calc_area = area if area > 0 else bbox_area
            
            if hull_area > 0:
                solidity = calc_area / hull_area
            elif calc_area > 0:
                solidity = 1.0
            else:
                solidity = 0.0
            
            perimeter = cv2.arcLength(contour, True)
            compactness = (perimeter * perimeter) / calc_area if calc_area > 0 else float('inf')
            
            if area > 0:
                thickness = area / perimeter if perimeter > 0 else 0
            else:
                thickness = min(w, h)
            
            has_children = hierarchy[i][2] != -1
            is_child = hierarchy[i][3] != -1
            
            print(f"\nContour {i}: {'UNDERSCORE' if h < 10 else 'OTHER'}")
            print(f"  Position: ({x}, {y})")
            print(f"  Size: {w}x{h} pixels")
            print(f"  Area: {area:.1f} (bbox: {bbox_area})")
            print(f"  Effective area: {effective_area:.1f}")
            print(f"  Solidity: {solidity:.3f}")
            print(f"  Compactness: {compactness:.1f}")
            print(f"  Thickness: {thickness:.3f} (min: {min_thickness})")
            print(f"  Has children: {has_children}, Is child: {is_child}")
            
            # Check detection logic
            print(f"  Checks:")
            print(f"    - effective_area >= {min_solid_area}: {effective_area >= min_solid_area}")
            print(f"    - solidity > 0.25: {solidity > 0.25}")
            print(f"    - thickness >= {min_thickness}: {thickness >= min_thickness}")
            print(f"    - not has_children and not is_child: {not has_children and not is_child}")
            print(f"    - compactness < 100: {compactness < 100}")
            
            # Determine if it would be detected as solid
            is_solid = False
            if effective_area >= min_solid_area and solidity > 0:
                if has_children and not is_child:
                    print(f"    → Has children - checking parent rules...")
                elif solidity > 0.25 and thickness >= min_thickness:
                    if not has_children and not is_child:
                        is_solid = True
                        print(f"    → WOULD BE DETECTED AS SOLID (no children/parent)")
                    elif not has_children and compactness < 100:
                        is_solid = True
                        print(f"    → WOULD BE DETECTED AS SOLID (compact, no children)")
            
            if not is_solid:
                print(f"    → NOT DETECTED AS SOLID")
                if thickness < min_thickness:
                    print(f"      Reason: thickness {thickness:.3f} < {min_thickness}")
                if solidity <= 0.25:
                    print(f"      Reason: solidity {solidity:.3f} <= 0.25")

print("\n" + "="*80)
