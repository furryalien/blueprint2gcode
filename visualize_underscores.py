#!/usr/bin/env python3
"""Visualize the underscore test results"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from PIL import Image

def parse_gcode(filename):
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

# Load input image
img = np.array(Image.open('test_underscores.png').convert('L'))

# Parse G-code
gcode_lines = parse_gcode('test_output/underscores_test.gcode')

# Create visualization
fig, axes = plt.subplots(1, 2, figsize=(18, 8))

# Left: Original image
axes[0].imshow(img, cmap='gray')
axes[0].set_title('Input Image - Numbers with Underscores\n(5 underscores of increasing length)',
                  fontsize=13, fontweight='bold')
axes[0].set_xlabel('Pixel X', fontsize=10)
axes[0].set_ylabel('Pixel Y', fontsize=10)
axes[0].grid(True, alpha=0.3, linewidth=0.5)

# Right: G-code output
axes[1].set_xlim(0, 280)
axes[1].set_ylim(0, 210)
axes[1].set_aspect('equal')
axes[1].invert_yaxis()
axes[1].set_facecolor('white')
axes[1].grid(True, alpha=0.2, linewidth=0.5)
axes[1].set_title(f'G-Code Output\n{len(gcode_lines)} lines total',
                  fontsize=13, fontweight='bold')
axes[1].set_xlabel('X (mm)', fontsize=10)
axes[1].set_ylabel('Y (mm)', fontsize=10)

# Draw all lines
for (x1, y1), (x2, y2) in gcode_lines:
    axes[1].plot([x1, x2], [y1, y2], 'b-', linewidth=0.1, alpha=0.8)

# Add annotations to show where underscores should be
underscore_positions = [
    (60, 55, 41, 4, '1'),
    (60, 105, 61, 4, '2'),
    (60, 155, 81, 4, '3'),
    (60, 205, 101, 4, '4'),
    (60, 255, 121, 4, '5'),
]

for px, py, pw, ph, label in underscore_positions:
    # Convert pixel coordinates to mm
    scale = 0.6933
    x_mm = px * scale
    y_mm = py * scale
    w_mm = pw * scale
    h_mm = ph * scale
    
    # Draw bounding box
    rect = patches.Rectangle((x_mm, y_mm), w_mm, h_mm, linewidth=1.5,
                              edgecolor='red', facecolor='none', linestyle='--', alpha=0.6)
    axes[1].add_patch(rect)
    axes[1].text(x_mm + w_mm/2, y_mm - 3, f'_{label}', ha='center', fontsize=8, color='red', fontweight='bold')

plt.tight_layout()
plt.savefig('underscore_test_result.png', dpi=150, bbox_inches='tight')
print("✅ Saved: underscore_test_result.png")
print(f"\nTotal lines: {len(gcode_lines)}")
print("Expected: Numbers + 5 hatched underscores")
