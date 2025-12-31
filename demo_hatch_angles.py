#!/usr/bin/env python3
"""
Create a comparison showing different hatch angles to demonstrate correct parallel hatching.
"""

import matplotlib.pyplot as plt
from PIL import Image
import re
import subprocess
import sys

def parse_gcode(gcode_file):
    """Parse G-code to extract paths."""
    paths = []
    current_path = []
    pen_down = False
    current_x, current_y = 0, 0
    
    with open(gcode_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith(';') or not line:
                continue
            
            x_match = re.search(r'X([-\d.]+)', line)
            y_match = re.search(r'Y([-\d.]+)', line)
            
            if x_match and y_match:
                current_x = float(x_match.group(1))
                current_y = float(y_match.group(1))
                if pen_down:
                    current_path.append((current_x, current_y))
            
            if 'Z' in line:
                z_match = re.search(r'Z([-\d.]+)', line)
                if z_match:
                    z_val = float(z_match.group(1))
                    if z_val == 0.0:
                        pen_down = True
                        current_path = [(current_x, current_y)]
                    else:
                        pen_down = False
                        if len(current_path) > 1:
                            paths.append(current_path)
                        current_path = []
    
    if len(current_path) > 1:
        paths.append(current_path)
    return paths

def generate_and_visualize(angle, output_base, ax):
    """Generate G-code for given angle and visualize."""
    gcode_file = f"{output_base}_angle{angle}.gcode"
    
    # Generate G-code
    cmd = [
        sys.executable, 'blueprint2gcode.py',
        'test_images_solid/test1_simple_shapes.png',
        gcode_file,
        '--fill-solid-areas',
        '--hatch-spacing', '2.5',
        '--hatch-angle', str(angle)
    ]
    
    print(f"Generating {angle}° hatching...")
    subprocess.run(cmd, capture_output=True, check=True)
    
    # Parse and plot
    paths = parse_gcode(gcode_file)
    
    ax.set_aspect('equal')
    for path in paths:
        if len(path) > 1:
            xs, ys = zip(*path)
            ax.plot(xs, ys, 'b-', linewidth=0.7, alpha=0.8)
    
    ax.set_xlim(0, 300)
    ax.set_ylim(0, 220)
    ax.set_title(f'{angle}° Hatch Angle\n{len(paths)} lines', fontsize=12, fontweight='bold')
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.grid(True, alpha=0.3)

# Create 2x3 grid
fig, axes = plt.subplots(2, 3, figsize=(18, 12))
fig.suptitle('Fixed Parallel Hatching - Different Angles', fontsize=16, fontweight='bold')

# Original image
img = Image.open('test_images_solid/test1_simple_shapes.png')
axes[0, 0].imshow(img, cmap='gray')
axes[0, 0].set_title('Original Image', fontsize=12, fontweight='bold')
axes[0, 0].axis('off')

# Generate different angles
angles = [0, 45, 90, 135, 30]
output_axes = [axes[0, 1], axes[0, 2], axes[1, 0], axes[1, 1], axes[1, 2]]

for angle, ax in zip(angles, output_axes):
    generate_and_visualize(angle, 'test_output/hatch_demo', ax)

plt.tight_layout()
plt.savefig('test_output/hatch_angles_comparison.png', dpi=150, bbox_inches='tight')
print('\n✓ Comparison saved to: test_output/hatch_angles_comparison.png')
print('\nThis demonstrates proper parallel hatching at various angles.')
