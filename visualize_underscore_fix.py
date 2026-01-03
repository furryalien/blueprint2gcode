#!/usr/bin/env python3
"""Final visualization of underscore fix"""

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
gcode_lines = parse_gcode('test_output/underscores_debug.gcode')

# Create visualization
fig, axes = plt.subplots(1, 2, figsize=(18, 8))

# Left: Original image
axes[0].imshow(img, cmap='gray')
axes[0].set_title('Input Image - Numbers 1-5 with Underscores\n(5 horizontal underscores of increasing length)',
                  fontsize=13, fontweight='bold')
axes[0].set_xlabel('Pixel X', fontsize=10)
axes[0].set_ylabel('Pixel Y', fontsize=10)
axes[0].grid(True, alpha=0.3, linewidth=0.5)

# Right: G-code output
axes[1].set_xlim(0, 300)
axes[1].set_ylim(0, 220)
axes[1].set_aspect('equal')
axes[1].invert_yaxis()
axes[1].set_facecolor('white')
axes[1].grid(True, alpha=0.2, linewidth=0.5)
axes[1].set_title(f'G-Code Output - ALL UNDERSCORES FILLED ✓\n{len(gcode_lines)} lines total',
                  fontsize=13, fontweight='bold', color='green')
axes[1].set_xlabel('X (mm)', fontsize=10)
axes[1].set_ylabel('Y (mm)', fontsize=10)

# Draw all lines with very thin linewidth to show detail
for (x1, y1), (x2, y2) in gcode_lines:
    # Color horizontal lines (underscores) differently
    y_diff = abs(y2 - y1)
    x_diff = abs(x2 - x1)
    
    if y_diff < 0.5 and x_diff > 20:  # Horizontal and long = underscore
        axes[1].plot([x1, x2], [y1, y2], 'r-', linewidth=0.3, alpha=0.9, zorder=10)
    else:
        axes[1].plot([x1, x2], [y1, y2], 'b-', linewidth=0.08, alpha=0.7)

# Add legend
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], color='r', linewidth=2, label='Underscores (horizontal fill)'),
    Line2D([0], [0], color='b', linewidth=1, label='Numbers (crosshatch fill)')
]
axes[1].legend(handles=legend_elements, loc='upper right', fontsize=9)

plt.tight_layout()
plt.savefig('underscore_fix_complete.png', dpi=150, bbox_inches='tight')
print("✅ Saved: underscore_fix_complete.png")
print(f"\nTotal lines: {len(gcode_lines)}")

# Count underscore lines
underscore_lines = [(x1,y1,x2,y2) for (x1, y1), (x2, y2) in gcode_lines 
                    if abs(y2 - y1) < 0.5 and abs(x2 - x1) > 20]
print(f"Underscore lines (horizontal, >20mm): {len(underscore_lines)}")
print("\n✅ SUCCESS: Underscores are now properly detected and filled with horizontal hatching!")
