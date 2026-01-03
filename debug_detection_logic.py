#!/usr/bin/env python3
"""Run blueprint2gcode with extra debugging"""

import sys
import numpy as np
from PIL import Image
import cv2

# Inline the key detection logic with debugging
img = Image.open('test_underscores.png').convert('L')
img_array = np.array(img)
_, binary = cv2.threshold(img_array, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

contours, hierarchy = cv2.findContours(binary, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)

min_solid_area = 0  # Match the default
min_thickness = 0.15

print(f"Found {len(contours)} contours")
print("\nDETECTION LOGIC (matching blueprint2gcode.py):\n")

if hierarchy is not None:
    hierarchy = hierarchy[0]
    
    solid_areas = []
    parent_indices = set()
    rejected_outline_parents = set()
    
    for i, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        x, y, w, h = cv2.boundingRect(contour)
        bbox_area = w * h
        
        effective_area = area if area > 0 else bbox_area
        
        # Skip small areas
        if effective_area < min_solid_area:
            continue
        
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        calc_area = area if area > 0 else bbox_area
        
        if hull_area > 0:
            solidity = calc_area / hull_area
        elif calc_area > 0:
            solidity = 1.0
        else:
            solidity = 0.0
        
        if solidity > 0:
            has_children = hierarchy[i][2] != -1
            is_child = hierarchy[i][3] != -1
            
            perimeter = cv2.arcLength(contour, True)
            compactness = (perimeter * perimeter) / calc_area if calc_area > 0 else float('inf')
            
            if area > 0:
                thickness = area / perimeter if perimeter > 0 else 0
            else:
                thickness = min(w, h)
            
            is_solid = False
            reason = ""
            
            # Check if it's an underscore candidate
            is_underscore = (w > h and w > 15 and h < 10)
            
            if is_underscore:
                print(f"\n{'='*70}")
                print(f"Contour {i}: UNDERSCORE CANDIDATE")
                print(f"  Position: ({x}, {y}), Size: {w}x{h}")
                print(f"  Area: {area:.1f}, Effective: {effective_area:.1f}")
                print(f"  Solidity: {solidity:.3f}, Thickness: {thickness:.3f}")
                print(f"  Compactness: {compactness:.1f}")
                print(f"  has_children: {has_children}, is_child: {is_child}")
            
            # MATCHING THE ACTUAL CODE LOGIC
            if has_children and not is_child:
                if is_underscore:
                    print(f"  Branch: has_children and not is_child")
                
                children_area = 0
                child_idx = hierarchy[i][2]
                while child_idx != -1:
                    children_area += cv2.contourArea(contours[child_idx])
                    child_idx = hierarchy[child_idx][0]
                
                fill_ratio = (calc_area - children_area) / calc_area if calc_area > 0 else 0
                
                if solidity > 0.4 and compactness < 200 and fill_ratio > 0.15 and thickness >= min_thickness:
                    is_solid = True
                    reason = "parent with holes"
                    parent_indices.add(i)
                else:
                    rejected_outline_parents.add(i)
                    reason = f"rejected parent (sol={solidity:.2f}, comp={compactness:.1f}, fill={fill_ratio:.2f}, thick={thickness:.3f})"
            
            elif solidity > 0.25 and thickness >= min_thickness:
                if is_underscore:
                    print(f"  Branch: solidity > 0.25 and thickness >= min_thickness")
                    print(f"    Checking sub-conditions...")
                
                if not has_children and not is_child:
                    is_solid = True
                    reason = "truly solid (no children/parent)"
                    if is_underscore:
                        print(f"    ✓ MATCHED: not has_children and not is_child")
                
                elif is_child:
                    if is_underscore:
                        print(f"    Checking: is_child")
                    parent_idx = hierarchy[i][3]
                    if parent_idx in rejected_outline_parents:
                        reason = "child of rejected parent"
                    elif parent_idx not in parent_indices:
                        if solidity > 0.95 and compactness < 50:
                            is_solid = True
                            reason = "standalone filled child"
                        else:
                            reason = f"child but not solid enough (sol={solidity:.2f}, comp={compactness:.1f})"
                    else:
                        reason = "child of solid parent (hole)"
                
                elif not has_children and compactness < 100:
                    is_solid = True
                    reason = "single contour, moderate compactness"
                    if is_underscore:
                        print(f"    ✓ MATCHED: not has_children and compactness < 100")
                
                elif not has_children:
                    reason = f"not has_children but compactness too high ({compactness:.1f})"
                    if is_underscore:
                        print(f"    ✗ FAILED: compactness {compactness:.1f} >= 100")
            
            else:
                if is_underscore:
                    print(f"  Branch: else (failed initial check)")
                    if solidity <= 0.25:
                        print(f"    Reason: solidity {solidity:.3f} <= 0.25")
                    if thickness < min_thickness:
                        print(f"    Reason: thickness {thickness:.3f} < {min_thickness}")
                reason = f"failed initial check (sol={solidity:.2f}, thick={thickness:.3f})"
            
            if is_underscore:
                print(f"  Result: {'✅ SOLID' if is_solid else '❌ NOT SOLID'}")
                print(f"  Reason: {reason}")
            
            if is_solid:
                solid_areas.append((i, contour))

print(f"\n{'='*70}")
print(f"Total solid areas detected: {len(solid_areas)}")
print(f"{'='*70}\n")
