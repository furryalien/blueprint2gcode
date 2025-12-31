#!/usr/bin/env python3
"""
Test harness to process corner accuracy test images and generate visualizations.
"""

import os
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
from PIL import Image
import subprocess

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
            elif line.startswith('G1 X') or line.startswith('G0 X'):
                parts = line.split()
                x = y = None
                for part in parts:
                    if part.startswith('X'):
                        x = float(part[1:])
                    elif part.startswith('Y'):
                        y = float(part[1:])
                if x and y:
                    new_pos = (x, y)
                    if current_pos and pen_down and line.startswith('G1'):
                        lines.append((current_pos, new_pos))
                    current_pos = new_pos
    return lines

def process_test(test_file, output_dir, viz_dir):
    """Process a single test image."""
    input_path = os.path.join('test_images_corners', test_file)
    output_path = os.path.join(output_dir, test_file.replace('.png', '.gcode'))
    
    # Run blueprint2gcode
    cmd = [
        'python3', 'blueprint2gcode.py',
        input_path,
        output_path,
        '--fill-solid-areas'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            print(f"  ⚠ Error processing {test_file}")
            print(f"    {result.stderr[:200]}")
            return None
    except Exception as e:
        print(f"  ⚠ Exception processing {test_file}: {e}")
        return None
    
    # Parse G-code
    if not os.path.exists(output_path):
        print(f"  ⚠ Output file not created: {output_path}")
        return None
    
    lines = parse_gcode(output_path)
    return lines

def create_visualization(test_file, input_path, gcode_lines, viz_path):
    """Create side-by-side visualization of input and G-code output."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Load and display input image
    img = mpimg.imread(input_path)
    axes[0].imshow(img)
    axes[0].set_title(f'Input: {test_file}', fontsize=10, fontweight='bold')
    axes[0].axis('off')
    
    # Display G-code output
    axes[1].set_xlim(0, 260)
    axes[1].set_ylim(0, 208)
    axes[1].set_aspect('equal')
    axes[1].invert_yaxis()
    axes[1].set_facecolor('white')
    axes[1].grid(True, alpha=0.15, linewidth=0.3)
    axes[1].set_title(f'G-Code Output\n{len(gcode_lines)} lines', fontsize=10, fontweight='bold')
    axes[1].set_xlabel('X (mm)')
    axes[1].set_ylabel('Y (mm)')
    
    # Draw G-code lines
    for (x1, y1), (x2, y2) in gcode_lines:
        axes[1].plot([x1, x2], [y1, y2], 'b-', linewidth=0.1, alpha=0.8)
    
    plt.tight_layout()
    plt.savefig(viz_path, dpi=120, bbox_inches='tight')
    plt.close()

def main():
    """Run all corner accuracy tests."""
    output_dir = 'test_output_corners'
    viz_dir = 'test_visualizations_corners'
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(viz_dir, exist_ok=True)
    
    # Get all test images
    test_images = sorted([f for f in os.listdir('test_images_corners') if f.endswith('.png')])
    
    print("=" * 70)
    print("CORNER ACCURACY TEST HARNESS")
    print("=" * 70)
    print(f"Processing {len(test_images)} test images...")
    print()
    
    results = []
    
    for i, test_file in enumerate(test_images, 1):
        print(f"[{i}/{len(test_images)}] Processing {test_file}...", end=' ')
        sys.stdout.flush()
        
        # Process the test
        gcode_lines = process_test(test_file, output_dir, viz_dir)
        
        if gcode_lines is None:
            print("FAILED")
            results.append((test_file, 0, False))
            continue
        
        # Create visualization
        input_path = os.path.join('test_images_corners', test_file)
        viz_path = os.path.join(viz_dir, test_file.replace('.png', '_viz.png'))
        create_visualization(test_file, input_path, gcode_lines, viz_path)
        
        print(f"✓ ({len(gcode_lines)} lines)")
        results.append((test_file, len(gcode_lines), True))
    
    # Print summary
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"{'Test':<40} {'Lines':>10} {'Status':>8}")
    print("-" * 70)
    
    for test_file, line_count, success in results:
        status = "✓" if success else "FAIL"
        print(f"{test_file:<40} {line_count:>10} {status:>8}")
    
    successful = sum(1 for _, _, success in results if success)
    print("-" * 70)
    print(f"Successful: {successful}/{len(results)}")
    print()
    print(f"G-Code output: {output_dir}/")
    print(f"Visualizations: {viz_dir}/")
    
    # Create summary grid visualization
    create_summary_grid(results, viz_dir)

def create_summary_grid(results, viz_dir):
    """Create a grid showing all test results."""
    # Select key tests for summary
    key_tests = [
        'test1_square_300x300.png',
        'test2_square_100x100.png',
        'test4_rect_wide_600x100.png',
        'test5_rect_tall_100x500.png',
        'test6_grid_6squares_100x100.png',
        'test7_nested_squares.png',
        'test9_diamond.png',
        'test12_lshape.png',
        'test15_corner_squares.png',
    ]
    
    fig, axes = plt.subplots(3, 3, figsize=(18, 12))
    axes = axes.flatten()
    
    for i, test_file in enumerate(key_tests):
        if i >= len(axes):
            break
        
        viz_path = os.path.join(viz_dir, test_file.replace('.png', '_viz.png'))
        
        if os.path.exists(viz_path):
            try:
                img = mpimg.imread(viz_path)
                axes[i].imshow(img)
                axes[i].set_title(test_file.replace('.png', '').replace('_', ' '), fontsize=9)
            except:
                axes[i].text(0.5, 0.5, f'Error loading\n{test_file}', ha='center', va='center')
        else:
            axes[i].text(0.5, 0.5, f'Not found:\n{test_file}', ha='center', va='center')
        
        axes[i].axis('off')
    
    plt.suptitle('Corner Accuracy Test Results - Key Tests', fontsize=14, fontweight='bold')
    plt.tight_layout()
    summary_path = os.path.join(viz_dir, 'summary_grid.png')
    plt.savefig(summary_path, dpi=120, bbox_inches='tight')
    plt.close()
    
    print(f"\nSummary grid saved: {summary_path}")

if __name__ == '__main__':
    main()
