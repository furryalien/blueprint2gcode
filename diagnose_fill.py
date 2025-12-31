#!/usr/bin/env python3
"""
Diagnostic tool to understand solid fill detection and generation.
Helps identify why G-code might not match expectations.
"""

import argparse
import numpy as np
from PIL import Image, ImageDraw
import cv2
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def analyze_image(image_path):
    """Analyze an image and show what will be detected as solid areas."""
    print(f"\n{'='*80}")
    print(f"ANALYZING: {image_path}")
    print(f"{'='*80}")
    
    # Load image
    img = Image.open(image_path)
    img_gray = img.convert('L')
    arr = np.array(img_gray, dtype=np.uint8)
    
    print(f"\n1. INPUT IMAGE:")
    print(f"   Size: {arr.shape[1]}x{arr.shape[0]} pixels")
    
    # Count black/white
    black_pixels = np.sum(arr < 128)
    white_pixels = np.sum(arr >= 128)
    print(f"   Black pixels: {black_pixels:,} ({100*black_pixels/arr.size:.1f}%)")
    print(f"   White pixels: {white_pixels:,} ({100*white_pixels/arr.size:.1f}%)")
    
    # Apply threshold like blueprint2gcode does
    _, binary = cv2.threshold(arr, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    print(f"\n2. AFTER THRESH_BINARY_INV:")
    print(f"   White (will be processed): {np.sum(binary == 255):,} pixels")
    print(f"   Black (will be ignored): {np.sum(binary == 0):,} pixels")
    print(f"   → BLACK areas from original become WHITE and will be filled")
    
    # Find contours
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    
    print(f"\n3. CONTOURS DETECTED: {len(contours)}")
    
    # Analyze hierarchy
    solid_contours = []
    hole_contours = []
    
    if hierarchy is not None:
        h = hierarchy[0]
        for i, cnt in enumerate(contours):
            area = cv2.contourArea(cnt)
            bounds = cv2.boundingRect(cnt)
            next_sib, prev_sib, first_child, parent = h[i]
            
            is_parent = parent == -1
            has_children = first_child != -1
            
            # Determine if this is solid or a hole
            if is_parent and area > 100:  # Parent contours
                solid_contours.append((i, cnt, area, bounds))
                print(f"   [{i}] PARENT: area={area:,.0f}, pos=({bounds[0]},{bounds[1]}), "
                      f"size={bounds[2]}x{bounds[3]}, children={first_child}")
            elif not is_parent and area > 50:  # Child contours (holes)
                hole_contours.append((i, cnt, area, bounds))
                print(f"   [{i}] HOLE: area={area:,.0f}, pos=({bounds[0]},{bounds[1]}), "
                      f"size={bounds[2]}x{bounds[3]}, parent={parent}")
    
    print(f"\n4. CLASSIFICATION:")
    print(f"   Solid areas (parents): {len(solid_contours)}")
    print(f"   Holes (children): {len(hole_contours)}")
    
    # Create visualization
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    
    # Original
    axes[0, 0].imshow(arr, cmap='gray')
    axes[0, 0].set_title('Original Image\n(Gray values)', fontsize=12, fontweight='bold')
    axes[0, 0].axis('off')
    
    # Binary (inverted)
    axes[0, 1].imshow(binary, cmap='gray')
    axes[0, 1].set_title('After THRESH_BINARY_INV\n(White = will be filled)', fontsize=12, fontweight='bold')
    axes[0, 1].axis('off')
    
    # Contours overlay
    overlay = np.array(img.convert('RGB'))
    if solid_contours:
        for i, cnt, area, bounds in solid_contours:
            cv2.drawContours(overlay, [cnt], -1, (255, 0, 0), 3)  # Red for solid areas
    if hole_contours:
        for i, cnt, area, bounds in hole_contours:
            cv2.drawContours(overlay, [cnt], -1, (0, 0, 255), 3)  # Blue for holes
    axes[0, 2].imshow(overlay)
    axes[0, 2].set_title('Detected Contours\n(Red=solid, Blue=holes)', fontsize=12, fontweight='bold')
    axes[0, 2].axis('off')
    
    # Mask for solid areas (what will actually be filled)
    fill_mask = np.zeros(arr.shape, dtype=np.uint8)
    for i, cnt, area, bounds in solid_contours:
        cv2.drawContours(fill_mask, [cnt], -1, 255, -1)
        # Subtract holes
        if hierarchy is not None:
            h = hierarchy[0]
            child_idx = h[i][2]  # First child
            while child_idx != -1:
                cv2.drawContours(fill_mask, [contours[child_idx]], -1, 0, -1)
                child_idx = h[child_idx][0]  # Next sibling
    
    axes[1, 0].imshow(fill_mask, cmap='gray')
    axes[1, 0].set_title('What Will Be Filled\n(excluding holes)', fontsize=12, fontweight='bold')
    axes[1, 0].axis('off')
    
    # Expected output (original black areas)
    expected = 255 - arr  # Invert so black becomes white
    axes[1, 1].imshow(expected, cmap='gray')
    axes[1, 1].set_title('Expected (Original Black→White)\nShould match "What Will Be Filled"', 
                         fontsize=12, fontweight='bold')
    axes[1, 1].axis('off')
    
    # Comparison (difference)
    diff = np.abs(fill_mask.astype(int) - expected.astype(int))
    axes[1, 2].imshow(diff, cmap='hot')
    axes[1, 2].set_title(f'Difference\n{np.sum(diff > 0):,} pixels different', 
                         fontsize=12, fontweight='bold')
    axes[1, 2].axis('off')
    
    plt.tight_layout()
    output_name = image_path.replace('.png', '_diagnosis.png').replace('test_images_solid/', '')
    plt.savefig(output_name, dpi=120, bbox_inches='tight')
    print(f"\n✓ Saved: {output_name}")
    
    # Calculate match percentage
    match_percent = 100 * (1 - np.sum(diff > 0) / arr.size)
    print(f"\n5. ACCURACY:")
    print(f"   Match: {match_percent:.2f}%")
    if match_percent < 95:
        print(f"   ⚠️  WARNING: Poor match! Check contour detection logic.")
    else:
        print(f"   ✓ Good match - detection is working correctly")
    
    return {
        'solid_areas': len(solid_contours),
        'holes': len(hole_contours),
        'match_percent': match_percent
    }


def main():
    parser = argparse.ArgumentParser(description='Diagnose solid fill detection')
    parser.add_argument('image', help='Input image to analyze')
    args = parser.parse_args()
    
    analyze_image(args.image)


if __name__ == '__main__':
    main()
