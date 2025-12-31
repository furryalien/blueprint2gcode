#!/usr/bin/env python3
"""Regenerate solid test visualizations with corrected Y-axis orientation"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import os
from pathlib import Path

def parse_gcode(filename):
    """Parse G-code and return line segments"""
    lines = []
    with open(filename) as f:
        current_pos = None
        pen_down = False
        for line in f:
            line = line.strip()
            if 'Z3' in line or 'Z 3' in line:
                pen_down = False
            elif 'Z0' in line or 'Z 0' in line:
                pen_down = True
            elif line.startswith('G1 X'):
                parts = line.split()
                x = y = None
                for part in parts:
                    if part.startswith('X'):
                        x = float(part[1:])
                    elif part.startswith('Y'):
                        y = float(part[1:])
                if x and y:
                    new_pos = (x, y)
                    if current_pos and pen_down:
                        lines.append((current_pos, new_pos))
                    current_pos = new_pos
            elif line.startswith('G0 X'):
                parts = line.split()
                x = y = None
                for part in parts:
                    if part.startswith('X'):
                        x = float(part[1:])
                    elif part.startswith('Y'):
                        y = float(part[1:])
                if x and y:
                    current_pos = (x, y)
    return lines

def main():
    # Mapping of test files to input images
    test_image_map = {
        'test1_default': 'test1_simple_shapes',
        'test2_default': 'test2_mixed_solid_outline',
        'test3_text_solids': 'test3_text_with_solids',
        'test4_floor_plan': 'test4_floor_plan_with_walls',
        'test5_mechanical': 'test5_mechanical_part',
        'test6_logo': 'test6_logo_style',
        'test7_circuit': 'test7_circuit_with_pads',
    }

    output_dir = Path('test_visualizations_solid')
    output_dir.mkdir(exist_ok=True)

    gcode_dir = Path('test_output_solid')
    if not gcode_dir.exists():
        print(f"Error: {gcode_dir} not found")
        return

    count = 0
    for test_base, img_base in test_image_map.items():
        gcode_file = gcode_dir / f'{test_base}.gcode'
        if not gcode_file.exists():
            continue
        
        # Find input image
        input_image = None
        for img_dir in ['test_images_solid', 'test_images']:
            for ext in ['.png', '.jpg']:
                img_path = f'{img_dir}/{img_base}{ext}'
                if os.path.exists(img_path):
                    input_image = img_path
                    break
            if input_image:
                break
        
        if not input_image:
            print(f"⚠ Skipping {test_base} - no input image found")
            continue
        
        # Parse G-code
        lines = parse_gcode(str(gcode_file))
        if not lines:
            print(f"⚠ Skipping {test_base} - no lines in G-code")
            continue
        
        # Load input image
        img = np.array(Image.open(input_image).convert('L'))
        
        # Create visualization
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # Original image
        axes[0].imshow(img, cmap='gray')
        axes[0].set_title(f'{test_base.replace("_", " ").title()}\nOriginal Image', 
                         fontsize=12, fontweight='bold')
        axes[0].axis('off')
        
        # G-code output
        axes[1].set_xlim(0, 280)
        axes[1].set_ylim(0, 210)  # Correct: Y=0 at bottom (matches G-code coordinate system)
        axes[1].set_aspect('equal')
        axes[1].set_facecolor('white')
        axes[1].grid(True, alpha=0.2, linewidth=0.5)
        axes[1].set_title(f'G-Code Output\n{len(lines)} lines', 
                         fontsize=12, fontweight='bold')
        axes[1].set_xlabel('X (mm)')
        axes[1].set_ylabel('Y (mm)')
        
        # Draw lines
        for (x1, y1), (x2, y2) in lines:
            axes[1].plot([x1, x2], [y1, y2], 'b-', linewidth=0.08, alpha=0.8)
        
        plt.tight_layout()
        output_path = output_dir / f'{test_base}.png'
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        count += 1
        print(f"✓ Generated: {output_path}")

    print(f"\n✓ Generated {count} visualizations in {output_dir}/")

if __name__ == '__main__':
    main()
