#!/usr/bin/env python3
"""
Visualize G-code output to compare solid area filling results.
"""

import matplotlib.pyplot as plt
import re
from pathlib import Path

def parse_gcode(gcode_path):
    """Parse G-code file and extract line segments."""
    segments = []
    current_segment = []
    pen_down = False
    
    with open(gcode_path, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Check for pen up/down
            if 'Z' in line and 'G0' in line:
                z_match = re.search(r'Z([\d.-]+)', line)
                if z_match:
                    z = float(z_match.group(1))
                    if z > 1:  # Pen up
                        if current_segment and pen_down:
                            segments.append(current_segment)
                            current_segment = []
                        pen_down = False
                    else:  # Pen down
                        pen_down = True
            
            # Extract X, Y coordinates
            if ('G0' in line or 'G1' in line) and 'X' in line and 'Y' in line:
                x_match = re.search(r'X([\d.-]+)', line)
                y_match = re.search(r'Y([\d.-]+)', line)
                
                if x_match and y_match:
                    x = float(x_match.group(1))
                    y = float(y_match.group(1))
                    
                    if pen_down:
                        current_segment.append((x, y))
    
    if current_segment:
        segments.append(current_segment)
    
    return segments

def visualize_comparison(gcode_with_fill, gcode_without_fill, output_path):
    """Create side-by-side comparison visualization."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Parse both G-code files
    segments_with = parse_gcode(gcode_with_fill)
    segments_without = parse_gcode(gcode_without_fill)
    
    # Plot without filling
    ax1.set_title(f'Without Solid Fill\n{len(segments_without)} line segments', fontsize=14, fontweight='bold')
    for segment in segments_without:
        if len(segment) >= 2:
            xs, ys = zip(*segment)
            ax1.plot(xs, ys, 'b-', linewidth=0.5)
    ax1.set_aspect('equal')
    ax1.invert_yaxis()  # Invert Y-axis to match image orientation
    ax1.grid(True, alpha=0.3)
    ax1.set_xlabel('X (mm)')
    ax1.set_ylabel('Y (mm)')
    
    # Plot with filling
    ax2.set_title(f'With Solid Fill (--fill-solid-areas)\n{len(segments_with)} line segments', fontsize=14, fontweight='bold')
    for segment in segments_with:
        if len(segment) >= 2:
            xs, ys = zip(*segment)
            ax2.plot(xs, ys, 'r-', linewidth=0.5)
    ax2.set_aspect('equal')
    ax2.invert_yaxis()  # Invert Y-axis to match image orientation
    ax2.grid(True, alpha=0.3)
    ax2.set_xlabel('X (mm)')
    ax2.set_ylabel('Y (mm)')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Visualization saved to: {output_path}")
    
    # Print statistics
    print("\n" + "=" * 60)
    print("COMPARISON STATISTICS")
    print("=" * 60)
    print(f"Without fill: {len(segments_without)} line segments")
    print(f"With fill:    {len(segments_with)} line segments")
    print(f"Difference:   {len(segments_with) - len(segments_without)} additional segments")
    print("=" * 60)

def main():
    """Generate comparison visualizations."""
    output_dir = Path('../visualizations/test_visualizations_solid')
    output_dir.mkdir(exist_ok=True)
    
    # Compare test1
    print("\nGenerating comparison for Test 1: Simple Shapes..")
    visualize_comparison(
        '../test_data/test_output_solid/test1_default.gcode',
        '../test_data/test_output_solid/test1_no_fill.gcode',
        output_dir / 'comparison_test1.png'
    )
    
    print("\nComparison visualization created!")
    print(f"View it at: {output_dir}/comparison_test1.png")

if __name__ == '__main__':
    main()
