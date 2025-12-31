#!/usr/bin/env python3
"""
Analyze corner accuracy by zooming into corners of test shapes.
"""

import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def parse_gcode(filename):
    """Parse G-code file and extract drawing lines."""
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

# Create corner analysis for test1 (300x300 square)
print("Analyzing corner accuracy...")

fig, axes = plt.subplots(2, 2, figsize=(16, 16))

tests = [
    ('test1_square_300x300.png', 'test1_square_300x300.gcode', 'Top-left corner'),
    ('test1_square_300x300.png', 'test1_square_300x300.gcode', 'Top-right corner'),
    ('test1_square_300x300.png', 'test1_square_300x300.gcode', 'Bottom-left corner'),
    ('test1_square_300x300.png', 'test1_square_300x300.gcode', 'Bottom-right corner'),
]

# Parse G-code
gcode_lines = parse_gcode(f'test_output_corners/test1_square_300x300.gcode')

# Define corner regions (in mm coordinates - approximate)
# The square is centered on a 208x277mm page with margins
# Square is ~100mm x 100mm (300px * 0.347 scale)
corners = [
    (85, 160, 105, 180, 'Top-left'),      # x1, y1, x2, y2
    (170, 160, 190, 180, 'Top-right'),
    (85, 60, 105, 80, 'Bottom-left'),
    (170, 60, 190, 80, 'Bottom-right'),
]

for idx, (x1, y1, x2, y2, title) in enumerate(corners):
    ax = axes[idx // 2, idx % 2]
    
    ax.set_xlim(x1, x2)
    ax.set_ylim(y1, y2)
    ax.set_aspect('equal')
    ax.invert_yaxis()
    ax.set_facecolor('white')
    ax.grid(True, alpha=0.3, linewidth=0.5)
    ax.set_title(f'{title} Corner (20mm × 20mm zoom)', fontsize=12, fontweight='bold')
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    
    # Draw G-code lines in this region
    lines_in_region = 0
    for (sx, sy), (ex, ey) in gcode_lines:
        # Check if line is in or near this region
        if (x1 - 5 <= sx <= x2 + 5 and y1 - 5 <= sy <= y2 + 5) or \
           (x1 - 5 <= ex <= x2 + 5 and y1 - 5 <= ey <= y2 + 5):
            ax.plot([sx, ex], [sy, ey], 'b-', linewidth=0.5, alpha=0.8)
            lines_in_region += 1
    
    ax.text(0.02, 0.98, f'{lines_in_region} lines', 
            transform=ax.transAxes, fontsize=9, 
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.suptitle('Corner Accuracy Analysis - 300x300 Square\n(Zoomed 20mm regions at each corner)', 
             fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('corner_analysis_zoom.png', dpi=150, bbox_inches='tight')
print("✓ Saved: corner_analysis_zoom.png")

# Now create a comparison showing hatching pattern density
print("\nAnalyzing hatching density...")

fig, axes = plt.subplots(1, 3, figsize=(18, 6))

test_cases = [
    ('test2_square_100x100.gcode', '100x100 square'),
    ('test1_square_300x300.gcode', '300x300 square'),
    ('test4_rect_wide_600x100.gcode', '600x100 rectangle'),
]

for idx, (gcode_file, title) in enumerate(test_cases):
    ax = axes[idx]
    
    try:
        lines = parse_gcode(f'test_output_corners/{gcode_file}')
        
        ax.set_xlim(0, 260)
        ax.set_ylim(0, 208)
        ax.set_aspect('equal')
        ax.invert_yaxis()
        ax.set_facecolor('white')
        ax.grid(True, alpha=0.15, linewidth=0.3)
        ax.set_title(f'{title}\n{len(lines)} lines', fontsize=11, fontweight='bold')
        ax.set_xlabel('X (mm)')
        ax.set_ylabel('Y (mm)')
        
        for (sx, sy), (ex, ey) in lines:
            ax.plot([sx, ex], [sy, ey], 'b-', linewidth=0.08, alpha=0.85)
    except Exception as e:
        ax.text(0.5, 0.5, f'Error: {e}', ha='center', va='center')

plt.suptitle('Hatching Density Comparison (1mm spacing)', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('hatching_density_comparison.png', dpi=140, bbox_inches='tight')
print("✓ Saved: hatching_density_comparison.png")

print("\n" + "="*70)
print("CORNER ANALYSIS COMPLETE")
print("="*70)
print("\nGenerated visualizations:")
print("  1. corner_analysis_zoom.png - Zoomed views of all 4 corners")
print("  2. hatching_density_comparison.png - Density across different sizes")
print("\nCheck these images to verify:")
print("  ✓ Corners are fully filled (no gaps)")
print("  ✓ Hatching extends to edges")
print("  ✓ No overflow beyond boundaries")
