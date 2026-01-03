#!/usr/bin/env python3
"""Debug hatching generation for underscores specifically"""

import numpy as np
from PIL import Image
import cv2

img = Image.open('test_underscores.png').convert('L')
img_array = np.array(img)
_, binary = cv2.threshold(img_array, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

contours, hierarchy = cv2.findContours(binary, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)

print("Testing hatching generation for underscore contours:")

hatch_angle = 45  # Default from blueprint2gcode
hatch_spacing_px = 2.16  # From the actual run

# Focus on the first underscore (contour 0, position 60,255, size 121x4)
for i, contour in enumerate(contours):
    x, y, w, h = cv2.boundingRect(contour)
    
    # Check if this is an underscore
    if w > h and w > 15 and h < 10:
        print(f"\n{'='*70}")
        print(f"Contour {i}: Underscore at ({x}, {y}), size {w}x{h}")
        
        # Check special case
        if h == 1:
            print("  → Triggers special case (h == 1) - horizontal line only")
        else:
            print(f"  → Normal hatching (h = {h} > 1)")
            
            # Create mask
            mask = np.zeros(binary.shape, dtype=np.uint8)
            cv2.drawContours(mask, [contour], -1, 255, -1)
            
            # Count mask pixels
            mask_pixels = np.count_nonzero(mask)
            print(f"  → Mask has {mask_pixels} pixels")
            
            # Calculate hatching parameters
            angle_rad = np.deg2rad(hatch_angle)
            perp_angle = angle_rad + np.pi/2
            dx_perp = np.cos(perp_angle)
            dy_perp = np.sin(perp_angle)
            dx_line = np.cos(angle_rad)
            dy_line = np.sin(angle_rad)
            
            diagonal = int(np.sqrt(w**2 + h**2)) + 20
            cx, cy = x + w/2, y + h/2
            
            # Calculate perpendicular extent
            corners = [
                (x, y), (x + w, y), (x, y + h), (x + w, y + h)
            ]
            perp_offsets = []
            for corner_x, corner_y in corners:
                offset = (corner_x - cx) * dx_perp + (corner_y - cy) * dy_perp
                perp_offsets.append(offset)
            
            min_offset = min(perp_offsets) - hatch_spacing_px * 2
            max_offset = max(perp_offsets) + hatch_spacing_px * 2
            
            num_lines = int((max_offset - min_offset) / hatch_spacing_px) + 3
            
            print(f"  → Perpendicular range: {min_offset:.2f} to {max_offset:.2f}")
            print(f"  → Number of hatch lines to generate: {num_lines}")
            print(f"  → Hatch spacing: {hatch_spacing_px:.2f}px")
            print(f"  → Hatch angle: {hatch_angle}°")
            
            # Try generating a few lines
            hatch_lines = []
            img_shape = binary.shape
            
            for i_line in range(min(num_lines, 5)):  # Just first 5 lines for testing
                offset = min_offset + i_line * hatch_spacing_px
                
                # Line endpoints
                px = cx + offset * dx_perp - diagonal * dx_line
                py = cy + offset * dy_perp - diagonal * dy_line
                qx = cx + offset * dx_perp + diagonal * dx_line
                qy = cy + offset * dy_perp + diagonal * dy_line
                
                p1 = (int(round(px)), int(round(py)))
                p2 = (int(round(qx)), int(round(qy)))
                
                # Clip to bounds
                p1 = (max(0, min(img_shape[1]-1, p1[0])), max(0, min(img_shape[0]-1, p1[1])))
                p2 = (max(0, min(img_shape[1]-1, p2[0])), max(0, min(img_shape[0]-1, p2[1])))
                
                # Check if line intersects mask
                line_start = np.array([float(p1[0]), float(p1[1])])
                line_end = np.array([float(p2[0]), float(p2[1])])
                line_vec = line_end - line_start
                line_length = np.linalg.norm(line_vec)
                
                if line_length < 1:
                    continue
                
                # Sample along line
                num_samples = int(line_length * 10) + 20
                hits = 0
                
                for sample_idx in range(num_samples):
                    t = sample_idx / (num_samples - 1)
                    point = line_start + t * line_vec
                    px_int, py_int = int(round(point[0])), int(round(point[1]))
                    
                    if 0 <= px_int < img_shape[1] and 0 <= py_int < img_shape[0]:
                        if mask[py_int, px_int] > 0:
                            hits += 1
                
                print(f"    Line {i_line}: offset={offset:.2f}, {hits}/{num_samples} samples hit mask")
                
                if hits > 0:
                    hatch_lines.append(1)
            
            print(f"  → Generated {len(hatch_lines)} hatch lines (from first 5 attempts)")

print("\n" + "="*70)
